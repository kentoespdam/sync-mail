# Issue: 06 - ETL Pipeline (Extractor, Transformer, Loader)

## 🎯 Tujuan
Membangun tiga modul inti yang menjadi jantung sistem migrasi: **Extractor** (mengambil data dari source secara streaming dengan keyset pagination, tanpa menumpuk data di RAM), **Transformer** (menerapkan aturan mapping per baris secara murni, tanpa I/O), dan **Loader** (mem-bulk-insert hasil transformasi ke target dengan transaksi atomic per batch). Tiga modul ini wajib generator-based dan low-memory — kontrak keras dari PRD untuk dapat menangani jutaan baris.

> **Catatan:** Karena task ini ukurannya cukup besar, disarankan dipecah menjadi tiga sub-issue (06a Extractor, 06b Transformer, 06c Loader) saat dieksekusi. Dokumen ini menyatukannya supaya konteks pipeline tetap utuh.

## 🔗 Dependensi
- Issue 02 (DB Connection) — extractor & loader butuh koneksi yang sudah benar.
- Issue 04 (Mapping Loader & Validator) — transformer & loader butuh `MappingDocument` yang sudah valid.
- Issue 05 (Checkpoint) — extractor butuh tahu `last_pk` untuk titik mulai.

## 📝 Alur Kerja / Logika Sistem (Step-by-Step)

### 6a. Extractor — `src/sync_mail/pipeline/extractor.py`

**Langkah 1: Buat fungsi generator `extract(conn_source, mapping, last_pk)`.**
- Output: iterator yang setiap kali di-iterasi, yield satu list of dict (satu chunk berisi sampai `mapping.batch_size` baris).
- **Tidak boleh** mengembalikan list lengkap semua chunk — itu merusak model streaming.

**Langkah 2: Loop fetch dengan keyset pagination.**
- Setiap iterasi: bangun query `SELECT <kolom yang dibutuhkan> FROM source_table WHERE pk > :last_pk ORDER BY pk LIMIT :batch_size`.
- Eksekusi via `SSDictCursor`. Fetch semua hasil di chunk ini ke list lokal.
- `yield list_chunk`.
- Update variabel `last_pk` lokal dengan PK dari row terakhir di chunk.
- Berhenti loop saat hasil fetch < `batch_size` (sinyal end-of-stream).

**Langkah 3: Larangan keras `OFFSET`.**
- Tidak ada satu pun query yang boleh memakai `LIMIT x OFFSET y`. Ini akan memaksa MariaDB scan ulang baris sebelumnya — overhead Disk I/O yang menghabiskan waktu eksponensial.

**Langkah 4: Identifikasi kolom PK.**
- Untuk versi pertama, asumsikan PK numerik monotonic single-column (sesuai keputusan default di master plan §1 OQ #1).
- Jika nanti dibutuhkan PK komposit, gunakan tuple comparison `WHERE (a, b) > (:last_a, :last_b)` — tapi ini ekstensi fase berikutnya.

---

### 6b. Transformer — `src/sync_mail/pipeline/transformer.py`

**Langkah 1: Buat fungsi murni `transform(rows, mapping) -> list[tuple]`.**
- **Pure function, no I/O.** Tidak menyentuh database, tidak menyentuh disk, tidak melempar event. Hanya transformasi data.
- Input: list dict (output extractor) + `MappingDocument`.
- Output: list of tuple, di mana urutan elemen tuple **sama** dengan urutan `target_column` di `mapping.mappings`. Ini penting agar bisa langsung di-feed ke `executemany` di loader.

**Langkah 2: Iterasi setiap row.**
- Untuk setiap `ColumnMapping` di mapping:
  - **`NONE`**: ambil nilai `row[source_column]`.
  - **`CAST`**: ambil `row[source_column]`, lakukan konversi sesuai `cast_target`. Untuk ENUM→VARCHAR cukup `str(value)`. Untuk numeric cast pakai konstruktor tipe Python yang sesuai (`int`, `float`, `Decimal`). Jika nilai None tapi kolom target NOT NULL: lempar `BatchFailedError` dengan context row (PK + nama kolom).
  - **`INJECT_DEFAULT`**: resolve nilai dari `default_value`. Jika string-nya `'CURRENT_TIMESTAMP'` → panggil `datetime.now(UTC)` SEKALI per batch (cache di luar loop) lalu pakai untuk semua row di batch. Selain itu pakai literal langsung.

**Langkah 3: Output deterministik.**
- Urutan kolom di tuple wajib sama untuk semua row di satu batch. Loader akan caching SQL `INSERT INTO ... VALUES (%s, %s, ...)` di luar loop, jadi kalau urutan tuple berubah, query akan rusak.

---

### 6c. Loader — `src/sync_mail/pipeline/loader.py`

**Langkah 1: Buat fungsi `load(conn_target, mapping, transformed_rows) -> int`.**
- Output: jumlah baris yang sukses di-insert (`cursor.rowcount`).

**Langkah 2: Cache SQL INSERT statement di luar loop.**
- Bangun string `INSERT INTO target_table (col_a, col_b, ...) VALUES (%s, %s, ...)` SEKALI saat loader pertama kali dipanggil (atau di constructor jika dibuat class). Jangan generate ulang per batch — itu pemborosan.

**Langkah 3: Bungkus dengan transaksi atomic.**
- Pakai helper transaksi dari Issue 02: `BEGIN` → `cursor.executemany(insert_sql, transformed_rows)` → `COMMIT`.
- Saat exception apapun di dalam blok: `ROLLBACK`, lalu lempar `BatchFailedError(batch_id, last_pk, row_count, original_exception)`.

**Langkah 4: Tidak ada row-by-row fallback otomatis.**
- Sesuai keputusan master plan §0: saat batch gagal, **abort** seluruh job. Operator akan inspect manual untuk menentukan baris mana yang bermasalah, lalu fix data atau mapping.
- Ini berbeda dari opsi PRD §5 yang menyebutkan row-by-row fallback — kita pilih jalur abort untuk simplicity dan kontrol.

**Langkah 5: Tuning batch size.**
- `batch_size` dari mapping diasumsikan sudah valid (5.000–15.000) berkat validator Issue 04.
- Jika MariaDB error `Packet too large`, itu sinyal `batch_size` dipasang terlalu besar untuk `max_allowed_packet` target. Pesan error harus jelas menyarankan operator turunkan `batch_size`.

## ✅ Kriteria Penerimaan (Acceptance Criteria)
- [ ] **Extractor**: tabel 3 juta row + memory profiler → peak RSS < 100 MB (indikator generator bekerja).
- [ ] **Extractor**: Tidak ada query memakai `OFFSET` di seluruh codebase (verifikasi via grep).
- [ ] **Transformer**: unit test untuk semua skenario PRD (CAST ENUM→VARCHAR, NONE, INJECT_DEFAULT static, INJECT_DEFAULT CURRENT_TIMESTAMP) menghasilkan tuple dengan nilai dan urutan yang benar.
- [ ] **Transformer**: Pure function — tidak ada call ke `requests`, `open()`, koneksi DB, atau side-effect lain.
- [ ] **Loader**: batch sukses → COMMIT, target bertambah; jumlah row di target = jumlah row yang dikirim.
- [ ] **Loader**: batch gagal di tengah (mis. constraint violation pada row ke-5000 dari 10000) → ROLLBACK, target tidak berubah, `BatchFailedError` terlempar dengan context lengkap.
- [ ] **Loader**: SQL INSERT statement di-cache, tidak di-rebuild per batch.

## 🤖 SOP Eksekusi (Wajib Dibaca)

**PENTING: Sebelum mengeksekusi penulisan kode untuk task ini, Anda wajib mencari referensi terbaru. Ikuti urutan prioritas berikut:**

1. **JALAN PERTAMA: `/graphify query`** — Gunakan selalu untuk pemindaian file atau mencari logika aplikasi. Hindari pemindaian file secara rekursif (`find`, `ls -R`, dll).
2. **JALAN KEDUA: `context7`** — Selalu utamakan `context7` untuk mendapatkan *best practice*, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan *up-to-date*, aman, dan berkinerja tinggi.
3. **JALAN KETIGA: Pencarian Internet** — Gunakan pencarian internet hanya jika `context7` tidak memberikan informasi yang cukup.

**Prioritas riset untuk task ini:**
- Praktik `cursor.executemany()` MariaDB & kalkulasi `max_allowed_packet`
- Pola generator + context manager Python 3.14
- Idiom keyset pagination single-column dan komposit
- Perbandingan strategi cast ENUM→VARCHAR (apakah `str()` cukup atau perlu lookup tabel mapping)
