# Issue: 02 - Automated HTML Reporting Engine

## 🎯 Tujuan
Memberikan **artefak laporan tunggal berformat HTML** yang merangkum hasil setiap operasi `sync-mail` — baik Sync Sukses, Sync Gagal, maupun Dry Run — ke dalam satu file *standalone* yang mudah dibagikan ke pemangku kepentingan non-teknis (atasan, auditor, tim DBA target). Operator tidak perlu lagi men-screenshot TUI atau menyalin log mentah; cukup satu file HTML yang dapat dibuka di browser apa pun, tanpa server dan tanpa dependensi eksternal. Laporan harus **informatif sekaligus dapat ditindaklanjuti**: status keseluruhan terbaca dalam tiga detik pertama (lewat *status badge* yang dominan), lalu tabel statistik mempertegas skala data yang diproses, dan terakhir blok rekomendasi memberi tahu operator langkah perbaikan apabila ditemukan kegagalan atau anomali. Modul ini menjadi *closing capstone* dari rangkaian fitur engine: ia mengubah hasil eksekusi pipeline menjadi dokumentasi yang persisten dan profesional.

## 🔗 Dependensi
- **Issue 11 (Dry Run & Validation Engine)** dari `plan/claude/11-dry-run-validation-engine.md` — sumber utama data anomali. Engine ini sudah menghasilkan struktur `DryRunReport` lengkap dengan kategori anomali, kolom terdampak, dan rekomendasi solutif. HTML Reporting Engine **mengkonsumsi** struktur tersebut, bukan menghitung ulang.
- **Issue 06 / 07 (ETL Pipeline & Orchestrator)** dari `plan/claude/06-etl-pipeline.md` dan `plan/claude/07-orchestrator-resume.md` — sumber data hasil Sync nyata: jumlah baris yang berhasil di-`COMMIT`, jumlah baris yang gagal pada fallback per-row, durasi total job, last evaluated primary key, status akhir (`COMPLETED` / `ABORTED`). HTML Reporting Engine memanfaatkan ringkasan yang sudah dipublikasikan oleh orchestrator melalui event bus dan checkpoint final.
- **Issue 09 (Multi-Table Orchestration)** dari `plan/claude/09-multi-table-orchestration.md` — apabila satu sesi sinkronisasi menjalankan banyak tabel sekaligus, laporan HTML wajib mampu merangkum hasil per-tabel dalam satu file induk, bukan menerbitkan banyak file terpisah.
- **Issue 01 (Optional YAML Connection Configuration)** dari `plan/feature/2026-04-29-optional-yaml-connection-config.md` — penting untuk konteks: laporan menampilkan identitas koneksi **tanpa** membocorkan password (host & database name boleh, kredensial sensitif dimasking).

> Issue 02 ini **baru boleh dimulai** setelah Issue 11 menghasilkan struktur `DryRunReport` yang stabil dan Issue 06/07 sudah memublikasikan event ringkasan akhir job. Tanpa kedua sumber data tersebut, generator HTML tidak punya bahan baku.

## 📝 Alur Kerja / Logika Sistem (Step-by-Step)

### Langkah 0 — Pemindaian Alur Data Eksisting (WAJIB sebelum coding)
Sebelum menulis baris kode apa pun, developer/agent **wajib** menjalankan pemindaian alur data menggunakan `graphify query` untuk memastikan posisi modul baru ini di dalam pipeline. Pertanyaan minimum yang harus dijawab dari hasil pemindaian:
1. Di titik mana orchestrator menandai akhir dari sebuah job (sukses, gagal, atau abort)?
2. Di titik mana DryRunEngine menutup eksekusinya dan menyerahkan `DryRunReport`?
3. Bagaimana event bus memublikasikan event ringkasan, dan siapa konsumernya saat ini (TUI? Logger?)?
4. Apakah sudah ada konvensi penamaan direktori output (mis. `state/`, `checkpoints/`)?

Hasil pemindaian ini akan menentukan **dua keputusan arsitektural**: (a) di file mana hook generator HTML ditempelkan; (b) bagaimana data dikumpulkan tanpa menambah *coupling* ke orchestrator.

### Langkah 1 — Pengumpulan Data (in-memory aggregator)
Sediakan satu kontainer data terstruktur di memori yang merangkum seluruh fakta yang dibutuhkan laporan. Kontainer ini diisi secara **inkremental** selama job berjalan, sehingga saat job selesai, semua data sudah siap dirender tanpa perlu membaca ulang dari database atau file. Isi minimum kontainer:
- Identitas job: nama tabel sumber, nama tabel target, nama file mapping, mode operasi (`DRY_RUN` / `REAL_SYNC`), waktu mulai, waktu selesai, durasi total.
- Identitas koneksi (tanpa password): host & nama database source dan target.
- Statistik baris: total yang dipindai dari source, total yang berhasil ditransform, total yang berhasil di-`COMMIT` (untuk Real Sync) atau total yang lolos validasi (untuk Dry Run), total yang gagal, total yang dilewati.
- Statistik batch: jumlah batch yang sukses, jumlah batch yang harus *fallback* per-row, last evaluated primary key.
- Daftar anomali / error terperinci: kategori, kolom terdampak, primary key baris bermasalah, nilai mentah yang menyebabkan error, pesan teknis singkat, dan **rekomendasi aksi** (mis. "perpanjang `VARCHAR` ke minimal 255", "tambahkan `default_value` di YAML untuk kolom X", "kolom Y di target butuh `NOT NULL`, tetapi source mengirim NULL").
- Metadata environment: versi `sync-mail`, versi Python, hostname mesin pelaksana.

Aggregator ini idealnya menjadi *consumer* dari event bus yang sudah ada (lihat Issue 06/11) sehingga ia hanya **mendengarkan** event dan tidak menyentuh internal pipeline.

### Langkah 2 — Pemilihan Mode Render
Generator HTML harus bercabang berdasarkan mode operasi:
- **Mode Real Sync — SUCCESS:** seluruh batch commit, `failed_rows == 0`. Status badge **hijau**, judul "Sync Selesai Dengan Sukses". Bagian rekomendasi disembunyikan atau diganti pesan apresiatif singkat.
- **Mode Real Sync — FAILED / WARNING:** ada baris yang gagal di fallback, atau job di-abort di tengah jalan. Status badge **merah** (FAILED) atau **kuning** (WARNING — sukses sebagian). Tabel error wajib tampil dan rekomendasi diaktifkan.
- **Mode Dry Run:** status badge **biru** dengan label "DRY RUN — TIDAK ADA DATA YANG DITULIS" agar tidak tertukar dengan Real Sync. Banner peringatan ini harus dominan secara visual supaya pembaca laporan tidak salah tafsir.

Pemilihan mode dilakukan sekali di awal render dan menentukan *theme variables* (warna utama, ikon, label) yang dipakai konsisten di seluruh laporan.

### Langkah 3 — Penyusunan Template (semantic-first)
Template HTML disusun dengan **prinsip semantik** — bukan dengan tabel layout 1990-an. Struktur logis dari atas ke bawah:
1. **Header eksekutif** — nama aplikasi, judul laporan, timestamp, status badge besar.
2. **Ringkasan eksekutif** — *card grid* berisi 4–6 metrik utama: durasi, mode, total rows, success rate, jumlah error.
3. **Detail koneksi** — host & database source/target, file mapping yang dipakai. Password dimasking (`****`).
4. **Statistik data** — tabel atau visualisasi sederhana berbasis CSS (bar progress, donut sederhana berbasis `conic-gradient` jika perlu — tetap *standalone*, tidak boleh JS framework eksternal).
5. **Detail error / anomali** — tabel terperinci dengan kolom: kategori, kolom terdampak, baris (PK), nilai mentah, pesan teknis. Setiap baris error punya *severity badge* sendiri.
6. **Blok rekomendasi solutif** — dikelompokkan per kategori anomali, disajikan sebagai *callout box* yang menonjol (border kiri tebal berwarna sesuai severity).
7. **Footer** — metadata environment dan tautan/petunjuk untuk operator (cara menjalankan ulang, di mana checkpoint terakhir tersimpan).

Tema visual harus profesional namun ringan: tipografi sistem (`-apple-system`, `Segoe UI`, `Inter`, dst), palet warna terbatas (1 warna utama + 3 warna status: hijau / kuning / merah / biru), dan whitespace yang murah hati. Hindari ikon eksternal — gunakan karakter Unicode atau glyph CSS sederhana.

### Langkah 4 — Standalone Embedding (TANPA dependency runtime)
Laporan HTML wajib **standalone**: dibuka di browser mana pun, tanpa internet, tanpa file pendamping. Konsekuensi teknis:
- Seluruh CSS ditanam di dalam tag `<style>` di `<head>`. Tidak ada `link rel=stylesheet`.
- Bila perlu sedikit interaktivitas (toggle detail error, filter kategori), gunakan JavaScript inline murni — **dilarang** menyertakan jQuery, React, atau framework apa pun.
- Ikon/logo (jika ada) di-encode sebagai *data URI* (Base64) atau diganti dengan glyph Unicode.
- Font menggunakan font system stack agar laporan tetap konsisten lintas OS tanpa harus mengunduh font.

### Langkah 5 — Penyimpanan File
File HTML disimpan ke direktori output dengan konvensi penamaan yang **tidak ambigu** dan mudah di-sort kronologis:
- Direktori default: `reports/` di root proyek (sudah ditambahkan ke `.gitignore` agar laporan tidak mencemari repository git).
- Format nama file: `[mode]_[nama_tabel]_[YYYYMMDD-HHMMSS].html` — contoh tekstual: `dry-run_users_20260429-153012.html`, `real-sync_orders_20260429-201145.html`.
- Apabila mode multi-table aktif, gunakan satu file induk dengan nama `[mode]_batch_[YYYYMMDD-HHMMSS].html` yang merangkum seluruh tabel di dalam satu dokumen (tab/section per tabel).
- Path absolut file yang dihasilkan **wajib** dipublikasikan kembali ke event bus (event tipe `REPORT_GENERATED`) sehingga TUI dapat menampilkan notifikasi "Laporan tersimpan di …" di akhir job.

### Langkah 6 — Integrasi ke Pipeline Eksisting (hook, bukan rewrite)
Aturan integrasi yang ketat:
- Generator HTML **tidak boleh** dipanggil dari dalam orchestrator atau ETL pipeline secara langsung. Ia hanya berlangganan ke event bus.
- Generator dijalankan **setelah** event `JOB_COMPLETED` (atau `JOB_ABORTED`, atau `DRY_RUN_FINISHED`) diterima — bukan di tengah job.
- Kegagalan saat menghasilkan laporan (mis. disk penuh, permission denied) **dilarang** memengaruhi status job utama. Kegagalan generator dicatat di log, tetapi job yang sudah `COMPLETED` tetap `COMPLETED`.
- Generator harus *idempotent*: memanggil ulang dengan data yang sama menghasilkan file dengan timestamp baru, tidak menimpa file lama.

### Langkah 7 — Mode Dry Run Highlight (treatment khusus)
Karena Dry Run rentan disalahpahami sebagai Real Sync, laporan untuk mode ini **wajib** memiliki perlakuan visual ekstra:
- Banner peringatan tebal di atas header eksekutif: "MODE SIMULASI — TIDAK ADA DATA YANG DITULIS KE TARGET".
- Watermark diagonal samar di latar belakang setiap halaman dengan teks "DRY RUN" (CSS `transform: rotate`).
- Bagian "Statistik Data" mengganti label "Berhasil Disimpan" menjadi "Lolos Validasi", dan menyembunyikan metrik commit yang tidak relevan.
- Blok rekomendasi mendapat porsi yang lebih besar dibanding mode Real Sync, karena tujuan utama Dry Run memang menemukan masalah sebelum produksi.

## ✅ Kriteria Penerimaan (Acceptance Criteria)
- [ ] Direktori `reports/` sudah terdaftar di `.gitignore`, dan modul generator membuat direktori tersebut secara otomatis bila belum ada.
- [ ] Setelah job Real Sync selesai dengan sukses, sebuah file HTML standalone tersimpan di `reports/` dengan nama yang mengandung mode, nama tabel, dan timestamp.
- [ ] Setelah job Real Sync gagal (abort di tengah atau ada baris yang `ROLLBACK`), laporan tetap tersimpan dengan status badge merah/kuning dan tabel error terisi lengkap.
- [ ] Setelah Dry Run selesai, laporan menampilkan banner peringatan dominan "MODE SIMULASI" dan watermark "DRY RUN", sehingga pembaca tidak mungkin keliru menganggapnya sebagai Real Sync.
- [ ] Laporan menampilkan **perbedaan visual yang jelas** antara mode Dry Run (palet biru, banner peringatan) dan Real Sync (palet hijau/merah sesuai status).
- [ ] Laporan menyertakan blok rekomendasi yang dapat ditindaklanjuti untuk setiap kategori anomali yang terdeteksi (mis. saran perubahan pada YAML mapping atau pada skema target).
- [ ] File HTML benar-benar *standalone*: dibuka di browser tanpa koneksi internet, tanpa file pendamping, dan seluruh CSS/asset tertanam di dalamnya.
- [ ] Password database **tidak pernah** muncul di laporan; field password dimasking dengan karakter pengganti.
- [ ] Kegagalan saat menghasilkan laporan (disk penuh, permission, dll.) tidak mengubah status akhir job utama; kegagalan ini tercatat di log namun job tetap dianggap selesai.
- [ ] Path file laporan yang baru dihasilkan dipublikasikan ke event bus sehingga TUI menampilkan notifikasi lokasi penyimpanan kepada operator.
- [ ] Mode Multi-Table menghasilkan **satu file induk** yang memuat ringkasan semua tabel, bukan banyak file terpisah yang membingungkan.
- [ ] Tersedia smoke test yang memvalidasi: (a) file HTML berhasil ter-generate untuk dataset dummy; (b) struktur HTML mengandung penanda mode (Dry Run vs Real Sync) yang benar; (c) tidak ada string password mentah yang bocor di output.

## 🤖 SOP Eksekusi (Wajib Dibaca)
**PENTING: Sebelum mengeksekusi penulisan kode untuk task ini, Anda wajib mencari referensi terbaru. Ikuti urutan prioritas berikut:**

1. **JALAN PERTAMA: `/graphify query`** — Gunakan selalu untuk pemindaian file atau mencari logika aplikasi. Hindari pemindaian file secara rekursif (`find`, `ls -R`, dll). Pertanyaan awal yang wajib dijawab: di mana orchestrator menandai akhir job? di mana DryRunEngine menyerahkan laporannya? bagaimana event bus dipakai konsumer eksisting?
2. **JALAN KEDUA: `context7`** — Selalu utamakan `context7` untuk mendapatkan *best practice*, dokumentasi library Python mutakhir (mis. `jinja2`, `dataclasses`, modul standar `html`), dan pola optimasi agar kode yang dihasilkan *up-to-date*, aman, dan berkinerja tinggi. Tanyakan secara spesifik, bukan keyword tunggal.
3. **JALAN KETIGA: Pencarian Internet** — Gunakan pencarian internet hanya jika `context7` tidak memberikan informasi yang cukup, terutama untuk inspirasi desain visual laporan HTML modern (palet warna status, layout *executive summary card*).
