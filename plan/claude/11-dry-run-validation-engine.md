# Issue: 11 - Dry Run & Validation Engine (Error Reporting Solutif)

## 🎯 Tujuan
Membangun **mode simulasi** yang mengeksekusi seluruh tahap *Extract* dan *Transform* berdasarkan konfigurasi YAML **tanpa** menulis (`INSERT/COMMIT`) ke database target. Tujuan akhirnya: operator dapat memvalidasi sebuah mapping (mis. setelah edit YAML hasil Issue 03) dengan dataset dummy 10–100 baris, lalu menerima **laporan anomali yang lengkap dan rekomendatif** sebelum job nyata dijalankan pada jutaan data. Engine **dilarang crash** saat menemukan error pada satu baris — ia wajib mengumpulkan seluruh anomali, mengelompokkannya, dan menampilkan rekomendasi penanganan yang dapat langsung dieksekusi operator (mis. "Sesuaikan panjang varchar di YAML kolom X menjadi minimal Y", "Tambahkan default value untuk kolom Z").

## 🔗 Dependensi
- **Issue 01** (Foundation) — exception hierarchy & event bus.
- **Issue 02** (DB Connection) — koneksi source untuk Extract simulasi.
- **Issue 04** (Mapping Loader & Validator) — input dry-run adalah `MappingDocument` yang sudah lolos validasi semantik.
- **Issue 05** (Checkpoint) — read-only saja; dry-run boleh menampilkan checkpoint terakhir tapi tidak boleh menulisnya.
- **Issue 06** (ETL Pipeline: Extractor & Transformer) — engine dry-run **memakai ulang** Extractor & Transformer yang sama; yang dimatikan hanya Loader.

> Dependensi ini berarti Issue 11 **baru boleh** dimulai setelah Issue 06 minimal punya extractor + transformer yang berfungsi. Loader tidak diperlukan untuk dry-run.

## 📝 Alur Kerja / Logika Sistem (Step-by-Step)

### A. Prinsip Dasar Dry Run (wajib dipahami sebelum coding)
1. **Tidak ada `BEGIN/INSERT/COMMIT`** ke target. Engine boleh membuka koneksi target hanya untuk *probing* metadata (mis. introspect ulang skema target untuk validasi tipe), tetapi tidak pernah memodifikasi data.
2. **Tidak boleh meledak.** Semua exception yang biasanya menghentikan job nyata (type mismatch, data truncation, NOT NULL violation) **harus ditangkap per baris**, dicatat ke laporan, lalu engine lanjut ke baris berikutnya. Hanya error sistemik (koneksi putus, file mapping rusak) yang menghentikan dry-run.
3. **Sample-friendly.** Dry-run dirancang untuk dataset kecil (10–100 baris) supaya operator cepat iterasi. Sediakan parameter `sample_limit` (default 100) yang membatasi jumlah baris yang ditarik dari source — limit ini diaplikasikan di extractor melalui `LIMIT` aman, **bukan** dengan menarik seluruh tabel lalu memotong di Python.

### B. File Baru yang Dibuat
| File | Tanggung Jawab High-Level |
|---|---|
| `src/sync_mail/pipeline/dry_run.py` | Engine inti dry-run: orkestrasi extract → validate → simulate transform → kumpulkan anomali → keluarkan `DryRunReport`. |
| `src/sync_mail/pipeline/anomaly.py` | Definisi tipe data anomali: `Anomaly` (dataclass) berisi kategori, kolom, baris (PK), nilai mentah, pesan teknis, dan **rekomendasi solutif**. Plus enum `AnomalyCategory`. |
| `src/sync_mail/pipeline/dry_run_report.py` | Formatter laporan: ringkasan agregat (jumlah anomali per kategori), detail per anomali, dan blok rekomendasi yang dikelompokkan. Output dapat berupa `str` (untuk RichLog/console) dan `dict` (untuk konsumsi TUI / file JSON). |
| `src/sync_mail/db/target_probe.py` | Helper read-only yang menarik metadata target (panjang `VARCHAR`, nullability, `DEFAULT`, set `ENUM`) — dipakai oleh validator untuk mendeteksi truncation & constraint violation **tanpa** harus benar-benar INSERT. |

### C. Algoritma Engine Dry Run (high-level)
**Langkah 1 — Persiapan.**
- Terima input: `MappingDocument` (sudah tervalidasi dari Issue 04), koneksi source, koneksi target (read-only), dan `sample_limit`.
- Probing target: ambil metadata kolom target via `target_probe.describe_target_columns(...)`. Hasil: dict `{target_column: {type, max_length, nullable, default, enum_values}}`.
- Sediakan struktur kosong untuk menampung anomali: list `anomalies`, dan counter per kategori.

**Langkah 2 — Sampling Extract.**
- Panggil extractor (Issue 06) dengan parameter tambahan `limit_override = sample_limit`. Extractor harus support membatasi jumlah row total yang di-yield (bukan per batch). Implementasi minimal: hentikan loop ketika akumulasi rows ≥ `sample_limit`.
- Tidak ada checkpoint write. Tidak ada update `last_pk`.

**Langkah 3 — Simulate Transform per baris.**
- Untuk tiap baris hasil extract, jalankan transformer (Issue 06) dalam mode "non-fatal":
  - Bungkus pemanggilan transformer dalam `try/except`. Jika transformer raise exception, **tangkap** dan ubah jadi `Anomaly(category=TRANSFORM_ERROR, ...)`. Jangan re-raise.
- Setelah transformer sukses, lanjut ke Langkah 4 (validasi target-shape).

**Langkah 4 — Validasi Target-Shape (per kolom).**
Untuk tiap nilai hasil transform, evaluasi terhadap metadata target:
1. **Type compatibility.** Apakah tipe Python hasil transform kompatibel dengan tipe SQL target? (mis. `int` ke `VARCHAR` → ok via cast; `str` panjang ke `INT` → anomali `TYPE_MISMATCH`). Gunakan tabel kompatibilitas sederhana yang didokumentasikan di docstring modul.
2. **Length / truncation.** Jika target `VARCHAR(N)` dan `len(str(value)) > N` → anomali `DATA_TRUNCATION`. Sertakan panjang aktual dan rekomendasi: `"Naikkan panjang VARCHAR di mapping/DDL menjadi minimal {actual_len}"`.
3. **NOT NULL violation.** Jika target `NOT NULL` dan nilai hasil transform `None` → anomali `NOT_NULL_VIOLATION`. Rekomendasi: `"Tambahkan transformation_type INJECT_DEFAULT dengan default_value untuk kolom <X>"`.
4. **ENUM membership.** Jika target ENUM dan nilai bukan anggota set → anomali `ENUM_MISMATCH`. Rekomendasi: `"Nilai <v> tidak ada di ENUM target. Mapping ulang via CAST + value-map, atau tambah nilai ke ENUM target"`.
5. **Default tidak resolvable.** Jika `INJECT_DEFAULT` tapi `default_value` tidak resolvable (mis. literal yang tidak match tipe target) → anomali `DEFAULT_INVALID`.

**Langkah 5 — Cross-mapping checks (sekali per dry-run, bukan per baris).**
- **Kolom target tidak tercover oleh mapping** — bandingkan list target columns vs mapping; flag setiap target column yang tidak punya entry mapping (kecuali punya DB-side default). Rekomendasi: `"Tambahkan entry mapping untuk target_column <X>, atau pastikan kolom punya DEFAULT di DDL target"`.
- **Source column tidak ada di tabel source** — flag jika `source_column` di mapping tidak ada di metadata source. Rekomendasi: `"Periksa typo nama kolom source, atau jalankan ulang Issue 03 untuk regenerate mapping"`.
- **Batch size sanity check** — meski validator Issue 04 sudah cek rentang, dry-run laporkan ulang sebagai informasi (bukan error).

**Langkah 6 — Hasilkan `DryRunReport`.**
- Struktur laporan (high-level, lihat juga sub-bagian D):
  - Header: nama job, source→target, timestamp, sample_limit yang dipakai, jumlah baris yang berhasil di-extract.
  - Ringkasan: total anomali, breakdown per kategori (`TYPE_MISMATCH: 12`, `DATA_TRUNCATION: 3`, …).
  - Detail anomali: dikelompokkan per kategori → per kolom → list (baris PK, nilai contoh, pesan, **rekomendasi**).
  - Blok "Rekomendasi Tindak Lanjut": agregasi semua rekomendasi unik (deduplicated) dengan urutan prioritas: blocker (NOT_NULL, TYPE_MISMATCH) di atas, advisory (TRUNCATION, ENUM) di bawah.
  - Status akhir: `PASS` (tidak ada anomali blocker), `WARN` (ada advisory saja), `FAIL` (ada blocker).

**Langkah 7 — Emit event ke EventBus.**
- Engine emit event `DryRunStarted`, `DryRunRowEvaluated` (untuk progress TUI), `DryRunCompleted(report)`. Tidak emit event `BatchCommitted` (tidak ada commit beneran).

### D. Format Laporan yang Mudah Dibaca Operator
Operator manusia harus bisa baca laporan **tanpa** scroll log mentah. Ikuti template berikut (high-level, bukan literal):

```
┌─ DRY RUN REPORT ─────────────────────────────┐
│ Job:        legacy_tx → tx_optimized          │
│ Sample:     100 rows extracted                │
│ Status:     ❌ FAIL (3 blocker, 7 advisory)   │
└───────────────────────────────────────────────┘

▼ BLOCKER
  [TYPE_MISMATCH] kolom target `amount` (INT)
    PK 12, 27, 41
    Contoh nilai: "12.5", "abc", null
    → Rekomendasi: nilai source bukan integer. Ubah cast_target
      menjadi VARCHAR di mapping kolom amount, atau bersihkan
      data source.

▼ ADVISORY
  [DATA_TRUNCATION] kolom target `description` (VARCHAR(50))
    PK 8, 19  (max length aktual: 73)
    → Rekomendasi: naikkan VARCHAR target menjadi minimal 73,
      atau tambah transformation untuk truncate aman.

▼ REKOMENDASI TINDAK LANJUT (deduplicated)
  1. Naikkan VARCHAR target `description` ke ≥73.
  2. Tambah default value untuk kolom `migrated_at`.
  3. Verifikasi konversi tipe `amount` di mapping YAML.
```

### E. Larangan & Pagar Pengaman
- ❌ **Dilarang** memanggil `cursor.executemany()` atau `INSERT` apapun ke target — ini harus dijaga via review code & test (mis. test menggunakan target connection yang sengaja read-only / mock yang fail jika INSERT dipanggil).
- ❌ **Dilarang** menulis `state.json` saat dry-run.
- ❌ **Dilarang** mematikan exception lokal dengan `except: pass` — semua exception harus jadi `Anomaly` dengan pesan teknis & rekomendasi.
- ✅ **Wajib** logging level INFO untuk progress, ERROR hanya untuk error sistemik (bukan anomali per baris — anomali masuk laporan, bukan log error).

## ✅ Kriteria Penerimaan (Acceptance Criteria)
- [ ] Engine dry-run dapat dijalankan terhadap dataset dummy 10–100 baris dan **selesai tanpa exception** meski source berisi baris yang akan menggagalkan migrasi nyata.
- [ ] Tidak ada query `INSERT/UPDATE/DELETE/REPLACE` apapun yang dieksekusi ke target selama dry-run (verifikasi via target connection mock atau log statement-level di test fixture).
- [ ] Setiap kategori anomali (`TYPE_MISMATCH`, `DATA_TRUNCATION`, `NOT_NULL_VIOLATION`, `ENUM_MISMATCH`, `DEFAULT_INVALID`, `TRANSFORM_ERROR`) memiliki minimal satu test case dengan input dummy yang men-trigger anomali tersebut, dan laporan akhir mencantumkan rekomendasi solutifnya.
- [ ] Laporan akhir mencantumkan: header (job, sample, status), ringkasan agregat per kategori, detail per kolom, **blok rekomendasi tindak lanjut yang dideduplikasi**.
- [ ] Status akhir laporan benar: `PASS` jika 0 anomali, `WARN` jika hanya advisory, `FAIL` jika ada blocker.
- [ ] Dry-run **tidak menulis** ke `state/<job>.state.json` (verifikasi: timestamp file sebelum & sesudah dry-run identik).
- [ ] Parameter `sample_limit` default 100; bila operator memberikan nilai lain, extractor menghormati limit tersebut tanpa menarik seluruh tabel.
- [ ] Setiap rekomendasi dalam laporan dapat **langsung dipahami operator non-developer**, mis. "Naikkan VARCHAR kolom X menjadi minimal 73" — bukan "raise StringDataRightTruncation".

## 🤖 SOP Eksekusi (Wajib Dibaca)
**PENTING: Sebelum mengeksekusi penulisan kode untuk task ini, Anda wajib mencari referensi terbaru. Ikuti urutan prioritas berikut:**

1. **JALAN PERTAMA: `/graphify query`** — Gunakan selalu untuk pemindaian file atau mencari logika aplikasi. Hindari pemindaian file secara rekursif (`find`, `ls -R`, dll).
2. **JALAN KEDUA: `context7`** — Selalu utamakan `context7` untuk mendapatkan *best practice*, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan *up-to-date*, aman, dan berkinerja tinggi.
3. **JALAN KETIGA: Pencarian Internet** — Gunakan pencarian internet hanya jika `context7` tidak memberikan informasi yang cukup.

**Prioritas riset untuk task ini:**
- Pola "non-fatal validation pipeline" di Python (kumpulkan error agregat tanpa stop), bandingkan dengan praktik di pydantic v2 / cerberus / voluptuous.
- Cara membaca metadata kolom MariaDB lengkap (panjang VARCHAR, ENUM members, default expression) via `information_schema.columns` — perhatikan kolom `CHARACTER_MAXIMUM_LENGTH` dan `COLUMN_TYPE`.
- Idiom dataclass + enum untuk struktur laporan diagnostik di Python 3.14.

**Pro Tip Verifikasi:** Sebelum diuji pada jutaan data, **wajib** uji engine dry-run pada dummy data 10–100 baris saja. Tujuannya memastikan format laporan sudah benar-benar mudah dibaca operator manusia (rekomendasi solutif, bukan stack trace mentah). Iterasi cepat di skala kecil ini menghemat waktu dibanding menemukan masalah format setelah 1 jam dry-run pada data besar.
