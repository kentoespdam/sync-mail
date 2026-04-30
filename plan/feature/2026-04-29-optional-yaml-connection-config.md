# Issue: 01 - Optional YAML Connection Configuration dengan Fallback Input Interaktif

## 🎯 Tujuan
Memberikan jalur konfigurasi koneksi database yang **opsional namun aman** bagi pengguna `sync-mail`. Pengguna yang sering menjalankan sinkronisasi cukup menyimpan kredensial sumber dan target sekali di file YAML khusus untuk mempercepat eksekusi (tanpa mengetik ulang setiap kali). Sebaliknya, pengguna yang baru mencoba aplikasi di environment baru — tanpa file YAML, tanpa Environment Variables — tetap dapat menjalankan aplikasi karena sistem akan **selalu** menyediakan jalur input interaktif di terminal sebagai cadangan. Aplikasi tidak boleh berhenti, crash, atau melempar error fatal hanya karena file konfigurasi koneksi belum ada atau kosong.

## 🔗 Dependensi
- **Issue 02 (Database Connection Manager)** dari rencana utama (`plan/claude/02-db-connection.md`) — modul `connection.py` yang membungkus PyMySQL `SSDictCursor` sudah tersedia dan menerima dictionary parameter DSN (host, port, user, password, database). Fitur ini hanya menambahkan **lapisan resolver** di depan factory koneksi tersebut, bukan mengubah cara koneksi dibuka.
- **Issue 04 (Mapping Loader & Validator)** — pola pembacaan YAML untuk mapping skema sudah ada. Loader untuk `connection.yaml` harus konsisten dengan gaya pembacaan YAML yang sudah dipakai (library YAML yang sama, error handling yang seragam), namun **harus dipisahkan secara file** dari mapping skema tabel. Satu file untuk skema, satu file lain untuk kredensial.

## 📝 Alur Kerja / Logika Sistem (Step-by-Step)

### Langkah 1: Pemisahan File Konfigurasi Koneksi
Sistem mengenali sebuah file konfigurasi koneksi khusus dengan nama default `connection.yaml`, terletak di root proyek (atau lokasi standar yang ditentukan satu kali, sejalan dengan konvensi mapping). File ini **terpisah** dari file YAML mapping skema tabel. Pemisahan ini wajib karena:
- File koneksi berisi kredensial sensitif (password database) yang tidak boleh tercampur dengan file mapping yang umumnya boleh di-commit ke repository.
- File koneksi punya siklus hidup berbeda: jarang berubah, sementara mapping bisa berubah setiap kali skema target berubah.

Struktur konseptual `connection.yaml` cukup memuat dua blok: blok `source` dan blok `target`. Setiap blok berisi kunci yang sama: alamat host, nomor port, nama user, password, dan nama database. Tidak ada kunci tambahan; tidak ada nested object yang aneh. Sederhana, beginner-friendly.

### Langkah 2: Mekanisme Pencarian dan Pembacaan File
Saat aplikasi dijalankan, modul resolver koneksi melakukan **tiga pengecekan berurutan**:
1. **Cek keberadaan file:** apakah `connection.yaml` ada di lokasi yang diharapkan?
2. **Cek isi file:** jika file ada, apakah isinya kosong (nol byte, atau hanya whitespace/komentar)?
3. **Cek kelengkapan blok:** jika file berisi sesuatu, apakah blok `source` dan `target` dengan semua field wajib (host, port, user, password, database) tersedia dan valid?

Hasil dari tiga cek ini menentukan jalur eksekusi:
- **Jalur A — File lengkap dan valid:** parameter koneksi langsung dipakai untuk membuka koneksi. Tidak ada interaksi dengan pengguna.
- **Jalur B — File tidak ada:** lompat ke Langkah 3 (TUI form koneksi).
- **Jalur C — File ada tetapi kosong:** lompat ke Langkah 3 (TUI form koneksi).
- **Jalur D — File ada tetapi sebagian field hilang/cacat:** sistem **tidak boleh diam-diam menambal** dengan nilai default untuk semua field, karena itu menyembunyikan bug konfigurasi. Sebaliknya, sistem tetap masuk ke TUI form koneksi (Langkah 3), tetapi field yang **sudah valid dari YAML di-prefill** dan field yang hilang/cacat ditandai/dikosongkan agar pengguna fokus melengkapinya. Jangan crash; jangan lanjut diam-diam.

### Langkah 3: Penyerahan ke TUI Form Koneksi (Tampilan Awal)
Jika resolver memutuskan butuh input dari pengguna (jalur B, C, atau D), sistem **tidak** menjalankan rangkaian prompt teks di terminal. Sebaliknya, aplikasi langsung membuka **tampilan awal TUI** yang memang sudah memuat form input koneksi (source + target). Aturan untuk alur ini:
- TUI form koneksi adalah satu-satunya jalur fallback. Tidak ada `input()`, `getpass()`, atau prompt baris perintah lain di luar TUI.
- **Jangan** menyentuh atau mencari Environment Variables (`.env`, `os.environ`). Jalur fallback eksklusif lewat form TUI. Ini eksplisit dari spesifikasi.
- Tampilkan **banner/notifikasi singkat** di dalam TUI yang menjelaskan kenapa form muncul (mis. "File `connection.yaml` tidak ditemukan — silakan isi detail koneksi di form ini.", atau "Field `target.host` tidak valid — silakan perbaiki di form ini.").
- Pada jalur D (file tidak lengkap), **prefill** field-field yang valid dari YAML ke kontrol form yang sesuai supaya pengguna tidak perlu mengetik ulang yang sudah benar; field yang hilang/cacat dibiarkan kosong (atau dengan default ramah seperti `localhost` / `3306`) dan diberi indikator visual agar mudah ditemukan.
- Validasi field (port harus angka, host tidak boleh kosong, password tidak ditampilkan) menjadi tanggung jawab kontrol form TUI; resolver hanya membaca hasilnya setelah pengguna menekan tombol "Connect"/"Submit".
- Setelah pengguna submit, TUI mengirim dictionary parameter koneksi yang **bentuknya identik** dengan output pembacaan YAML ke resolver, supaya factory koneksi di hilir tidak peduli dari mana data itu berasal.
- Opsional: TUI boleh menawarkan tombol "Save to connection.yaml" agar input dari form sekaligus tertulis ke file (dengan peringatan agar tidak commit file tersebut). Fitur penyimpanan ini bukan syarat utama issue; pastikan tidak menulis kredensial ke log.

### Langkah 4: Penanganan Konflik dengan Output Log Terminal
Aplikasi `sync-mail` punya logger yang bisa menulis ke stdout. Karena fallback dilakukan via TUI (Textual) yang mengambil alih layar, log stdout bukan lagi sumber utama konflik — namun tetap harus rapi. Aturan:
- Selama TUI form koneksi aktif (sebelum koneksi terbuka), **tunda atau senyapkan** handler stdout pada logger root agar tidak ada baris log mentah yang merusak rendering TUI. Logger boleh tetap menulis ke file log.
- Jika ada pesan yang relevan untuk pengguna selama fase ini, tampilkan via widget log/notifikasi di dalam TUI, bukan via `print` atau handler stdout.
- Setelah pengguna submit form dan TUI ditutup (atau berpindah ke mode operasi), kembalikan logger stdout ke perilaku normal.
- Test alur ini saat dijalankan via `uv run` atau runner lain yang membungkus stdout/stderr, karena beberapa runner ikut campur dengan buffer terminal dan dapat mengganggu rendering TUI.

### Langkah 5: Penyerahan ke Connection Manager
Setelah dictionary parameter koneksi terkumpul (entah dari YAML atau input terminal), data diserahkan ke factory koneksi yang sudah ada di Issue 02. Resolver **tidak** mengulang logika koneksi PyMySQL — ia hanya menyiapkan input. Pemisahan ini menjaga tanggung jawab tetap jelas: resolver bertugas mendapatkan kredensial; connection manager bertugas membuka koneksi.

### Langkah 6: Standar Keamanan File Konfigurasi
- **Daftarkan `connection.yaml` di `.gitignore`.** Tambahkan baris yang menyaring nama file koneksi (dan variannya seperti `*.connection.yaml` jika diperlukan) ke dalam `.gitignore` proyek. Tujuannya mencegah kebocoran kredensial ke history Git.
- **Sediakan `connection.example.yaml`.** Buat file contoh dengan struktur yang sama persis dengan `connection.yaml`, tetapi diisi dengan **nilai dummy yang jelas-jelas placeholder** (mis. host `your-db-host`, password `your-password-here`). File contoh ini **tidak** masuk `.gitignore` — justru sebaliknya, ia di-commit agar developer/pengguna baru tahu format yang diharapkan.
- Tambahkan catatan singkat di README/runbook (atau dokumen onboarding) yang menjelaskan: salin `connection.example.yaml` menjadi `connection.yaml`, isi dengan kredensial nyata, dan jangan pernah commit file `connection.yaml` yang sudah terisi.
- Sebelum aplikasi pertama kali menulis output apa pun yang berasal dari file koneksi, lakukan double-check di kode bahwa nama file koneksi sudah tercantum di `.gitignore`. Jika tidak, tampilkan **warning ramah** ke terminal yang menyarankan pengguna menambahkannya. Ini bukan error fatal, hanya pengingat keamanan.

### Langkah 7: Logging Kejadian Konfigurasi (Tanpa Membocorkan Kredensial)
Catat di log informasi tentang **jalur mana** yang dipakai (file lengkap, file kosong, file tidak ada, file tidak lengkap), tetapi **jangan pernah** menulis nilai field koneksi ke log — bahkan host pun sebaiknya disamarkan menjadi placeholder umum. Tujuannya: log tetap berguna untuk debugging tanpa menjadi sumber kebocoran kredensial.

## ✅ Kriteria Penerimaan (Acceptance Criteria)

- [ ] **File ada dan valid:** Saat `connection.yaml` tersedia dan berisi blok `source` + `target` lengkap, aplikasi membuka koneksi tanpa menampilkan TUI form koneksi.
- [ ] **File tidak ada:** Saat `connection.yaml` tidak ada di lokasi yang diharapkan, aplikasi **tidak crash**, melainkan langsung membuka TUI tampilan awal dengan form koneksi (source + target) dan banner informatif yang menjelaskan alasannya.
- [ ] **File kosong:** Saat `connection.yaml` ada tetapi isinya kosong (atau hanya berisi komentar/whitespace), perilaku sama dengan kondisi file tidak ada — aplikasi langsung membuka TUI form koneksi tanpa error.
- [ ] **File tidak lengkap:** Saat `connection.yaml` hanya berisi blok `source` (target hilang) atau ada field yang kosong, TUI form muncul dengan field valid sudah ter-prefill dari YAML, field hilang/cacat ditandai, dan banner menjelaskan field mana yang bermasalah.
- [ ] **Tidak ada prompt teks:** Tidak ada `input()`, `getpass()`, atau prompt baris perintah lain yang muncul saat fallback. Satu-satunya jalur input adalah TUI form.
- [ ] **Tidak menyentuh `.env`:** Verifikasi bahwa kode resolver tidak membaca `os.environ` atau file `.env` saat fallback. Jalur fallback eksklusif lewat TUI form.
- [ ] **Password tersembunyi:** Field password di TUI form merender karakter yang diketik sebagai mask (mis. `•` atau `*`), tidak menampilkan plaintext.
- [ ] **Default ramah pengguna:** Field host dan port di TUI form sudah berisi default (`localhost` / `3306`) sehingga pengguna cukup melanjutkan tanpa mengisi ulang.
- [ ] **Pengamanan repository:** File `.gitignore` proyek memuat entri yang menyaring `connection.yaml`. File `connection.example.yaml` ada di repository, bisa di-commit, dan strukturnya identik dengan file asli (tetapi nilainya placeholder; termasuk field DSN scheme `mariadb+pymysql://`).
- [ ] **Tidak ada kebocoran log:** Log aplikasi (`logs/sync-mail.log` atau setara) tidak memuat nilai password, user, atau host nyata yang dimasukkan pengguna — hanya status jalur konfigurasi.
- [ ] **Tidak bentrok dengan logger:** Saat dijalankan dengan `uv run`, rendering TUI form tetap rapi dan tidak tertimpa baris log stdout.
- [ ] **Integrasi mulus:** Setelah TUI submit atau file diolah, hasilnya diteruskan ke connection manager (Issue 02) tanpa mengubah signature factory koneksi yang sudah ada.

## 🤖 SOP Eksekusi (Wajib Dibaca)
**PENTING: Sebelum mengeksekusi penulisan kode untuk task ini, Anda wajib mencari referensi terbaru. Ikuti urutan prioritas berikut:**

1. **JALAN PERTAMA: `/graphify query`** — Gunakan selalu untuk pemindaian file atau mencari logika aplikasi. Hindari pemindaian file secara rekursif (`find`, `ls -R`, dll).
2. **JALAN KEDUA: `context7`** — Selalu utamakan `context7` untuk mendapatkan *best practice*, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan *up-to-date*, aman, dan berkinerja tinggi.
3. **JALAN KETIGA: Pencarian Internet** — Gunakan pencarian internet hanya jika `context7` tidak memberikan informasi yang cukup.

**Prioritas riset untuk task ini:**
- Pola pembacaan YAML yang sudah dipakai di modul mapping (`PyYAML` atau `ruamel.yaml`) agar konsisten.
- Praktik mutakhir input password tersembunyi di terminal Python 3.14 (modul `getpass` atau alternatif modern).
- Cara menonaktifkan/menyenyapkan handler stdout pada logger Python sementara, lalu mengembalikannya tanpa kehilangan log file.
- Konvensi penulisan `.gitignore` untuk file kredensial dan pola `*.example.*` di proyek Python modern.
