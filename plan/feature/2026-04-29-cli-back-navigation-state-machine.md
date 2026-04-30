# Issue: 03 - Pembuatan State Machine & Fitur Navigasi Back CLI

## 🎯 Tujuan

Menyeragamkan pengalaman navigasi pada antarmuka TUI `sync-mail` dengan menghadirkan fitur "Back" (Kembali) berbasis pola arsitektur *State Machine* / *Navigation Stack*. Fitur ini memberi pengguna kemampuan untuk membatalkan langkah saat ini dan mundur tepat satu langkah ke layar sebelumnya secara terurut, tanpa kehilangan data input yang telah dimasukkan. Tujuan akhirnya adalah menghasilkan alur interaksi yang konsisten di seluruh layar interaktif (Connection, Introspect, Inspect, Migrate, Dry-Run, dan setiap *prompt* turunannya), serta mencegah munculnya *spaghetti code* akibat penanganan transisi maju-mundur yang tersebar di banyak tempat. Layar awal (Menu Utama) dikecualikan secara eksplisit karena merupakan akar pohon navigasi.

## 🔗 Dependensi

- Fitur konfigurasi koneksi YAML opsional dan layar interaktifnya, yang memperkenalkan pola layar ber-*prompt* berurutan dan menjadi konsumen utama mekanisme back-navigation.
- Arsitektur lima layar TUI (Menu, Connection, Introspect, Inspect, Migrate) yang sudah didefinisikan dalam dokumentasi proyek; semua layar non-menu wajib menjadi peserta state machine.
- Konvensi gaya CSS Textual proyek (alignment via `align` + `width`, larangan `margin: auto`) yang harus tetap dihormati ketika label instruksi "Back" ditambahkan ke setiap layar.
- Smoke test TUI yang sudah ada — setiap layar partisipan navigasi membutuhkan pembaruan pengujian untuk memvalidasi transisi maju dan mundur.

## 📝 Alur Kerja / Logika Sistem (Step-by-Step)

### 1. Pemodelan Riwayat Navigasi sebagai *Stack*

- Bentuk satu komponen logis tunggal yang berperan sebagai *Navigation Controller*. Komponen ini menyimpan struktur data tumpukan (LIFO) berisi entri-entri "langkah" yang pernah dikunjungi pengguna.
- Setiap entri dalam tumpukan terdiri dari dua bagian konseptual: (a) identitas langkah (misalnya "pilih sumber koneksi", "isi host database target", "konfirmasi tabel yang akan diintrospeksi"), dan (b) muatan data input yang telah dikumpulkan sampai langkah tersebut.
- Akar tumpukan selalu berisi entri Menu Utama dan tidak pernah dapat di-*pop*. Dengan demikian, syarat "Menu Utama tidak memiliki tombol Back" terpenuhi by-design: ketika tumpukan hanya berisi satu entri, sistem tahu bahwa aksi mundur tidak relevan.

### 2. Transisi Maju (Forward Transition)

- Setiap kali pengguna menyelesaikan satu *prompt* atau memilih opsi yang membuka layar baru, *Navigation Controller* melakukan dua hal berurutan: pertama menyimpan kembali muatan data terkini ke entri saat ini (snapshot), kemudian melakukan *push* entri baru yang merepresentasikan langkah berikutnya.
- Layar berikutnya membaca entri puncak untuk merender dirinya. Bila muatan data untuk layar tersebut sudah pernah ada (akibat pengguna sebelumnya pernah maju lalu mundur), nilai-nilai itu langsung dijadikan *pre-fill* pada elemen input.

### 3. Transisi Mundur (Backward Transition Bertahap)

- Pada setiap layar partisipan, sistem menampilkan instruksi yang jelas — contoh frasa di bawah label input: *"Ketik B lalu tekan Enter untuk kembali ke langkah sebelumnya."* Instruksi ini wajib hadir, kecuali pada Menu Utama.
- Penangkapan input "B"/"b" dilakukan di lapisan validasi awal sebelum input diperlakukan sebagai data domain. Validator memeriksa string yang diketik pengguna; bila — setelah dipangkas spasi — bernilai persis satu karakter "B" tanpa memandang besar/kecil huruf, input tersebut TIDAK dianggap sebagai nilai field melainkan sebagai sinyal navigasi.
- Sinyal navigasi diteruskan ke *Navigation Controller*. Controller menjalankan urutan: (a) menyimpan snapshot data terbaru pada entri saat ini agar tidak hilang, (b) melakukan *pop* satu entri dari tumpukan, (c) memerintahkan layar baru di puncak untuk merender ulang dirinya menggunakan snapshot yang tersimpan.
- Aturan "tepat satu langkah" berarti satu kali penekanan "B" hanya melakukan satu *pop*. Untuk mundur lebih jauh, pengguna harus menekan "B" berulang kali. Tidak ada jalan pintas langsung ke Menu Utama melalui tombol Back.

### 4. Penyimpanan State (State Retention)

- Snapshot data tiap entri tinggal di dalam memori sesi *runtime* aplikasi. Tidak diperlukan persistensi ke disk untuk fitur ini — siklus hidup snapshot identik dengan siklus hidup proses TUI.
- Saat pengguna mundur, layar yang dirender ulang harus mengisi semua *widget* input dengan nilai yang tersimpan, baik berupa teks bebas (host, port, username), pilihan tabel, maupun parameter ukuran batch. Tidak ada *reset* otomatis pada saat back.
- Saat pengguna kembali maju dari titik tersebut, jika ia mengubah nilai, snapshot pada entri yang berada "di atas" titik perubahan dianggap kedaluwarsa dan dibuang. Hal ini mencegah ketidakkonsistenan ketika pengguna memutuskan jalur baru di tengah alur.

### 5. Re-render & *Clean Clear-Screen*

- Karena Textual mengelola *compositing* layar sendiri, transisi mundur diimplementasikan sebagai pergantian *screen* aktif, bukan sebagai pencetakan ulang teks ke terminal. Dengan begitu tidak akan muncul *artifact* berupa baris ganda atau sisa label dari layar sebelumnya.
- Kontrak setiap layar adalah: satu kali dipasang ulang, layar bertanggung jawab menggambar penuh tampilan dirinya, termasuk header, instruksi navigasi (kecuali Menu Utama), area input, dan label bantuan. Tidak diperbolehkan menyisakan *widget* milik layar terdahulu di luar lifecycle layar saat ini.
- Setiap label instruksi "Back" diletakkan pada area konsisten — direkomendasikan tepat di bawah area input atau di sisi kanan footer layar — agar pengguna dengan mudah mengenalinya tanpa perlu mempelajari pola berbeda di tiap layar.

### 6. Kontrak Antarmuka Logika antar Komponen

- Setiap layar memperlakukan *Navigation Controller* sebagai satu-satunya otoritas perpindahan layar. Layar TIDAK boleh memanggil layar lain secara langsung.
- Setiap layar mengekspos dua tanggung jawab konseptual: (a) "berikan snapshot data milikmu saat ini" — diminta oleh controller sebelum *push*/*pop*, (b) "isikan dirimu dari snapshot ini" — dipanggil oleh controller setelah *pop*.
- Dengan kontrak ini, penambahan layar baru di masa depan cukup mengimplementasikan dua tanggung jawab tersebut, tanpa perlu memodifikasi logika navigasi inti.

## ✅ Kriteria Penerimaan (Acceptance Criteria)

- [ ] Pengguna dapat mengetikkan "B" atau "b" untuk kembali ke menu tepat sebelumnya (kecuali layar awal/Menu Utama, yang tidak menampilkan instruksi Back).
- [ ] Penekanan satu kali tombol Back mundur tepat satu langkah, bukan langsung ke Menu Utama, di seluruh alur (Connection, Introspect, Inspect, Migrate, Dry-Run, dan *prompt* turunannya).
- [ ] Data input dari langkah sebelumnya berhasil dipertahankan di memori sesi (tidak ter-reset otomatis) dan ter-*pre-fill* saat pengguna mundur ke layar tersebut.
- [ ] Karakter "B"/"b" dikenali sebagai sinyal navigasi terlepas dari spasi di sekelilingnya, dan TIDAK pernah disimpan sebagai nilai field domain.
- [ ] Transisi antarmuka terminal tidak meninggalkan *artifact* teks ganda; setiap layar baru tampil sebagai *clean screen* tanpa sisa elemen dari layar sebelumnya.
- [ ] Menu Utama secara eksplisit tidak menampilkan instruksi "Back" dan tidak pernah dapat di-*pop* dari tumpukan navigasi.
- [ ] Smoke test TUI mencakup skenario: maju ke layar berikutnya, tekan "B", pastikan layar sebelumnya yang dirender, dan pastikan nilai input sebelumnya masih ada.
- [ ] Mengubah nilai input setelah mundur lalu maju kembali menyebabkan snapshot pada langkah-langkah di atas titik perubahan dibuang, sehingga tidak terjadi *state* yang saling bertentangan.

## 🤖 SOP Eksekusi (Wajib Dibaca)

**PENTING: Sebelum mengeksekusi penulisan kode untuk task ini, Anda wajib mencari referensi terbaru. Ikuti urutan prioritas berikut:**

1. **JALAN PERTAMA: `/graphify query`** ➔ Gunakan selalu untuk pemindaian file atau mencari logika aplikasi. Hindari pemindaian file secara rekursif (`find`, `ls -R`, dll).
2. **JALAN KEDUA: `context7`** ➔ Selalu utamakan `context7` untuk mendapatkan *best practice*, dokumentasi library Python mutakhir untuk manajemen state CLI (mis. Textual screen-stack, pola navigasi modal), dan pola optimasi agar kode yang dihasilkan *up-to-date*, aman, dan berkinerja tinggi.
3. **JALAN KETIGA: Pencarian Internet** ➔ Gunakan pencarian internet hanya jika `context7` tidak memberikan informasi yang cukup.
