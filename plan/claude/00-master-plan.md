# Master Plan: Data Migration & Schema Transformation Engine (`sync-mail`)

> **Sumber kebenaran:** `plan/00-prd.md`. Dokumen ini adalah breakdown arsitektural & rencana kerja berfase. **Tidak memuat source code** — hanya logika, alur data, dan tanggung jawab tiap file.

---

## 0. Keputusan Desain Awal (Hasil Klarifikasi)

Sebelum fase dimulai, keputusan berikut sudah dikunci dan menjadi landasan seluruh rencana:

| Aspek | Keputusan | Implikasi Arsitektural |
|---|---|---|
| **Cakupan introspection** | Single-table per run dulu; multi-table di fase lanjutan (opsional) | Phase 3 fokus satu pasangan tabel; Phase 9 (opsional) menambahkan orchestrator multi-mapping |
| **State checkpoint** | File `state.json` lokal (per migration job) | Tidak butuh migrasi schema di target untuk state; cukup atomic write (write-temp + rename) |
| **Antarmuka eksekusi** | **TUI berbasis Textual** | Phase 8 dedicated untuk TUI; engine inti harus headless & event-driven supaya dapat di-drive oleh TUI |
| **Strategi batch gagal** | Abort job + simpan checkpoint terakhir yang sukses | Tidak ada row-by-row fallback otomatis. Operator melakukan inspeksi manual lalu resume |
| **Library TUI** | Textual | Menambah dependency `textual`; engine harus expose progress via callback/queue, bukan print langsung |

---

## 1. Pertanyaan Optimasi (Open Questions untuk Iterasi Berikutnya)

Pertanyaan-pertanyaan berikut **tidak memblokir mulai pengerjaan**, tapi harus dijawab sebelum fase yang relevan dimulai supaya tidak halu:

1. **Identifikasi Primary Key untuk Keyset Pagination.** Apakah seluruh source table dijamin punya PK numerik monotonic, atau ada tabel dengan PK komposit / UUID? Ini menentukan apakah keyset extractor cukup single-column atau perlu tuple comparison (`WHERE (a, b) > (:last_a, :last_b)`).
2. **Definisi "selesai" untuk one-time batch.** Apakah migrasi dianggap selesai saat extractor mengembalikan empty result, atau perlu cross-check `COUNT(*)` antara source vs target sebagai post-validation? Mempengaruhi Phase 7 (verification step).
3. **Toleransi terhadap perubahan data di source selama migrasi.** Apakah source dijamin frozen (read-only) selama job berjalan, atau bisa ada INSERT/UPDATE baru? Jika tidak frozen, keyset pagination mungkin melewatkan baris baru dengan PK lebih kecil dari watermark — perlu strategi tambahan (mis. snapshot isolation atau two-pass).
4. **Logging level & lokasi log file.** Apakah rotating file log harus relatif terhadap CWD, atau path konfigurable dari YAML/CLI? Mempengaruhi Phase 1 (logger setup).
5. **Behavior YAML auto-generate saat target tabel belum ada.** Haruskah introspection error-out, atau mengusulkan DDL `CREATE TABLE` sebagai output sampingan? PRD tidak eksplisit; default plan ini: **error-out, target wajib sudah ada**.

---

## 2. Folder Tree (Arsitektur Direktori)

```
sync-mail/
├── pyproject.toml                  # dependency pinning (PyMySQL, SQLAlchemy 2.0, ruamel.yaml, textual)
├── main.py                         # entrypoint TUI (delegate ke sync_mail.tui.app)
├── plan/                           # PRD & rencana (sudah ada)
├── state/                          # runtime state, dibuat saat job pertama berjalan
│   └── <job_name>.state.json       # last_evaluated_pk per job
├── mappings/                       # YAML mapping yang dihasilkan introspection / diedit manual
│   └── <source>_to_<target>.yaml
├── logs/                           # rotating file log
│   └── sync-mail.log
└── src/
    └── sync_mail/
        ├── __init__.py
        ├── config/
        │   ├── __init__.py
        │   ├── loader.py            # baca YAML mapping → object MappingConfig
        │   ├── schema.py            # dataclass / TypedDict definisi MappingConfig, ColumnMapping
        │   └── validator.py         # validasi semantik mapping (mis. CAST butuh cast_target)
        ├── db/
        │   ├── __init__.py
        │   ├── connection.py        # factory koneksi PyMySQL dgn SSDictCursor; flag profiling off
        │   └── introspect.py        # query information_schema → metadata kolom
        ├── pipeline/
        │   ├── __init__.py
        │   ├── extractor.py         # generator keyset pagination (yield chunks)
        │   ├── transformer.py       # apply ColumnMapping per row (CAST, INJECT_DEFAULT, NONE)
        │   ├── loader.py            # bulk insert via executemany + atomic transaction
        │   └── orchestrator.py      # rangkai extract → transform → load + checkpoint
        ├── state/
        │   ├── __init__.py
        │   └── checkpoint.py        # read/write state.json atomic (temp + rename)
        ├── reconciliation/
        │   ├── __init__.py
        │   └── auto_yaml.py         # heuristik matching kolom → tulis mapping template + ACTION_REQUIRED
        ├── observability/
        │   ├── __init__.py
        │   ├── logger.py            # setup logging (STDOUT INFO + RotatingFileHandler ERROR)
        │   ├── metrics.py           # counter throughput, ETA, batch latency
        │   └── events.py            # event bus (callback/queue) untuk progress feed → TUI
        ├── errors/
        │   ├── __init__.py
        │   └── exceptions.py        # hierarchy: MigrationError, BatchFailedError, MappingError, ResumeError
        └── tui/
            ├── __init__.py
            ├── app.py               # Textual App; layout utama
            ├── screens/
            │   ├── menu.py          # screen pemilih job (introspect / migrate / resume)
            │   ├── introspect.py    # form input source/target table → trigger auto_yaml
            │   ├── migrate.py       # progress bar, throughput, current PK, log panel
            │   └── inspect.py       # viewer state.json + last error
            └── widgets/
                ├── progress.py      # widget progress + ETA
                └── log_panel.py     # widget streaming log dari event bus
```

> **Catatan:** layout `src/sync_mail/...` sengaja dipilih (bukan flat `sync_mail/`) supaya editable install (`pip install -e .`) tidak mencemari root, dan `pyproject.toml` cukup deklarasi `[tool.setuptools.packages.find] where = ["src"]`.

---

## 3. SOP Delegasi (Wajib Dibaca di Awal Setiap Fase)

> **PENTING: Sebelum mengeksekusi penulisan kode untuk task ini, Anda wajib mencari referensi terbaru di internet. Gunakan `context 7` untuk pencarian data *best practice*, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan *up-to-date* dan berkinerja tinggi.**
>
> Aturan tambahan yang berlaku lintas-fase:
> - **Patuhi non-negotiable di `CLAUDE.md`**: server-side cursor, generator streaming, keyset pagination (no `OFFSET`), `executemany`, tidak ada ORM/Pandas tanpa alasan kuat, transaksi atomic per batch, resume via state, profiler/query log dimatikan.
> - **Buat issue Beads** (`bd create`) untuk setiap task sebelum mulai coding; klaim dengan `bd update <id> --claim`; tutup dengan `bd close <id>` setelah acceptance terpenuhi.
> - **Dilarang menyentuh source code di dokumen plan**. Plan adalah panduan logika, bukan implementasi.

---

## 4. Phased Work Plan

### Phase 1 — Project Setup, Dependency, & Observability Foundation

**Tujuan:** Membangun pondasi proyek yang dapat dijalankan: dependency terpasang, struktur paket terbentuk, logging & error hierarchy siap dipakai oleh seluruh modul berikutnya.

> **SOP Delegasi:** *Sebelum eksekusi, wajib cek `context 7` untuk best-practice terbaru: layout `src/`, konfigurasi `pyproject.toml` setuptools modern, pola `logging.handlers.RotatingFileHandler` untuk Python 3.14, dan struktur custom exception hierarchy.*

| File | Tanggung Jawab High-Level |
|---|---|
| `pyproject.toml` | Tambahkan dependency: `PyMySQL`, `SQLAlchemy>=2.0` (Core saja), `ruamel.yaml`, `textual`. Pin minor version. Daftarkan `[project.scripts]` opsional `sync-mail = "main:main"`. Set `[tool.setuptools.packages.find] where = ["src"]`. |
| `src/sync_mail/__init__.py` | Hanya export versi paket. Tidak ada side-effect import. |
| `src/sync_mail/errors/exceptions.py` | Definisikan hierarchy exception: `MigrationError` (base) → `MappingError`, `ConnectionError`, `BatchFailedError`, `ResumeError`, `IntrospectionError`. Setiap exception membawa context dict (job_name, batch_id, last_pk) untuk logging terstruktur. |
| `src/sync_mail/observability/logger.py` | Bangun fungsi `configure_logging(level, log_dir)`: dua handler — StreamHandler (INFO ke STDOUT, format ringkas dengan throughput) + RotatingFileHandler (ERROR ke `logs/sync-mail.log`, maksimal 50MB per rotasi, backup count 5). Format file mencakup timestamp, batch_id, primary_key, stack trace. Pastikan logger root **tidak** memuat query SQL apapun. |
| `src/sync_mail/observability/events.py` | Definisikan kontrak `EventBus` minimal (pub/sub) untuk komunikasi engine → TUI: event types `BatchCommitted`, `BatchFailed`, `JobStarted`, `JobCompleted`, `JobAborted`. Implementasi pakai `queue.Queue` thread-safe (TUI Textual nanti consume via worker thread). |
| `main.py` | Hapus boilerplate PyCharm. Buat fungsi `main()` yang hanya mendelegasikan ke `sync_mail.tui.app:run()` (TUI adalah satu-satunya entrypoint). |

**Acceptance Phase 1:**
- `pip install -e .` sukses di Python 3.14.
- `python main.py` membuka TUI kosong (boleh blank screen, yang penting tidak crash).
- Logger menulis ke `logs/sync-mail.log` saat di-trigger; rotasi terverifikasi dengan log dummy berukuran > 50MB.

---

### Phase 2 — Database Connection Manager

**Tujuan:** Menyediakan factory koneksi yang **selalu** menggunakan server-side cursor dan **tidak pernah** melakukan client-side buffering. Modul ini jadi satu-satunya pintu masuk ke MariaDB di seluruh aplikasi.

> **SOP Delegasi:** *Wajib lookup `context 7` untuk dokumentasi mutakhir PyMySQL `SSDictCursor`, opsi koneksi yang menonaktifkan query log/profiling driver-side, dan praktik connection lifecycle (context manager) untuk Python 3.14.*

| File | Tanggung Jawab High-Level |
|---|---|
| `src/sync_mail/db/connection.py` | Fungsi `connect(role: 'source'|'target', dsn_params)` mengembalikan koneksi PyMySQL dengan `cursorclass=SSDictCursor`. Pastikan `autocommit=False` (kita kelola transaksi manual). Set `init_command` untuk mematikan query log session-level. Sediakan context manager `connection_scope()` yang menjamin `close()` walau exception. Untuk koneksi target, sediakan helper `begin()/commit()/rollback()` yang membungkus transaksi atomic per batch. |

**Acceptance Phase 2:**
- Smoke test: koneksi ke source bisa membuka cursor, fetch 1 row dari `information_schema.tables`, lalu close — tanpa memuat seluruh result set ke RAM (verifikasi via memory profiler kasar).
- Koneksi target dapat menjalankan `BEGIN ... ROLLBACK` tanpa error.
- Tidak ada query yang muncul di log file saat koneksi dibuka/ditutup.

---

### Phase 3 — Schema Introspection & Auto-YAML Generator (Single-Table)

**Tujuan:** Diberi nama satu source table & target table, hasilkan file `mappings/<source>_to_<target>.yaml` yang sudah berisi heuristik mapping kolom plus flag `ACTION_REQUIRED` untuk kolom yang butuh keputusan manual.

> **SOP Delegasi:** *Cek `context 7` untuk dokumentasi terbaru `information_schema.columns` di MariaDB 11.x (kolom `COLUMN_NAME`, `DATA_TYPE`, `IS_NULLABLE`, `COLUMN_DEFAULT`, `EXTRA`), dan praktik penulisan YAML yang preserve order + comment dengan `ruamel.yaml`.*

| File | Tanggung Jawab High-Level |
|---|---|
| `src/sync_mail/db/introspect.py` | Fungsi `describe_table(conn, schema, table)` mengembalikan list metadata kolom (nama, tipe, nullability, default, extra). Hindari `SELECT *` dari `information_schema`; pilih kolom eksplisit untuk efisiensi. |
| `src/sync_mail/reconciliation/auto_yaml.py` | Fungsi `generate_mapping(source_meta, target_meta, source_table, target_table) -> MappingDocument`. Heuristik: (a) kolom dengan nama identik & tipe kompatibel → `transformation_type: NONE`; (b) nama identik tapi tipe beda (mis. ENUM di source, VARCHAR di target) → `CAST` dengan `cast_target` diisi tipe target + komentar `ACTION_REQUIRED: verifikasi mapping nilai`; (c) kolom hanya di target → `source_column: null` + `INJECT_DEFAULT` dengan `default_value: ACTION_REQUIRED`; (d) kolom hanya di source → tidak masuk mapping, tapi dicatat sebagai komentar `# UNMAPPED SOURCE: <name>` di YAML. Tulis file via `ruamel.yaml` agar comment & order terjaga. |
| `src/sync_mail/config/schema.py` | Definisi struktur data: `MappingDocument` (job-level) dan `ColumnMapping` (per-kolom). Belum perlu validator; cukup typed structure. |

**Acceptance Phase 3:**
- Diberi dua tabel demo (source punya kolom ENUM, target punya kolom tambahan `migrated_at`), output YAML mengandung semua skenario PRD §3 dan flag `ACTION_REQUIRED` muncul di kolom yang tepat.
- File YAML hasil dapat di-load kembali oleh `ruamel.yaml` tanpa error parsing.

---

### Phase 4 — Mapping Loader & Validator

**Tujuan:** Setelah operator mengedit YAML hasil Phase 3, modul ini memuatnya menjadi struktur in-memory yang sudah tervalidasi sehingga engine ETL bisa percaya 100% pada data konfigurasi.

> **SOP Delegasi:** *Lookup `context 7` untuk pola validasi konfigurasi modern di Python 3.14 (mis. dataclass + post-init validation, atau `pydantic v2` jika dijustifikasi). Pertimbangkan trade-off menambah dependency vs validasi manual.*

| File | Tanggung Jawab High-Level |
|---|---|
| `src/sync_mail/config/loader.py` | Fungsi `load_mapping(path) -> MappingDocument`. Baca YAML, populate dataclass. Tolak file yang masih mengandung string `ACTION_REQUIRED` di field non-komentar (artinya operator belum selesai edit) — raise `MappingError`. |
| `src/sync_mail/config/validator.py` | Validasi semantik: (a) `transformation_type=CAST` wajib punya `cast_target`; (b) `transformation_type=INJECT_DEFAULT` wajib punya `default_value`; (c) `transformation_type=NONE` wajib punya `source_column` non-null; (d) `batch_size` di rentang 5.000–15.000; (e) tidak ada duplikasi `target_column`. Setiap pelanggaran terkumpul ke list, lempar `MappingError` agregat. |

**Acceptance Phase 4:**
- File YAML valid → loader sukses, `MappingDocument` terisi.
- File YAML dengan `cast_target` kosong → `MappingError` menyebut field & baris.
- File YAML masih ada `ACTION_REQUIRED` → loader menolak.

---

### Phase 5 — Checkpoint / State Management

**Tujuan:** Persist `last_evaluated_pk` per job ke `state/<job_name>.state.json` secara atomic, supaya migrasi dapat resume tepat di titik putus.

> **SOP Delegasi:** *Cek `context 7` untuk pola atomic file write di Python (write-temp + `os.replace`), dan praktik file locking jika diperlukan untuk mencegah dua proses migrasi bersamaan.*

| File | Tanggung Jawab High-Level |
|---|---|
| `src/sync_mail/state/checkpoint.py` | Class `Checkpoint(job_name)` dengan method: `load() -> dict` (return dict kosong jika file belum ada); `save(last_pk, batch_count, status)` (tulis ke file `.tmp` lalu `os.replace` ke path final, sehingga crash di tengah tidak meninggalkan file korup); `mark_aborted(reason)` (status='aborted', simpan reason + timestamp); `mark_completed()` (status='completed'). Field minimum di state.json: `job_name`, `source_table`, `target_table`, `last_pk`, `batches_committed`, `rows_committed`, `status` (running/completed/aborted), `started_at`, `updated_at`, `error` (jika aborted). Optional: file lock via `fcntl` / `portalocker` untuk mencegah dua proses memodifikasi file yang sama. |

**Acceptance Phase 5:**
- Simulasi `kill -9` di tengah `save()` (mis. inject sleep antara write temp & rename) — file final tetap utuh dengan isi sebelumnya.
- `load()` setelah `mark_aborted` mengembalikan status & error message yang benar.

---

### Phase 6 — ETL Pipeline (Extractor, Transformer, Loader)

**Tujuan:** Tiga modul inti yang merupakan jantung sistem. Harus generator-based, low-memory, dan tidak ada satupun yang menampung seluruh result set.

> **SOP Delegasi:** *Wajib `context 7` lookup untuk: (a) `cursor.executemany()` MariaDB best-practice & kalkulasi `max_allowed_packet`; (b) pola generator + context manager Python 3.14; (c) keyset pagination idiom untuk PK numerik & PK komposit (tuple comparison) jika OQ #1 dijawab "ada PK komposit".*

#### 6a. Extractor — `src/sync_mail/pipeline/extractor.py`
- Fungsi generator `extract(conn_source, mapping, last_pk) -> Iterator[list[dict]]`.
- Loop: build query keyset (`WHERE pk > :last_pk ORDER BY pk LIMIT :batch_size`), execute via `SSDictCursor`, kumpulkan baris ke list seukuran `batch_size`, `yield` list, lalu update `last_pk` lokal dari row terakhir.
- Berhenti saat hasil fetch kurang dari `batch_size` (sinyal end-of-stream).
- **Tidak ada `OFFSET`** apapun.

#### 6b. Transformer — `src/sync_mail/pipeline/transformer.py`
- Fungsi `transform(rows, mapping) -> list[tuple]`. Pure function, tanpa I/O.
- Untuk tiap row, iterasi `mapping.mappings` (urutan kolom target = urutan tuple output, supaya bisa langsung di-feed ke `executemany`):
  - `NONE` → ambil nilai dari `source_column`.
  - `CAST` → ambil dari `source_column`, lakukan konversi sesuai `cast_target` (ENUM→VARCHAR cukup `str()`; numeric cast pakai konstruktor tipe Python yang sesuai). Anomali cast (mis. None tidak boleh, tapi kolom NOT NULL) raise `BatchFailedError` dengan context row.
  - `INJECT_DEFAULT` → resolve nilai: jika `default_value == 'CURRENT_TIMESTAMP'`, panggil `datetime.now(UTC)` sekali per batch (caching); selain itu pakai literal.
- Output: list of tuple dalam urutan deterministik.

#### 6c. Loader — `src/sync_mail/pipeline/loader.py`
- Fungsi `load(conn_target, mapping, transformed_rows) -> int` (return rows affected).
- Build `INSERT INTO target_table (col_a, col_b, ...) VALUES (%s, %s, ...)` sekali per job (cache di luar loop).
- Bungkus dengan `BEGIN` → `executemany(insert_sql, transformed_rows)` → `COMMIT`.
- Pada exception apapun: `ROLLBACK`, raise `BatchFailedError` membawa batch_id, last_pk, jumlah row, dan exception asli sebagai cause. **Tidak ada row-by-row fallback** (sesuai keputusan §0).

**Acceptance Phase 6:**
- Extractor di-trace dengan tabel 3 juta row + memory profiler: peak memory < 100MB (indikator generator bekerja).
- Transformer unit test: semua skenario PRD §3 (CAST, NONE, INJECT_DEFAULT static, INJECT_DEFAULT CURRENT_TIMESTAMP) menghasilkan tuple yang benar.
- Loader: batch sukses → COMMIT, target bertambah; batch gagal di tengah (mis. constraint violation) → ROLLBACK, target tidak berubah, exception terlempar.

---

### Phase 7 — Orchestrator & Resume Logic

**Tujuan:** Merangkai Phase 4–6 menjadi satu job migrasi end-to-end dengan checkpointing per batch dan abort-on-failure sesuai keputusan §0.

> **SOP Delegasi:** *Cek `context 7` untuk pola orchestration sederhana (state machine / pipeline pattern) di Python tanpa framework berat, dan praktik graceful shutdown handler untuk SIGINT/SIGTERM.*

| File | Tanggung Jawab High-Level |
|---|---|
| `src/sync_mail/pipeline/orchestrator.py` | Class `MigrationJob(mapping, checkpoint, event_bus)`. Method `run()`: <br>1. Load mapping & validate (Phase 4). <br>2. Buka koneksi source & target (Phase 2). <br>3. Baca checkpoint; jika `status=completed` → emit `JobCompleted` & exit. Jika `status=aborted` → log warning, lanjut dari `last_pk` yang tersimpan. <br>4. Loop `for batch in extractor(...)`: panggil transformer → loader → update checkpoint → emit `BatchCommitted` event berisi metrics (rows, throughput, ETA). <br>5. Saat extractor habis: `mark_completed()`, emit `JobCompleted`. <br>6. Pada `BatchFailedError`: `mark_aborted(reason)`, emit `JobAborted` dengan detail batch & last_pk yang sukses, **STOP** (sesuai keputusan §0). <br>7. Tangkap SIGINT/SIGTERM → flush checkpoint terakhir, emit `JobAborted('user_interrupt')`, exit clean. |
| `src/sync_mail/observability/metrics.py` | Helper kalkulasi throughput (rows/sec moving average) & ETA (sisa rows / throughput). Sumber data: jumlah rows per batch + timestamp dari event bus. |

**Acceptance Phase 7:**
- Run end-to-end dengan tabel 100k row → checkpoint final `status=completed`, jumlah rows source = target.
- Interupsi `Ctrl+C` di tengah → state.json `status=aborted`, `last_pk` valid; rerun otomatis melanjutkan dari `last_pk`, tidak ada duplikat.
- Sengaja masukkan row yang melanggar constraint target di tengah migrasi → job abort, target hanya berisi row sebelum batch gagal, state.json menyimpan reason error.

---

### Phase 8 — TUI (Textual) Frontend

**Tujuan:** Antarmuka utama operator. TUI **hanya** mengkonsumsi engine via event bus + memanggil entrypoint orchestrator; tidak ada logika migrasi di layer TUI.

> **SOP Delegasi:** *Wajib `context 7` lookup untuk: dokumentasi Textual mutakhir (App, Screen, Widget, reactive attributes), pola integrasi worker thread untuk long-running task non-async, dan widget `ProgressBar`, `DataTable`, `RichLog` terbaru.*

| File | Tanggung Jawab High-Level |
|---|---|
| `src/sync_mail/tui/app.py` | Class `SyncMailApp(textual.App)`. Definisikan key bindings (q=quit, r=refresh). Mount screen awal: `MenuScreen`. |
| `src/sync_mail/tui/screens/menu.py` | List opsi: "Introspect schema → generate YAML", "Run migration job", "Inspect last state", "Quit". Navigasi push screen sesuai pilihan. |
| `src/sync_mail/tui/screens/introspect.py` | Form input: source DSN, target DSN, source_table, target_table, output path. Tombol "Generate" → trigger `auto_yaml.generate_mapping()` di worker thread; tampilkan progress + path file hasil. |
| `src/sync_mail/tui/screens/migrate.py` | Layout: header (job_name, source→target), `ProgressBar` total rows, panel metrics (throughput, ETA, rows committed, current PK), `RichLog` panel untuk event stream. Subscribe ke `EventBus`; setiap event update UI via `call_from_thread()`. Tombol "Abort" mengirim signal ke orchestrator. |
| `src/sync_mail/tui/screens/inspect.py` | Pilih file `state/*.state.json`, tampilkan isi terformat (status, last_pk, error trace bila aborted). Berguna saat operator perlu inspeksi sebelum decide resume / fix data. |
| `src/sync_mail/tui/widgets/progress.py` | Custom progress widget yang menampilkan ETA + throughput sliding window. |
| `src/sync_mail/tui/widgets/log_panel.py` | Wrapper `RichLog` yang auto-scroll & filter level (INFO/ERROR). |

**Acceptance Phase 8:**
- TUI bisa launch (`python main.py`), navigasi antar screen mulus, tidak crash saat resize terminal.
- Saat migration job berjalan, progress bar & throughput update real-time (delay < 1 detik).
- Tombol abort menghentikan job dengan checkpoint tersimpan; layar inspect langsung menampilkan status `aborted`.

---

### Phase 9 — Multi-Table Orchestration (Opsional / Fase Lanjutan)

**Tujuan:** Mengangkat batasan single-table dari §0 untuk migrasi schema penuh. **Hanya dikerjakan setelah Phase 1–8 stabil**.

> **SOP Delegasi:** *Cek `context 7` untuk pola dependency graph / topological sort sederhana (tabel dengan FK harus dimigrasikan setelah parent), dan praktik concurrent migration (apakah aman parallel? umumnya tidak, karena bottleneck network).*

| File | Tanggung Jawab High-Level |
|---|---|
| `src/sync_mail/reconciliation/auto_yaml.py` (extend) | Tambah fungsi `generate_mappings_for_schema(source_db, target_db) -> list[Path]` yang loop semua tabel di source, hasilkan satu YAML per pasangan tabel. |
| `src/sync_mail/pipeline/orchestrator.py` (extend) | Tambah `JobBatch(jobs: list[MigrationJob])` dengan urutan eksekusi sekuensial (default) atau topological (jika ada deklarasi dependency antar mapping di YAML). |
| `src/sync_mail/tui/screens/migrate.py` (extend) | Tampilkan daftar job + progress per job + overall progress. |

**Acceptance Phase 9:**
- Auto-generate menghasilkan N file YAML untuk N tabel di source.
- `JobBatch` menjalankan job berurutan; satu job abort tidak menghentikan job berikutnya **kecuali** ada flag `stop_on_failure: true` di config batch.

---

### Phase 10 — Hardening & Documentation

**Tujuan:** Polish akhir sebelum dipakai di production migration window.

> **SOP Delegasi:** *Lookup `context 7` untuk template README terbaik, panduan operasional migrasi DB skala besar, dan checklist pre-flight untuk maintenance window.*

| Artefak | Isi |
|---|---|
| `README.md` (proyek) | Quickstart: install, generate YAML, edit YAML, jalankan TUI, resume. |
| `docs/operational-runbook.md` | Pre-flight checklist (backup target, verifikasi `max_allowed_packet`, freeze source, dry-run dengan tabel kecil), in-flight monitoring (TUI metrics, log file), post-flight verification (count source vs target, sampling row equality). |
| Test suite minimal | `pytest` dengan fixture MariaDB Docker; cover Phase 4 (mapping validator), Phase 5 (checkpoint atomic), Phase 6 (transformer pure functions). End-to-end test memakai dua database in-container dengan 10k row. |
| `pyproject.toml` (final) | Pin versi exact (`==`) untuk reproducibility migration window. |

**Acceptance Phase 10:**
- Test suite hijau di CI lokal.
- Runbook diuji ulang oleh orang lain dari awal sampai selesai tanpa intervensi penulis.

---

## 5. Roadmap Eksekusi yang Direkomendasikan

```
Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 4 ──► Phase 5 ──► Phase 6 ──► Phase 7 ──► Phase 8
                                                                                       │
                                                                                       ├──► Phase 9 (opsional)
                                                                                       └──► Phase 10
```

- Phase 1–2 setup & koneksi: prerequisite mutlak.
- Phase 3–5 dapat dikerjakan paralel oleh dua orang (introspect + state) setelah Phase 2 selesai.
- Phase 6 hanya boleh mulai setelah Phase 4 (loader butuh validated mapping) & Phase 5 (orchestrator butuh checkpoint).
- Phase 8 (TUI) bisa di-prototype paralel dengan Phase 7 menggunakan event bus mock; integrasi nyata setelah Phase 7 stabil.

---

## 6. Definition of Done untuk Keseluruhan Sistem

1. Operator dapat menjalankan `python main.py`, masuk TUI, generate YAML, edit, eksekusi migrasi 1 juta row, resume setelah Ctrl+C, dan mendapatkan target tabel identik dengan source (verified via `COUNT(*)` & sampling).
2. Selama migrasi 1 juta row, peak RSS Python proses tetap di bawah 200 MB (target indikatif; konfirmasi via `psutil` atau `/proc/<pid>/status`).
3. Tidak ada query SQL apapun yang muncul di file log — hanya event-level info & error.
4. Setiap fase memiliki issue Beads tertutup (`bd close`) dengan referensi acceptance criteria yang terpenuhi.
