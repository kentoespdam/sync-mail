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
- **Jalur B — File tidak ada:** lompat ke Langkah 3 (input interaktif).
- **Jalur C — File ada tetapi kosong:** lompat ke Langkah 3 (input interaktif).
- **Jalur D — File ada tetapi sebagian field hilang/cacat:** sistem **tidak boleh diam-diam menambal** dengan input interaktif untuk semua field, karena itu menyembunyikan bug konfigurasi. Sebaliknya, tampilkan pesan ramah ke pengguna yang menjelaskan field mana yang hilang/salah, lalu **jalankan input interaktif untuk seluruh blok yang bermasalah** (source saja, target saja, atau keduanya). Jangan crash; jangan lanjut diam-diam.

### Langkah 3: Graceful Fallback ke Input Interaktif Terminal
Jika resolver memutuskan butuh input interaktif (jalur B, C, atau D), sistem menampilkan rangkaian pertanyaan di terminal. Aturan untuk alur input ini:
- Tampilkan **header singkat** yang memberi tahu pengguna kenapa input interaktif muncul (mis. "File `connection.yaml` tidak ditemukan, silakan masukkan detail koneksi secara manual.").
- Tanyakan field satu per satu, dimulai dari blok `source`, lalu blok `target`. Urutannya: host → port → user → password → database.
- **Jangan** menyentuh atau mencari Environment Variables (`.env`, `os.environ`). Jalur fallback satu-satunya adalah input terminal langsung. Ini eksplisit dari spesifikasi.
- Untuk field password, gunakan mekanisme input yang **tidak menampilkan karakter** di layar (echo dimatikan). Konsep ini setara dengan cara `sudo` meminta password.
- Sediakan **default value** yang masuk akal untuk field non-sensitif (mis. host default `localhost`, port default `3306`) sehingga pengguna cukup menekan Enter untuk menerima nilai default.
- Validasi minimal di tempat: port harus angka, host tidak boleh string kosong. Jika input tidak valid, tampilkan pesan dan minta ulang field tersebut saja.
- Setelah seluruh field terkumpul, simpan ke struktur dictionary yang **bentuknya identik** dengan output pembacaan YAML, supaya factory koneksi di hilir tidak peduli dari mana data itu berasal.

### Langkah 4: Penanganan Konflik dengan Output Log Terminal
Aplikasi `sync-mail` punya logger yang bisa menulis ke stdout. Jika prompt input muncul **bersamaan** dengan log yang sedang ditulis, baris pertanyaan bisa "tertimpa" sehingga pengguna bingung apa yang harus diketik. Aturan:
- Selama fase resolver koneksi (sebelum koneksi terbuka), **tunda atau senyapkan** logger terminal agar tidak menulis ke stdout. Logger boleh tetap menulis ke file log.
- Setelah seluruh input selesai dan koneksi siap dibuka, kembalikan logger ke perilaku normal.
- Tujuannya: prompt interaktif menjadi satu-satunya hal yang muncul di stdout selama fase tanya-jawab.
- Test alur ini saat menjalankan via `uv run` atau perintah lain yang membungkus stdout, karena beberapa runner ikut campur dengan buffer terminal.

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

- [ ] **File ada dan valid:** Saat `connection.yaml` tersedia dan berisi blok `source` + `target` lengkap, aplikasi membuka koneksi tanpa menampilkan satu pun prompt interaktif di terminal.
- [ ] **File tidak ada:** Saat `connection.yaml` tidak ada di lokasi yang diharapkan, aplikasi **tidak crash**, melainkan menampilkan header informatif lalu meminta input host/port/user/password/database secara berurutan untuk source dan target.
- [ ] **File kosong:** Saat `connection.yaml` ada tetapi isinya kosong (atau hanya berisi komentar/whitespace), perilaku sama dengan kondisi file tidak ada — aplikasi langsung masuk mode interaktif tanpa error.
- [ ] **File tidak lengkap:** Saat `connection.yaml` hanya berisi blok `source` (target hilang) atau ada field yang kosong, aplikasi memberi tahu pengguna field mana yang bermasalah lalu meminta input untuk blok yang bermasalah saja.
- [ ] **Tidak menyentuh `.env`:** Verifikasi bahwa kode resolver tidak membaca `os.environ` atau file `.env` saat fallback. Jalur fallback eksklusif lewat input terminal.
- [ ] **Password tersembunyi:** Saat prompt password muncul, karakter yang diketik tidak terlihat di layar.
- [ ] **Default ramah pengguna:** Menekan Enter pada prompt host/port menerima default (`localhost` / `3306`) tanpa error.
- [ ] **Pengamanan repository:** File `.gitignore` proyek memuat entri yang menyaring `connection.yaml`. File `connection.example.yaml` ada di repository, bisa di-commit, dan strukturnya identik dengan file asli (tetapi nilainya placeholder).
- [ ] **Tidak ada kebocoran log:** Log aplikasi (`logs/sync-mail.log` atau setara) tidak memuat nilai password, user, atau host nyata yang dimasukkan pengguna — hanya status jalur konfigurasi.
- [ ] **Tidak bentrok dengan logger:** Saat dijalankan dengan `uv run`, prompt interaktif tetap terbaca jelas dan tidak tertimpa baris log lain.
- [ ] **Integrasi mulus:** Setelah input/file diolah, hasilnya diteruskan ke connection manager (Issue 02) tanpa mengubah signature factory koneksi yang sudah ada.

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
