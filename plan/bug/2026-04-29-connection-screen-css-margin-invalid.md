# Bug Report: Kegagalan Inisialisasi TUI `sync-mail` Akibat Nilai `auto` pada Properti `margin` di Stylesheet ConnectionScreen

- **Tanggal Laporan:** 2026-04-29
- **Pelapor:** Senior Software Architect (otonom debug session)
- **Komponen Terdampak:** Lapisan presentasi TUI (Textual) — blok stylesheet `ConnectionScreen` di dalam App utama
- **Tingkat Keparahan:** Tinggi (Blocker) — aplikasi gagal start, seluruh alur konfigurasi koneksi dan migrasi tidak dapat diakses
- **Status:** Open / Belum diperbaiki
- **Lingkup:** Hanya menyentuh definisi stylesheet aplikasi pada layar koneksi yang baru ditambahkan. Tidak menyentuh logika ekstraksi, transformasi, pemuatan data, maupun checkpoint resume.
- **Hubungan dengan laporan terdahulu:** Merupakan regresi setelah laporan `2026-04-29-sync-mail-error.md` (cacat border `thin`/`sunken`) — perbaikan sebelumnya menyelesaikan keluhan parser pada properti `border`, namun penambahan blok layar koneksi memperkenalkan satu kelas keluhan baru pada properti `margin`.

---

## 🤖 SOP Eksekusi (Wajib Dibaca Sebelum Patch)

**PENTING: Sebelum mengeksekusi penulisan kode untuk task ini, Anda wajib mencari referensi terbaru. Ikuti urutan prioritas berikut:**

1. **JALAN PERTAMA: `/graphify query`** — Gunakan selalu untuk pemindaian file atau mencari logika aplikasi. Hindari pemindaian rekursif (`find`, `ls -R`, dll).
2. **JALAN KEDUA: `context7`** — Selalu utamakan `context7` untuk mendapatkan dokumentasi resmi Textual mutakhir, terutama daftar nilai legal untuk properti tata letak agar regresi serupa tidak terulang.
3. **JALAN KETIGA: Pencarian Internet** — Gunakan pencarian internet hanya jika `context7` tidak memberikan informasi yang cukup.

---

## 1. Ringkasan Eksekutif

Saat perintah peluncur `sync-mail` dijalankan, framework TUI Textual menolak untuk mengaktifkan App karena parser CSS-nya menemukan satu nilai pada properti `margin` yang berada di luar tipe data yang sah. Akibatnya proses inisialisasi App terhenti sebelum layar manapun sempat dirender, sehingga seluruh alur — mulai dari pengisian form koneksi YAML interaktif, introspeksi skema, peluncuran migrasi, hingga inspeksi data — menjadi tidak dapat dipakai. Ini adalah cacat presentasi murni; pipeline data inti tidak terpengaruh secara langsung tetapi tidak akan pernah terjangkau selama bug ini terbuka.

## 2. Cara Reproduksi

1. Berada pada direktori proyek `sync-mail`.
2. Menjalankan binary peluncur tanpa argumen tambahan.
3. Aplikasi langsung gagal dengan satu blok galat parsing stylesheet sebelum layar pertama dirender.

Reproduksi bersifat deterministik: tidak bergantung pada keberadaan file `connection.yaml`, status koneksi database, atau isi YAML mapping. Galat terjadi murni pada tahap *bootstrap* TUI ketika parser stylesheet membaca atribut CSS kelas App utama.

## 3. Observasi Galat (Hasil Eksekusi)

Parser stylesheet Textual menerbitkan satu keluhan tunggal terhadap berkas yang sama:

- Lokasi keluhan diarahkan ke deklarasi `margin` pada selektor kontainer formulir koneksi (selektor identitas yang menampung form dua kolom Source dan Target).
- Nilai yang ditolak adalah pasangan dua-token: angka pada slot pertama (vertikal) dan kata kunci `auto` pada slot kedua (horizontal).
- Pesan parser secara eksplisit menyatakan bahwa `margin` hanya menerima 1, 2, atau 4 bilangan bulat yang dipisah spasi, dengan contoh sah `margin: 1`, `margin: 1 2`, dan `margin: 1 2 3 4`.
- Pesan akhir parser merangkum bahwa terdapat 1 kesalahan dalam stylesheet, sehingga inisialisasi App dibatalkan total.

Pesan galat ini berbeda dari laporan sebelumnya (yang menolak label tipe border tertentu): kali ini tipe data yang ditolak adalah keyword `auto` pada properti box-model, bukan label gaya garis tepi.

## 4. Pemindaian Arsitektur (Trace Dependensi)

Hasil pemetaan grafik pengetahuan proyek menunjukkan posisi sentral berkas yang gagal:

- **App TUI utama** adalah simpul pusat (god node) yang memuat stylesheet inline sebagai atribut kelas. Stylesheet tunggal ini berlaku untuk *semua* layar yang terdaftar — sehingga satu galat pada satu blok selektor membatalkan semua layar.
- **Layar yang terdaftar pada App** mencakup lima sub-layar: layar menu utama, layar introspeksi skema, layar pemantauan migrasi, layar inspeksi data, dan layar koneksi (yang baru ditambahkan oleh fitur konfigurasi YAML opsional).
- **Selektor bermasalah** adalah selektor kontainer formulir koneksi yang dimaksudkan untuk membungkus form input Source/Target di tengah layar. Selektor ini hanya direferensikan oleh layar koneksi, namun karena stylesheet bersifat global, parser tetap memvalidasinya saat App di-*bootstrap* terlepas apakah layar koneksi akan ditampilkan atau tidak.
- **Titik masuk CLI** memanggil App melalui fungsi peluncur tunggal. Karena App tidak pernah berhasil dimuat, titik masuk CLI tidak pernah mencapai fase pemeriksaan status konfigurasi koneksi (`VALID` / `MISSING_FILE` / `EMPTY_FILE` / `INVALID_FORMAT`), sehingga logika percabangan yang menentukan apakah layar koneksi perlu didorong ke atas layar menu pun tidak pernah dieksekusi.
- **Tes asap TUI** yang ada di rangkaian uji telah memvalidasi bahwa stylesheet sebelumnya bisa di-*mount*. Karena tes asap belum diperbarui untuk memuat layar koneksi setelah fitur baru ditambahkan, regresi ini lolos dari jaring pengaman uji.

## 5. Analisis Akar Masalah (Root Cause)

Akar masalah berlapis dua:

1. **Penyalahgunaan keyword `auto` pada properti `margin`.** Penulis stylesheet kemungkinan mengadaptasi pola umum dari CSS web (di mana `margin: <vertikal> auto` adalah idiom standar untuk memusatkan blok secara horizontal). Textual TIDAK mengadopsi keyword `auto` untuk properti `margin`. Berdasarkan dokumentasi resmi Textual mutakhir, properti `margin` hanya menerima 1, 2, atau 4 bilangan bulat (mewakili sel terminal), tanpa keyword pemusatan apapun.
2. **Strategi pemusatan yang salah secara idiom.** Idiom Textual untuk memusatkan kontainer di tengah layar bukan via `margin auto`, melainkan menggunakan properti `align` pada *parent* (umumnya `Screen` atau kontainer pembungkus) dengan nilai pemusatan horizontal/vertikal, dipadu dengan ukuran lebar yang ditentukan secara eksplisit pada anak (atau `width: auto` jika lebar mengikuti konten). Pendekatan ini memanfaatkan mesin tata letak Textual yang berbasis sel terminal, bukan model kotak HTML.

Faktor pendukung yang memperkuat dampak:

- **Stylesheet inline tunggal yang global.** Karena seluruh CSS App ditempelkan sebagai satu string besar pada kelas App, validasi parser terjadi sekali dan total. Tidak ada mekanisme isolasi per-layar yang memungkinkan layar lain tetap dapat berjalan saat satu blok rusak.
- **Kurangnya pemeriksaan otomatis terhadap kebenaran stylesheet.** Tes asap TUI yang ada memang mengecek instansiasi App, namun tidak diperbarui ketika layar koneksi baru ditambahkan. Akibatnya regresi stylesheet bisa di-*commit* tanpa mekanisme pencegah.

## 6. Dampak Logika

- **Dampak langsung pada pengguna akhir:** Aplikasi sama sekali tidak dapat dijalankan. Semua jalur fungsional (introspeksi, migrasi, inspeksi, konfigurasi koneksi) tertutup.
- **Dampak pada fitur baru "konfigurasi YAML koneksi opsional":** Fitur ini secara konseptual sudah selesai pada lapisan logika (resolver konfigurasi, status `VALID`/`MISSING_FILE`/`EMPTY_FILE`/`INVALID_FORMAT`/`*_INCOMPLETE`/`PARSE_ERROR`), namun pintu masuknya — yakni layar koneksi interaktif — tidak pernah dapat dirender. Manfaat fitur menjadi nol bagi pengguna sampai bug ini ditutup.
- **Dampak pada pipeline data:** Tidak ada kerusakan data, tidak ada batch yang setengah-jalan, tidak ada checkpoint yang korup. Pipeline tidak pernah dieksekusi karena App tidak pernah hidup. Risiko data integrity NIHIL.
- **Dampak pada operasional:** Selama bug ini tidak diperbaiki, satu-satunya cara menjalankan migrasi adalah melewati TUI sepenuhnya — yang saat ini belum tersedia sebagai jalur alternatif sah. Artinya proses migrasi terhenti total.
- **Dampak pada kualitas (regression risk):** Pola yang sama (`margin: <angka> auto`) dapat saja muncul lagi di layar baru yang ditambahkan ke depan jika tidak ada konvensi tertulis dan tidak ada gerbang uji.

## 7. Rencana Perbaikan Terstruktur

Perbaikan dipecah menjadi tiga lapisan dengan urutan eksekusi yang ketat: hentikan pendarahan dahulu, lalu pasang jaring pengaman, kemudian dokumentasikan konvensi.

### 7.1. Lapisan Perbaikan Utama (Wajib, Blocker)

1. **Hapus penggunaan keyword `auto` pada properti `margin`** di seluruh blok stylesheet App utama. Pencarian wajib mencakup *semua* selektor — bukan hanya selektor kontainer formulir koneksi — untuk menjamin tidak ada okurensi lain yang lolos.
2. **Ganti strategi pemusatan horizontal** kontainer formulir koneksi dengan idiom Textual yang sah:
   - Tetapkan `align` pada layar koneksi (sebagai *parent* langsung) dengan nilai pemusatan horizontal-vertikal.
   - Pertahankan `width` eksplisit pada kontainer formulir agar pemusatan terlihat (tanpa lebar pasti, layar akan merentangkan kontainer mengisi penuh).
   - Pertahankan `margin` vertikal (jika diinginkan jarak tepi atas/bawah) menggunakan bilangan bulat saja, atau gunakan properti spesifik `margin-top` / `margin-bottom`.
3. **Verifikasi parsing CSS** dengan menjalankan kembali peluncur TUI dan memastikan tidak ada keluhan parser pada *startup*. Verifikasi juga bahwa layar koneksi muncul ketika status konfigurasi adalah `MISSING_FILE`, `EMPTY_FILE`, `INVALID_FORMAT`, atau salah satu dari `*_INCOMPLETE`/`PARSE_ERROR`, dan tidak muncul ketika statusnya `VALID`.

### 7.2. Lapisan Pencegahan Regresi (Sangat Direkomendasikan)

4. **Perluas tes asap TUI** untuk secara eksplisit mendorong (mount) layar koneksi pada kondisi status konfigurasi yang tidak `VALID`. Tes asap harus gagal seketika jika ada keluhan parser stylesheet pada layar manapun yang terdaftar di App. Ini menutup celah yang membiarkan regresi sebelumnya lolos.
5. **Tambahkan satu pengecekan kebenaran stylesheet** di tahap awal pipeline uji (pre-flight): instansiasi App sekali, tangkap exception parsing, dan kegagalan apa pun di sini segera memblokir merge.
6. **Pertimbangkan refaktor stylesheet inline** menjadi berkas `.tcss` eksternal terpisah per layar (dengan path `CSS_PATH`). Manfaatnya: galat menjadi terlokalisir per layar dan tidak meledak global; berkas terpisah juga lebih mudah ditinjau dalam *code review*. Refaktor ini opsional tetapi strategis untuk mengurangi blast radius bug stylesheet di masa depan.

### 7.3. Lapisan Dokumentasi & Konvensi (Direkomendasikan)

7. **Dokumentasikan konvensi pemusatan Textual** dalam berkas panduan internal proyek (mis. tambahan singkat di `CLAUDE.md` atau dokumen panduan TUI) yang menyatakan secara eksplisit:
   - `margin` dalam Textual hanya menerima bilangan bulat — `auto` tidak ada.
   - Pemusatan dilakukan dengan `align: center middle` pada parent dipadu `width` eksplisit pada anak.
   - Setiap penambahan layar baru harus mencantumkan tes asap yang me-*mount* layar tersebut.
8. **Catat insiden pada pelacak isu Beads** sebagai bug terpisah dari laporan border sebelumnya, dengan tautan ke berkas laporan ini, agar histori regresi visual TUI dapat dirunut sebagai pola (bukan insiden tunggal).

## 8. Kriteria Penerimaan (Definition of Done)

- Peluncuran TUI berjalan tanpa galat parser stylesheet pada *startup*.
- Layar koneksi muncul saat status konfigurasi tidak `VALID` dan menampilkan banner status yang sesuai (`MISSING_FILE`, `EMPTY_FILE`, `INVALID_FORMAT`, `SOURCE_INCOMPLETE`, `TARGET_INCOMPLETE`, `BOTH_INCOMPLETE`, atau `PARSE_ERROR:...`).
- Form koneksi tampil terpusat secara horizontal di layar dengan jarak vertikal yang wajar dari tepi atas, tanpa bergantung pada keyword `auto`.
- Tes asap TUI mencakup *mount* eksplisit layar koneksi dan akan gagal jika regresi stylesheet serupa terjadi lagi.
- Tidak ada okurensi `margin: ... auto` yang tersisa di seluruh basis kode TUI.
- Dokumen konvensi internal diperbarui dengan aturan `margin` Textual.

## 9. Catatan Pasca-Perbaikan (Follow-Up Opsional)

- **Audit menyeluruh terhadap stylesheet App** untuk pola CSS web-isme lain yang mungkin tidak didukung Textual (mis. unit `px`, `%`, `em`; properti `display: flex`; pseudo-class yang tidak ada di Textual). Audit ini bisa dilakukan dalam satu tiket cleanup terpisah agar tidak memperpanjang scope perbaikan blocker ini.
- **Strategi penyimpanan kredensial** pada layar koneksi (saat ini password diisi via input bertopeng dan dipertahankan di memori App). Bahas terpisah karena menyangkut keamanan, bukan presentasi.

---

**Akhir laporan.**
