# Bug Report: Kegagalan Inisialisasi TUI `sync-mail` Akibat Properti CSS Tidak Valid

- **Tanggal Laporan:** 2026-04-29
- **Pelapor:** Senior Software Architect (otonom debug session)
- **Komponen Terdampak:** Lapisan presentasi TUI (Textual)
- **Tingkat Keparahan:** Tinggi (Blocker) — aplikasi gagal start, seluruh alur migrasi tidak dapat diakses oleh pengguna
- **Status:** Open / Belum diperbaiki
- **Lingkup:** Hanya menyentuh definisi stylesheet aplikasi, tidak mengubah logika ETL inti

---

## 🤖 SOP Eksekusi (Wajib Dibaca)
**PENTING: Sebelum mengeksekusi penulisan kode untuk task ini, Anda wajib mencari referensi terbaru. Ikuti urutan prioritas berikut:**

1. **JALAN PERTAMA: `/graphify query`** — Gunakan selalu untuk pemindaian file atau mencari logika aplikasi. Hindari pemindaian file secara rekursif (`find`, `ls -R`, dll).
2. **JALAN KEDUA: `context7`** — Selalu utamakan `context7` untuk mendapatkan *best practice*, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan *up-to-date*, aman, dan berkinerja tinggi.
3. **JALAN KETIGA: Pencarian Internet** — Gunakan pencarian internet hanya jika `context7` tidak memberikan informasi yang cukup.

---

## 1. Ringkasan Eksekutif

Saat perintah peluncuran `sync-mail` dijalankan, framework TUI (Textual) menolak untuk mengaktifkan layar utama karena parser CSS-nya menemukan dua nilai properti `border` yang tidak terdaftar di dalam himpunan tipe border yang sah. Akibatnya proses inisialisasi aplikasi terhenti sebelum sempat menampilkan menu, sehingga seluruh fungsi yang ada di balik antarmuka (introspeksi skema, peluncuran migrasi, dan inspeksi data) menjadi tidak dapat dipakai. Ini adalah cacat presentasi murni — bukan masalah pada pipeline ekstraksi, transformasi, atau pemuatan data.

## 2. Cara Reproduksi

1. Berada pada direktori proyek `sync-mail`.
2. Menjalankan binary peluncur (`uv run sync-mail`) tanpa argumen tambahan.
3. Aplikasi langsung gagal dengan dua blok galat parsing stylesheet sebelum layar pertama dirender.

Reproduksi bersifat deterministik: tidak bergantung pada koneksi database, isi YAML mapping, atau ukuran data — kegagalan terjadi murni pada tahap *bootstrap* TUI.

## 3. Observasi Galat (Hasil Eksekusi)

Parser stylesheet Textual menerbitkan dua keluhan paralel terhadap berkas yang sama:

1. **Keluhan pertama** menunjuk pada deklarasi border untuk panel metrik di dalam grid metrik. Nilai border yang ditolak adalah label *"thin"*. Parser menyatakan nilai ini bukan anggota daftar tipe border yang dikenali.
2. **Keluhan kedua** menunjuk pada deklarasi border untuk panel log. Nilai border yang ditolak adalah label *"sunken"*. Parser menyatakan nilai ini juga tidak ada di dalam daftar tipe border yang sah.

Keluaran parser secara eksplisit menyebutkan daftar nilai legal yang dikenali: rangkaian gaya seperti *ascii, blank, block, dashed, double, heavy, hidden, hkey, inner, none, outer, panel, round, solid, tab, tall, thick, vkey, wide*. Pesan akhir parser merangkum bahwa terdapat dua kesalahan dalam stylesheet, sehingga inisialisasi App dibatalkan.

## 4. Pemindaian Arsitektur (Trace Dependensi)

Hasil pemetaan grafik pengetahuan proyek menunjukkan posisi sentral berkas yang gagal:

- **Aplikasi inti TUI** adalah *god node* di sekitar definisi App utama. Stylesheet yang bermasalah ditempelkan langsung sebagai atribut kelas pada App tersebut, bukan dalam berkas eksternal terpisah.
- **Layar-layar (Screens) yang terdaftar** di App induk mencakup empat sub-layar: layar menu utama, layar introspeksi skema, layar pemantauan migrasi (yang merupakan sub-layar paling kompleks dan terhubung ke event bus, log panel, batch progress, dan migration progress), serta layar inspeksi data.
- **Widget pendukung** seperti panel log kustom, indikator kemajuan migrasi, dan indikator kemajuan batch, secara visual mengandalkan aturan border global yang didefinisikan oleh App induk.
- **Titik masuk CLI** memanggil App ini melalui fungsi peluncur tunggal. Karena App tidak pernah berhasil dimuat, titik masuk CLI tidak pernah mencapai fase pemuatan konfigurasi YAML, koneksi database, maupun orkestrator pipeline.

Implikasi penting: meskipun cacat berlokasi di lapisan paling tipis (CSS dalam-class), efek blastnya menutup seluruh permukaan interaksi pengguna karena App induk adalah pintu satu-satunya ke semua sub-layar.

## 5. Analisis Akar Masalah (Root Cause Analysis)

Akar masalahnya adalah **ketidakcocokan kosakata gaya border** antara harapan penulis stylesheet dan kontrak yang ditegakkan oleh parser Textual versi yang dipakai proyek:

1. **Kasus *thin*** — Nilai *thin* memang dikenal dalam ekosistem Textual, tetapi sebagai nilai sah untuk properti **keyline** (garis pemisah tipis pada container vertical/horizontal), bukan untuk properti **border**. Penulis kemungkinan terbawa intuisi CSS web atau sistem desain lain yang mempunyai konsep *thin border*, padahal di Textual border tidak memiliki tingkat ketebalan generik bernama *thin*; yang setara secara visual adalah *solid*, *round*, atau *ascii*.
2. **Kasus *sunken*** — Nilai *sunken* sama sekali tidak ada di tabel tipe border Textual. Ini mengikuti gaya CSS klasik desktop (mis. CSS2 untuk web) yang memang mengenal *inset/outset/groove/ridge/sunken*. Kontrak Textual memilih kosakata yang berbeda: jika tujuan visualnya adalah memberi kesan area yang "tertanam" atau panel sekunder, alternatif yang sah adalah *panel*, *inner*, atau *heavy* dengan warna teredam.

Kedua kesalahan ini lolos dari review karena Python tidak melakukan validasi statis terhadap isi string CSS — kesalahan baru muncul saat parser dijalankan pada saat *bootstrap* App. Tidak ada test asap (smoke test) yang mengeksekusi App sampai siklus *mount* sehingga parser tidak pernah dipicu di pipeline pemeriksaan kualitas.

Kategori cacat: **kesalahan kontrak antarmuka (interface contract violation)** pada lapisan presentasi, bersifat deklaratif (tidak ada cabang logika yang salah), dan deterministik (selalu gagal di kondisi yang sama).

## 6. Dampak terhadap Logika Aplikasi

- **Dampak fungsional langsung**: tidak ada layar yang dapat dimuat; pengguna tidak bisa menjalankan operasi introspeksi, migrasi, ataupun inspeksi.
- **Dampak terhadap pipeline ETL**: tidak ada — kode pipeline (ekstraktor server-side cursor, transformer, loader bulk, orkestrator multi-tabel, manajer checkpoint) tidak pernah dieksekusi. Tidak ada risiko data korup, transaksi setengah jadi, atau status state inkonsisten karena App gagal sebelum membuka koneksi database.
- **Dampak terhadap state.json / checkpoint**: nihil; tidak ada penulisan state.
- **Dampak terhadap pengalaman onboarding pengguna baru**: tinggi — aplikasi tampak rusak total dari sudut pandang pengguna meskipun seluruh logika data-plane sebenarnya sehat.
- **Dampak terhadap kepercayaan terhadap rilis**: signifikan, karena kegagalan terjadi pada *first-run smoke* yang seharusnya menjadi pengalaman paling halus.

## 7. Rencana Perbaikan Terstruktur

Perbaikan dilakukan secara berlapis: koreksi langsung pada stylesheet, pengerasan agar tidak terulang, dan dokumentasi konvensi gaya.

### 7.1 Perbaikan Konseptual pada Stylesheet
- Mengganti dua nilai border tidak sah dengan padanan visual yang setara dan resmi:
  - *thin* di panel metrik diganti dengan tipe border ringan yang resmi (mis. solid atau round dengan warna primer redup) untuk mempertahankan kesan pemisah tipis di antar sel grid.
  - *sunken* di panel log diganti dengan tipe border yang dirancang Textual untuk area sekunder atau kontainer "panel" (mis. panel atau inner) sehingga tetap memberi kesan area pasif yang menerima konten dinamis.
- Menyelaraskan palet warna border dengan token tema yang sudah ada (warna primer dan aksen) agar tampilan konsisten lintas layar.
- Memastikan bahwa setiap deklarasi border yang muncul di App induk tidak menabrak aturan border lokal di masing-masing screen/widget.

### 7.2 Pengerasan agar Tidak Terulang
- Menambahkan smoke test khusus TUI yang menginstansiasi App, memicu siklus mount, dan memverifikasi bahwa parser stylesheet tidak menerbitkan error. Test ini tidak perlu menggambar UI; cukup memastikan App dapat dibangun tanpa exception.
- Memindahkan stylesheet besar dari atribut kelas in-line menjadi berkas .tcss eksternal sehingga lebih mudah ditinjau, dilint, dan didukung oleh tooling Textual (mis. devtools / hot-reload). Ini juga membuka peluang untuk linting stylesheet tersendiri.
- Menambahkan checklist pre-merge yang mengharuskan menjalankan smoke test TUI sebelum perubahan apa pun pada lapisan presentasi disetujui.

### 7.3 Dokumentasi & Konvensi
- Menyusun panduan singkat di dokumen internal yang menyebutkan kosakata border resmi Textual (daftar nilai sah) dan padanan visual untuk istilah yang biasa dibawa pengembang dari ekosistem CSS web (mis. *thin* → solid/round, *sunken* → panel/inner, *ridge/groove* → tidak ada padanan langsung).
- Menambahkan catatan di pedoman kontribusi bahwa setiap nilai gaya yang tampak "umum CSS" wajib diverifikasi terhadap dokumentasi Textual versi yang dipakai proyek, karena Textual mempunyai kosakata properti yang independen dan terus berkembang.
- Mencatat keputusan ini di runbook sebagai preseden bila muncul ketidaksesuaian serupa di properti lain (mis. layout, scrollbar, keyline).

### 7.4 Verifikasi Pasca Perbaikan
- Menjalankan kembali peluncur TUI dan memastikan App berhasil masuk ke layar menu tanpa pesan parser.
- Menelusuri secara manual setiap layar (menu, introspeksi, migrasi, inspeksi) untuk memastikan border baru tampil sesuai maksud desain dan tidak ada regresi visual pada widget log, progress migrasi, dan progress batch.
- Menambahkan smoke test ke set pemeriksaan rutin agar regresi serupa terdeteksi otomatis di masa depan.

## 8. Risiko & Pertimbangan Lanjutan

- **Risiko low-blast lain di stylesheet yang sama**: karena dua nilai sudah terbukti salah, tidak menutup kemungkinan ada properti lain di stylesheet App induk maupun screen-level yang mengandung kosakata pinjaman dari CSS web. Tinjauan menyeluruh terhadap seluruh deklarasi border, outline, layout, dan scrollbar disarankan dalam satu sapuan yang sama.
- **Risiko regresi visual**: pergantian *sunken* ke *panel* atau *inner* akan mengubah kesan kedalaman pada panel log; pemilihan akhir sebaiknya dievaluasi bersama desainer atau pemilik produk agar tetap selaras dengan keseluruhan bahasa visual aplikasi.
- **Pertimbangan tema gelap/terang**: nilai warna primer/aksen sudah berbasis token tema, sehingga selama hanya tipe border yang diganti, dukungan multi-tema tetap berjalan tanpa perubahan tambahan.

## 9. Tindak Lanjut yang Disarankan

1. Membuka issue di pelacak Beads dengan tipe *bug*, prioritas tinggi, dan menautkan dokumen ini sebagai design reference.
2. Memutuskan apakah perbaikan dirilis sebagai patch terpisah atau digabungkan dengan upaya pemindahan stylesheet ke berkas `.tcss` eksternal.
3. Menambahkan smoke test TUI ke pipeline pra-rilis sebelum perbaikan ini dianggap selesai.
4. Memperbarui knowledge graph proyek (`graphify update .`) setelah perbaikan diterapkan agar peta dependensi tetap mencerminkan keadaan kode terkini.
