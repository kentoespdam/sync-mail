# Issue: 04 - Mapping Loader & Validator

## 🎯 Tujuan
Setelah operator mengedit YAML hasil Issue 03, modul ini bertugas memuat YAML tersebut menjadi struktur data in-memory yang **sudah tervalidasi**, sehingga engine ETL di fase selanjutnya bisa percaya 100% pada data konfigurasi tanpa perlu re-check di tengah jalan. Validator harus menolak file yang belum siap (mis. masih ada `ACTION_REQUIRED` yang belum diganti) dan memberikan pesan error yang jelas dan agregat (semua pelanggaran sekaligus, bukan satu per satu).

## 🔗 Dependensi
- Issue 01 (Foundation) — exception hierarchy.
- Issue 03 (Auto-YAML) — struktur `MappingDocument`/`ColumnMapping` di `config/schema.py` sudah didefinisikan.

## 📝 Alur Kerja / Logika Sistem (Step-by-Step)

**Langkah 1: Buat loader di `src/sync_mail/config/loader.py`.**
- Sediakan fungsi `load_mapping(path) -> MappingDocument`.
- Baca file YAML pakai `ruamel.yaml` (sama seperti Issue 03 untuk konsistensi).
- Populate ke struktur `MappingDocument` dan `ColumnMapping`. Konversi tipe field jelas: string ke string, integer ke integer, dst.
- Setelah parsing struktural berhasil, langsung panggil validator (langkah 2). Loader **tidak boleh** mengembalikan `MappingDocument` yang belum tervalidasi.

**Langkah 2: Buat validator semantik di `src/sync_mail/config/validator.py`.**
- Sediakan fungsi `validate(mapping_doc) -> None` (raise `MappingError` jika invalid).
- Aturan validasi (kumpulkan SEMUA pelanggaran, baru lempar agregat di akhir):
  - **(a)** `transformation_type=CAST` wajib punya `cast_target` non-empty.
  - **(b)** `transformation_type=INJECT_DEFAULT` wajib punya `default_value` non-empty.
  - **(c)** `transformation_type=NONE` wajib punya `source_column` non-null.
  - **(d)** `batch_size` wajib di rentang 5.000 – 15.000 (sesuai kontrak PRD performa).
  - **(e)** Tidak boleh ada duplikasi `target_column` dalam satu mapping document.
  - **(f)** Tidak boleh ada string `ACTION_REQUIRED` tersisa di field non-komentar (artinya operator belum selesai edit). Tolak dengan pesan jelas yang menunjuk kolom mana saja yang belum di-fix.
  - **(g)** `source_table` dan `target_table` tidak boleh kosong.

**Langkah 3: Format pesan error yang ramah operator.**
- Kumpulkan semua pelanggaran ke list. Format pesan akhir: `"Mapping file <path> tidak valid:\n- baris X: <pelanggaran>\n- baris Y: <pelanggaran>\n..."`.
- Sertakan nomor baris jika `ruamel.yaml` mendukungnya, supaya operator langsung tahu di mana harus edit.
- Lempar `MappingError` dengan agregasi pelanggaran sebagai context.

**Langkah 4: Sediakan helper untuk kasus edge.**
- Jika file tidak ada: `MappingError("Mapping file tidak ditemukan: <path>")`.
- Jika YAML rusak (parse error): bungkus exception ruamel jadi `MappingError` dengan pesan parse.

**Langkah 5: Smoke test manual.**
- Siapkan tiga file YAML dummy: satu valid, satu dengan `cast_target` kosong, satu dengan `ACTION_REQUIRED` tersisa.
- Pastikan loader menerima yang valid dan menolak dua sisanya dengan pesan error agregat.

## ✅ Kriteria Penerimaan (Acceptance Criteria)
- [ ] File YAML valid → `load_mapping()` sukses, `MappingDocument` terisi lengkap.
- [ ] File YAML dengan `cast_target` kosong → `MappingError` menyebut field, baris, dan jumlah pelanggaran lain (jika ada).
- [ ] File YAML masih mengandung `ACTION_REQUIRED` di field non-komentar → loader menolak dengan pesan eksplisit.
- [ ] File YAML dengan duplikasi `target_column` → loader menolak dan menyebut kolom yang duplikat.
- [ ] `batch_size` di luar rentang 5.000–15.000 → loader menolak dengan pesan rentang yang valid.
- [ ] Pesan error validator menampilkan **semua** pelanggaran sekaligus, bukan satu-per-satu (agregat).

## 🤖 SOP Eksekusi (Wajib Dibaca)
PENTING: Selalu utamakan mencari referensi terbaru menggunakan `context 7` untuk pencarian data *best practice*, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan *up-to-date*, aman, dan berkinerja tinggi
kemudian melalui internet jika diperlukan. Khusus untuk task ini, prioritaskan riset: pola validasi konfigurasi modern di Python 3.14 (dataclass + post-init validation, atau pertimbangkan `pydantic v2` jika trade-off menambah dependency justifiable), dan API `ruamel.yaml` untuk mengambil nomor baris saat reporting error. Prioritaskan menggunakan `context7` untuk pencarian dokumentasi eksternal, dan **prioritaskan selalu mencoba mencari informasi melalui `/graphify query` sebelum menggunakan `file_scanner`** untuk memahami konteks internal codebase.
