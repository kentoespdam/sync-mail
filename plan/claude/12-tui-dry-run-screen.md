# Issue: 12 - TUI Screen "Dry Run & Validation"

## 🎯 Tujuan
Menambahkan **screen Textual baru** yang menjadi pintu masuk operator untuk menjalankan engine Dry Run (Issue 11) dan membaca laporannya secara interaktif. Screen ini harus mudah dipakai oleh operator non-developer: pilih mapping → tentukan ukuran sample → jalankan → baca laporan terstruktur dengan rekomendasi solutif. Setelah membaca laporan, operator dapat memutuskan apakah akan kembali edit YAML atau melanjutkan ke screen "Run Migration" yang sudah ada.

## 🔗 Dependensi
- **Issue 08** (TUI Textual base) — `SyncMailApp`, `MenuScreen`, dan event bus integration sudah tersedia.
- **Issue 11** (Dry Run Engine) — engine yang menghasilkan `DryRunReport`.
- **Issue 04** (Mapping Loader) — untuk memuat YAML pilihan operator sebelum diumpan ke engine.

## 📝 Alur Kerja / Logika Sistem (Step-by-Step)

### A. Tambahan ke MenuScreen (Issue 08)
- Tambahkan satu opsi baru di daftar menu utama: **"Dry Run / Validate Mapping"**. Posisikan **di atas** opsi "Run Migration Job" — secara alur kerja, dry-run adalah langkah persiapan sebelum migrasi nyata, jadi naikkan visibilitasnya.
- Saat dipilih, push `DryRunScreen` ke stack screen.

### B. File Baru
| File | Tanggung Jawab High-Level |
|---|---|
| `src/sync_mail/tui/screens/dry_run.py` | Screen utama dry-run: form input → trigger engine → tampilkan laporan. |
| `src/sync_mail/tui/widgets/anomaly_table.py` | Widget tabel anomali (wrapping `DataTable`) yang dapat difilter per kategori (`BLOCKER`, `ADVISORY`) dan diurutkan per kolom target. |
| `src/sync_mail/tui/widgets/recommendation_panel.py` | Widget panel "Rekomendasi Tindak Lanjut" yang menampilkan rekomendasi terdeduplikasi dengan ikon prioritas. |

### C. Layout Screen `DryRunScreen`
**Bagian atas (Form Input).**
- Dropdown / file picker: pilih file mapping dari folder `mappings/`.
- Input numerik: `sample_limit` (default 100, min 10, max 1000).
- Tombol: **"Jalankan Dry Run"** — disabled jika mapping belum dipilih.
- Tombol: **"Kembali ke Menu"**.

**Bagian tengah (Status & Progress).**
- Label status: `Idle` → `Connecting` → `Extracting (n/sample_limit)` → `Validating` → `Done`.
- Progress bar kecil yang konsumsi event `DryRunRowEvaluated` dari event bus (Issue 11).

**Bagian bawah (Hasil — terlihat setelah dry-run selesai).**
- Header laporan: nama job, source→target, sample size, **badge status** (`✅ PASS` / `⚠ WARN` / `❌ FAIL`) dengan warna kontras.
- Tab atau kolom kiri-kanan:
  - **Kiri (60%):** `AnomalyTable` — kolom: `Kategori`, `Target Column`, `PK`, `Nilai`, `Pesan`. Filter dropdown di atas tabel untuk pilih kategori.
  - **Kanan (40%):** `RecommendationPanel` — list rekomendasi terdeduplikasi, dengan badge prioritas (`🔴 Blocker`, `🟡 Advisory`).
- Tombol bawah:
  - **"Simpan Laporan ke File"** — export ke `logs/dry-run-<timestamp>.txt` (format teks-plain) dan `.json` (format mesin).
  - **"Edit Mapping"** — buka path mapping di pesan helper (TUI tidak mengedit, tapi tampilkan path agar operator buka di editor luar).
  - **"Lanjut ke Run Migration"** — disabled jika status `FAIL`. Jika `PASS` / `WARN`, push `MigrateScreen` (Issue 08).

### D. Aturan Eksekusi Engine dari TUI
1. **Worker thread.** Engine dry-run **wajib** dijalankan di worker thread (sama seperti pola Issue 08), bukan di thread utama Textual. Gunakan `App.run_worker(...)` atau pola `call_from_thread()` untuk update UI.
2. **Cancellable.** Sediakan tombol **"Batal"** yang muncul saat dry-run berjalan; menekannya mengirim sinyal stop ke engine dan engine harus berhenti pada batas baris berikutnya (graceful, bukan kill).
3. **Tidak boleh memblok UI.** Update progress maksimal setiap 100ms (rate-limited) untuk menghindari render storm di Textual.
4. **Tidak menulis state.** Tegaskan di komentar header file: dry-run TUI screen dilarang memanggil API checkpoint/state.

### E. Aturan UX Pelaporan
- **Bahasa Indonesia** untuk semua label, status, dan rekomendasi (konsisten dengan PRD).
- Anomali yang sama (kategori + kolom + pesan) di banyak baris **digabung** di tabel jadi satu entry dengan kolom `PK` berisi list ringkas (`12, 27, 41` atau `12, 27, ...(+38 lagi)` jika > 5).
- Rekomendasi panel **mendeduplikasi**: jika 30 baris memunculkan rekomendasi "Naikkan VARCHAR description ke ≥73", tampilkan sekali.
- Jika status `PASS`, tampilkan pesan ramah: `✅ Mapping siap dipakai. Anda boleh melanjutkan ke "Run Migration".`
- Jika status `FAIL`, blokir tombol "Lanjut ke Run Migration" dan tampilkan tooltip: `Selesaikan blocker terlebih dahulu sebelum migrasi nyata.`

### F. Integrasi Event Bus
- Subscribe ke event types dari Issue 11: `DryRunStarted`, `DryRunRowEvaluated`, `DryRunCompleted`, `DryRunCancelled`.
- Setiap event masuk diproses via `call_from_thread()` agar update widget aman.

## ✅ Kriteria Penerimaan (Acceptance Criteria)
- [ ] Operator dapat membuka `DryRunScreen` dari menu utama, memilih mapping, set `sample_limit`, dan menjalankan dry-run tanpa crash.
- [ ] Saat engine berjalan, UI menampilkan progress real-time (lag < 1 detik) dan tombol **Batal** dapat menghentikan dry-run dengan graceful (engine tidak meledak, UI kembali ke status `Cancelled`).
- [ ] Setelah dry-run selesai, badge status (`PASS`/`WARN`/`FAIL`) muncul dengan warna yang benar.
- [ ] Anomali yang berulang **digabung** di tabel (1 baris untuk N kejadian) dan rekomendasi yang berulang **dideduplikasi** di panel rekomendasi.
- [ ] Tombol **"Lanjut ke Run Migration"** disabled saat status `FAIL`.
- [ ] Tombol **"Simpan Laporan ke File"** menghasilkan dua file di `logs/`: `.txt` untuk dibaca manusia, `.json` untuk dikonsumsi tooling lain.
- [ ] Resize terminal ke ukuran kecil (mis. 80×24) tidak merusak layout (tabel & panel tetap dapat di-scroll).
- [ ] Smoke test (`tests/test_tui_smoke.py`) di-extend: mount `DryRunScreen` dengan engine dummy yang langsung mengembalikan laporan, verifikasi semua widget utama ter-render.

## 🤖 SOP Eksekusi (Wajib Dibaca)
**PENTING: Sebelum mengeksekusi penulisan kode untuk task ini, Anda wajib mencari referensi terbaru. Ikuti urutan prioritas berikut:**

1. **JALAN PERTAMA: `/graphify query`** — Gunakan selalu untuk pemindaian file atau mencari logika aplikasi. Hindari pemindaian file secara rekursif (`find`, `ls -R`, dll).
2. **JALAN KEDUA: `context7`** — Selalu utamakan `context7` untuk mendapatkan *best practice*, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan *up-to-date*, aman, dan berkinerja tinggi.
3. **JALAN KETIGA: Pencarian Internet** — Gunakan pencarian internet hanya jika `context7` tidak memberikan informasi yang cukup.

**Prioritas riset untuk task ini:**
- Dokumentasi Textual mutakhir untuk: `Screen` lifecycle, `DataTable` (sorting & filtering), `ProgressBar`, `Worker` API, `call_from_thread()`, dan reactive attributes.
- Pola "rate-limit UI update" agar tidak terjadi render storm saat event datang ratusan kali per detik.
- Best practice menerapkan layout `Horizontal`/`Vertical` Textual untuk tata letak 60/40 yang responsif terhadap resize.

**Catatan TUI styling (project convention):**
- Jangan pakai `margin: auto`. Gunakan `align: center middle` di parent + `width` eksplisit di child.
- Nilai `margin` hanya integer (sel terminal).
- Smoke test wajib di `tests/test_tui_smoke.py`.

**Pro Tip Verifikasi:** Saat menguji screen ini, gunakan engine dummy yang menghasilkan laporan beragam (PASS, WARN, FAIL dengan campuran kategori). Pastikan operator non-developer dapat membaca laporan dan menemukan rekomendasi tanpa harus bertanya ke developer — itu adalah indikator bahwa fitur dry-run benar-benar berguna sebelum dipakai pada data jutaan baris.
