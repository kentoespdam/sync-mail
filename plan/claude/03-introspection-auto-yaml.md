# Issue: 03 - Schema Introspection & Auto-Generate YAML (Single-Table)

## 🎯 Tujuan
Diberi nama satu tabel source dan satu tabel target di MariaDB, hasilkan otomatis sebuah file YAML mapping di folder `mappings/` yang sudah berisi tebakan kolom-per-kolom plus penanda `ACTION_REQUIRED` untuk kolom-kolom yang masih butuh keputusan manual operator. Tujuannya menghemat waktu operator: ia hanya perlu mengoreksi tebakan, bukan mengetik mapping dari nol.

## 🔗 Dependensi
- Issue 01 (Foundation)
- Issue 02 (DB Connection) — kita butuh koneksi ke kedua database untuk introspeksi.

## 📝 Alur Kerja / Logika Sistem (Step-by-Step)

**Langkah 1: Definisikan struktur data mapping di `src/sync_mail/config/schema.py`.**
- Buat tipe data `MappingDocument` (level job) yang menampung: `source_table`, `target_table`, `batch_size`, dan list `mappings`.
- Buat tipe data `ColumnMapping` (level kolom) yang menampung: `source_column` (nullable), `target_column`, `transformation_type` (`NONE` | `CAST` | `INJECT_DEFAULT`), `cast_target` (nullable), `default_value` (nullable).
- Cukup typed structure (mis. `dataclass`); validator semantik akan dibuat di Issue 04.

**Langkah 2: Buat fungsi introspeksi di `src/sync_mail/db/introspect.py`.**
- Sediakan `describe_table(conn, schema, table)` yang mengembalikan list metadata kolom.
- Query ke `information_schema.columns`. Pilih kolom eksplisit (`COLUMN_NAME`, `DATA_TYPE`, `IS_NULLABLE`, `COLUMN_DEFAULT`, `EXTRA`) — jangan `SELECT *` agar efisien.
- Jika tabel tidak ditemukan: lempar `IntrospectionError` dengan context `{schema, table}`.
- Jaga urutan kolom sesuai `ORDINAL_POSITION` agar mapping output deterministik.

**Langkah 3: Buat heuristik rekonsiliasi di `src/sync_mail/reconciliation/auto_yaml.py`.**
- Sediakan fungsi `generate_mapping(source_meta, target_meta, source_table, target_table) -> MappingDocument`.
- Iterasi tiap kolom target:
  - **(a) Nama identik & tipe kompatibel** (mis. dua-duanya `INT`, dua-duanya `VARCHAR` panjang sama) → `transformation_type: NONE`.
  - **(b) Nama identik tapi tipe berbeda** (mis. source `ENUM`, target `VARCHAR`) → `transformation_type: CAST`, isi `cast_target` dengan tipe target. Tambahkan komentar inline `# ACTION_REQUIRED: verifikasi mapping nilai` agar operator tahu perlu di-review.
  - **(c) Kolom hanya ada di target** → `source_column: null`, `transformation_type: INJECT_DEFAULT`, `default_value: ACTION_REQUIRED`. Operator wajib mengganti placeholder ini sebelum mapping bisa di-load (loader Issue 04 akan menolak file dengan `ACTION_REQUIRED` tersisa).
- Iterasi kolom source yang tidak ada di target: jangan masukkan ke mapping, tapi **catat sebagai komentar di YAML** dengan format `# UNMAPPED SOURCE: <name>` agar operator sadar ada data yang dibuang.
- Set `batch_size` default ke nilai yang masuk akal (mis. 10000).

**Langkah 4: Tulis output YAML.**
- Pakai `ruamel.yaml` (bukan `PyYAML`) karena hanya ruamel yang bisa preserve order kolom dan menulis komentar inline.
- Output disimpan ke `mappings/<source_table>_to_<target_table>.yaml`. Buat folder `mappings/` jika belum ada.
- Pastikan setiap mapping kolom diawali dengan komentar singkat tipe transformasi (mis. `# CAST: ENUM('a','b') -> VARCHAR(64)`) untuk membantu operator memahami konteks.

**Langkah 5: Tangani edge case.**
- Jika tabel target belum ada: berdasarkan keputusan master plan (§1 OQ #5), default-nya **error-out** dengan `IntrospectionError`. Jangan generate DDL otomatis.
- Jika source dan target identik 100% kolom & tipe: tetap generate mapping (semua `NONE`), agar operator bisa langsung pakai tanpa edit.

## ✅ Kriteria Penerimaan (Acceptance Criteria)
- [ ] Diberi pasangan tabel demo (source punya kolom `ENUM`, target punya kolom tambahan `migrated_at`), output YAML mengandung 4 skenario PRD (CAST, NONE, INJECT_DEFAULT) dan flag `ACTION_REQUIRED` muncul di kolom yang tepat.
- [ ] Komentar `# UNMAPPED SOURCE: <name>` muncul untuk kolom source yang tidak ada di target.
- [ ] File YAML hasil dapat di-parse kembali oleh `ruamel.yaml` tanpa error.
- [ ] Urutan kolom di YAML output mengikuti `ORDINAL_POSITION` tabel target.
- [ ] Saat tabel target tidak ada, fungsi melempar `IntrospectionError` dengan pesan yang jelas.

## 🤖 SOP Eksekusi (Wajib Dibaca)
PENTING: Selalu utamakan mencari referensi terbaru di internet. Jika perlu gunakan `context 7` untuk pencarian data *best practice*, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan *up-to-date*, aman, dan berkinerja tinggi. Khusus untuk task ini, prioritaskan riset: dokumentasi `information_schema.columns` MariaDB 11.x (kolom tersedia dan semantik `EXTRA`), API mutakhir `ruamel.yaml` untuk preserve order + write komentar inline, dan strategi pencocokan tipe data yang aman antar versi MariaDB.
