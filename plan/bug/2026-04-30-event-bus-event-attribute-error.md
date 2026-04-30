# Bug Report: Kegagalan Total Pipeline & Dry-Run Akibat Kesalahan Akses Atribut `Event` pada Singleton Event Bus

- **Tanggal Laporan:** 2026-04-30
- **Pelapor:** Senior Software Architect (sesi debug otonom)
- **Komponen Terdampak:** Lapisan observability (event bus), pipeline ETL, mesin Dry-Run, modul introspeksi skema
- **Tingkat Keparahan:** Blocker / Kritis — seluruh aksi yang menerbitkan event (dry-run, migrasi, introspeksi) selalu gagal pada panggilan publish pertama
- **Status:** Open / Belum diperbaiki
- **Kategori Cacat:** Kesalahan kontrak antarmuka (interface contract violation) yang sistemik dan deterministik
- **Lingkup Skenario Reproduksi:** Mapping `area_publik` (table self-mapping; `mappings/area_publik_to_area_publik.yaml`) — tetapi cacat berlaku universal untuk seluruh mapping karena tidak bergantung pada isi data

---

## 🤖 SOP Eksekusi (Wajib Dibaca)
**PENTING: Sebelum mengeksekusi penulisan kode untuk task ini, Anda wajib mencari referensi terbaru. Ikuti urutan prioritas berikut:**

1. **JALAN PERTAMA: `/graphify query`** — Gunakan selalu untuk pemindaian file atau mencari logika aplikasi. Hindari pemindaian file secara rekursif (`find`, `ls -R`, dll).
2. **JALAN KEDUA: `context7`** — Selalu utamakan `context7` untuk mendapatkan *best practice*, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan *up-to-date*, aman, dan berkinerja tinggi.
3. **JALAN KETIGA: Pencarian Internet** — Gunakan pencarian internet hanya jika `context7` tidak memberikan informasi yang cukup.

---

## 1. Ringkasan Eksekutif

Saat dry-run untuk table `area_publik` dijalankan terhadap mapping `mappings/area_publik_to_area_publik.yaml`, mesin Dry-Run gagal pada panggilan publikasi event pertama dengan pesan bahwa objek `EventBus` tidak memiliki atribut bernama `Event`. Setelah kesalahan tersebut dijinakkan secara eksperimental (dengan menambahkan alias darurat di runtime), sisa pipeline dry-run berjalan normal: 10 baris berhasil diekstrak dari source, transformasi rampung tanpa anomali, dan laporan menyatakan status `PASS`. Ini membuktikan bahwa pipeline ekstraksi/transformasi inti **sehat** untuk mapping ini; satu-satunya penghalang adalah kesalahan deklaratif pada cara seluruh modul memanggil event bus.

Cacat ini bukan kasus tunggal — pemindaian terstruktur kode menemukan pola panggilan yang sama tersebar di tiga modul utama: mesin Dry-Run, pipeline ETL utama, dan modul introspeksi skema. Karena event bus adalah jalur komunikasi tunggal antara worker thread dan UI, kegagalan ini menutup setiap alur yang ingin melaporkan progres ke pengguna.

## 2. Cara Reproduksi

1. Pastikan berkas konfigurasi koneksi `connection.yaml` sudah ada dan kredensial source/target valid.
2. Pilih file mapping `mappings/area_publik_to_area_publik.yaml`.
3. Jalankan alur Dry-Run dari menu TUI (atau panggil mesin Dry-Run secara setara melalui pemanggilan internal).
4. Setelah koneksi berhasil dan probe metadata target selesai, mesin Dry-Run mencoba menerbitkan event "DryRunStarted" dan langsung terhenti dengan kesalahan akses atribut.

Reproduksi bersifat deterministik: tidak bergantung pada isi data tabel sumber maupun target, tidak bergantung pada `sample_limit`, dan tidak bergantung pada apakah kolom mapping mengandung anomali. Kesalahan terjadi sebelum baris data manapun diproses.

## 3. Observasi Galat (Hasil Eksekusi Aktual)

- Tahap koneksi ke source dan target: **berhasil**.
- Tahap pemuatan dokumen mapping `area_publik_to_area_publik.yaml`: **berhasil** (parser YAML mengenali `source_table`, `target_table`, `pk_column=id`, `batch_size=10000`, dan seluruh entri `mappings` dengan benar).
- Tahap probe metadata target: **berhasil** (skema `smartoffice_mail.area_publik` ditemukan).
- Tahap publikasi event awal `DRY_RUN_STARTED`: **gagal**. Interpreter Python melaporkan bahwa instance `EventBus` tidak memiliki atribut `Event`. Eksekusi terhenti tanpa pernah mencapai loop ekstraksi/transformasi.
- Setelah cacat ini diakali sementara di luar source code (menambahkan alias darurat saat runtime), dry-run dengan `sample_limit=10` berhasil sampai akhir: 10 baris diekstrak, status laporan `PASS`, jumlah anomali 0. Hal ini mengonfirmasi bahwa pipeline ekstraksi/transformasi/validasi inti tidak mengandung cacat untuk mapping ini.

## 4. Pemindaian Arsitektur (Trace Dependensi)

Hasil eksplorasi knowledge graph proyek menunjukkan posisi dan keterhubungan modul yang terlibat:

- **Modul observability** mengekspos tiga simbol publik: kelas `Event`, kelas `EventBus`, dan singleton `event_bus` (instance dari `EventBus`). Ketiga simbol ini diekspor melalui `observability/__init__.py`, sehingga seharusnya dipanggil sebagai entitas independen di setiap konsumen.
- **Mesin Dry-Run** (komponen utama yang gagal pada skenario ini) mengimpor `event_bus` dan `EventType`, tetapi **tidak** mengimpor kelas `Event`. Setiap kali ia ingin menerbitkan event, ia memanggil `event_bus.Event(...)` seakan-akan `Event` adalah factory method milik singleton. Pola ini diulang lima kali di dalam metode `execute()` mesin Dry-Run.
- **Pipeline ETL utama** (`etl_pipeline.py`) memakai pola panggilan yang identik pada lebih dari dua puluh titik publikasi event di seluruh siklus migrasi (mulai dari "JobStarted" hingga "JobCompleted/Aborted", termasuk emisi progres per-batch).
- **Modul introspeksi skema** memakai pola yang sama pada enam titik publikasi event saat fase introspeksi awal.
- **TUI Dry-Run Screen** dan **TUI Migrate Screen** menjadi konsumen di sisi penerima, mendengarkan event lewat `event_bus.subscribe(...)` untuk memperbarui progres bar, status label, dan ringkasan laporan.
- **Event bus singleton** memiliki dispatcher worker thread terpisah yang memproses queue secara FIFO dan memanggil semua subscriber. Karena setiap penerbitan event selalu gagal di sisi publisher, dispatcher tidak pernah menerima event apapun, sehingga semua callback UI berhenti diperbarui.

Implikasi sentralitas: cacat berada di lapisan tipis (cara pemanggilan), tetapi karena event bus adalah satu-satunya jalur komunikasi worker→UI, efek blast meliputi seluruh permukaan pengamatan dan progres pengguna selama eksekusi pipeline.

## 5. Analisis Akar Masalah (Root Cause Analysis)

Akar masalahnya adalah **kesalahan model mental** terhadap simbol `Event` saat fase implementasi awal seluruh penerbit event. Penulis kode tampaknya menganggap kelas `Event` adalah anggota (atribut) dari instance `event_bus`, padahal dalam desain modul observability:

1. `Event` adalah **kelas tingkat modul** yang berdiri sendiri di `observability/events.py`. Ia harus dipanggil sebagai konstruktor langsung — yaitu memanggil nama kelasnya — sebagaimana lazimnya pola event di Python.
2. `event_bus` adalah **instance singleton** dari kelas `EventBus`. Kelas `EventBus` hanya menyediakan metode publik `publish`, `subscribe`, `start`, dan `stop`. Tidak ada metode atau atribut bernama `Event` di sana.
3. Re-eksport `Event` melalui `observability/__init__.py` menyediakan jalur impor yang ringkas (`from sync_mail.observability import event_bus, Event, EventType`), tetapi tidak ada penulis pun yang konsisten memakai jalur ini untuk kelas `Event`. Seluruh penulis hanya mengimpor `event_bus` dan `EventType`, lalu mencoba mengakses `Event` sebagai atribut dari `event_bus`.

Mengapa cacat ini lolos dari review:

1. **Tidak ada uji integrasi end-to-end yang benar-benar menerbitkan event** ke dalam pipeline; uji unit yang ada cenderung memanggil komponen secara terpisah dengan stub atau mock event bus, sehingga jalur kode `event_bus.Event(...)` tidak pernah dieksekusi nyata di pipeline kualitas.
2. **Python tidak melakukan validasi statis** terhadap akses atribut runtime; tipe pemeriksa statis (mis. `mypy`) jika dipakai bisa menangkapnya, namun proyek belum mengaktifkan strict type checking pada modul observability.
3. **Pola panggilan yang salah ini ditiru secara konsisten** di lebih dari satu modul — kemungkinan besar oleh proses *copy-paste* dari satu titik publikasi awal yang sudah salah, sehingga akar tunggal menyebar menjadi lebih dari tiga puluh insiden tersebar.
4. **Pesan error hanya muncul di runtime** dan hanya pada jalur eksekusi yang dipicu oleh worker thread, sehingga tidak terlihat saat membuka aplikasi atau menjalankan layar tanpa memulai pekerjaan apa pun.

Kategori cacat: kesalahan kontrak antarmuka (memperlakukan kelas tingkat modul sebagai atribut instance) dengan multiplikasi karena duplikasi pola.

## 6. Dampak terhadap Logika Aplikasi

- **Dampak fungsional langsung pada Dry-Run:** mesin gagal sebelum loop ekstraksi dijalankan; pengguna tidak menerima ringkasan anomali, status laporan, ataupun progres. Tombol "Lanjut ke Migrasi" tidak pernah dapat diaktifkan karena alur dry-run tidak pernah selesai.
- **Dampak pada migrasi nyata:** pipeline ETL juga akan gagal pada penerbitan event "JobStarted" yang merupakan event pertama dalam siklus. Konsekuensinya, migrasi tidak pernah memulai loop ekstraksi-transformasi-pemuatan dan tidak ada baris yang dipindah ke target. Tidak ada risiko data korup atau transaksi setengah jadi karena kegagalan mendahului pembukaan transaksi.
- **Dampak pada introspeksi skema:** introspeksi awal yang menerbitkan event progres juga akan langsung gagal, sehingga generator template YAML tidak pernah menyelesaikan siklus dan UI introspeksi tidak menerima pembaruan.
- **Dampak pada state.json / checkpoint:** nihil; tidak ada penulisan state karena pipeline tidak pernah masuk fase per-batch.
- **Dampak pada pengalaman pengguna:** tinggi — aplikasi terasa rusak total pada setiap jalur kerja utama, padahal logika bisnis di balik UI sebagian besar sehat.
- **Dampak pada data target di environment produksi/staging:** nihil — tidak ada perubahan tertulis. Cacat ini bersifat *fail-closed* (gagal di awal), bukan *fail-open* (gagal di tengah operasi).

## 7. Rencana Perbaikan Terstruktur

Perbaikan dirancang berlapis: koreksi sumber, pencegahan regresi, dan dokumentasi konvensi.

### 7.1 Perbaikan Konseptual pada Kode

- **Penyelarasan pola panggilan event:** Setiap titik penerbitan event yang saat ini menggunakan akses atribut pada singleton harus dialihkan menjadi panggilan langsung terhadap kelas `Event` yang diimpor pada bagian atas berkas. Pilihan termudah adalah menambah `Event` ke daftar simbol yang diimpor pada setiap modul terdampak (mesin Dry-Run, pipeline ETL utama, modul introspeksi).
- **Pembersihan impor:** Modul-modul yang sudah mengimpor `event_bus` dan `EventType` cukup memperluas impornya untuk turut menyertakan `Event`. Tidak ada modul baru yang perlu dibuat.
- **Konsistensi penamaan:** Konvensi tunggal di seluruh proyek harus ditetapkan, yakni "publish dengan kelas Event tingkat modul, bukan via instance bus". Konvensi ini sebaiknya dicatat sebagai memori proyek (`bd remember`) agar agent dan kontributor manusia masa depan tidak mengulang kesalahan yang sama.

### 7.2 Pengerasan agar Tidak Terulang

- **Smoke test integrasi event bus:** menambahkan uji end-to-end yang mensimulasikan satu siklus dry-run pendek terhadap fixture in-memory atau database uji, yang berhasil menerbitkan dan menerima minimal satu event tipe `DRY_RUN_STARTED` dan satu event tipe `DRY_RUN_COMPLETED`. Tujuan utamanya bukan validasi data, melainkan memastikan kontrak publish tidak pernah meledak lagi.
- **Uji statis ringan:** mengaktifkan pemeriksa tipe statis pada modul observability dan modul-modul penerbit event, atau setidaknya menambahkan aturan linting kustom yang menolak pola `event_bus.Event(...)` sebagai panggilan ilegal.
- **Pre-commit guard:** menambahkan aturan grep di hook pre-commit yang menggagalkan commit bila menemukan pola `event_bus.Event(` di kode produksi, dengan saran pesan kesalahan untuk mengarahkan ke konvensi yang benar.
- **Audit one-shot:** sekali fix diterapkan, lakukan satu sapuan menyeluruh untuk memastikan tidak ada sisa panggilan dengan pola lama yang terlewat di modul yang lebih kecil (mis. reporter, orchestrator, screen tertentu yang tidak terjangkau pemindaian awal).

### 7.3 Dokumentasi & Konvensi

- **Bagian "Cara menerbitkan event" di pedoman kontribusi:** menambahkan paragraf singkat yang menjelaskan tiga simbol publik dari modul observability dan cara pemanggilan yang benar (kelas Event sebagai konstruktor, instance event_bus untuk publish/subscribe, enum EventType untuk identitas event).
- **Catatan di knowledge graph proyek:** memperbarui ringkasan komunitas yang berkaitan dengan event bus agar memuat peringatan eksplisit tentang pola pemanggilan yang tepat.
- **Catatan di runbook / memory:** menyimpan keputusan ini sebagai memori agar setiap sesi mendatang tidak perlu menemukan ulang root cause yang sama.

### 7.4 Verifikasi Pasca Perbaikan

1. Menjalankan ulang dry-run untuk mapping `area_publik` dengan `sample_limit=10`. Hasil yang diharapkan: status `PASS`, 10 baris diekstrak, 0 anomali (sesuai hasil simulasi setelah cacat dijinakkan secara temporer).
2. Menjalankan dry-run untuk satu mapping lain yang memiliki ENUM atau perubahan tipe (mis. salah satu mapping `mail_archive_*`) untuk memastikan event progres benar-benar diteruskan ke UI selama loop berjalan, bukan hanya event awal/akhir.
3. Mensimulasikan migrasi pendek terhadap subset data uji dan memverifikasi bahwa event `JOB_STARTED`, `BATCH_COMMITTED`, dan `JOB_COMPLETED` semuanya tampak di langganan UI tanpa kesalahan.
4. Menjalankan introspeksi skema dari awal dan memastikan progresnya sampai ke UI tanpa error.
5. Menjalankan smoke test TUI yang sudah ada (untuk regresi CSS) bersamaan, memastikan tidak ada regresi silang.

## 8. Risiko & Pertimbangan Lanjutan

- **Risiko sisa panggilan terlewat:** Audit awal sudah menemukan pola di tiga modul utama; tetap perlu sapuan akhir untuk modul yang lebih jarang dijalankan (reporter, orchestrator multi-job, screen-screen niche).
- **Risiko regresi pada langganan UI:** Pengubahan pemanggilan tidak mengubah kontrak event (tipe maupun payload), jadi sisi konsumen UI tidak perlu disesuaikan. Risiko regresi pada layar progres rendah, tetapi tetap perlu diverifikasi visual.
- **Risiko thread safety:** Tidak berubah; event bus tetap memakai queue thread-safe dan dispatcher worker daemon. Perbaikan murni di sisi pemanggil.
- **Pertimbangan migrasi historis:** Karena cacat ini fail-closed, tidak ada data inkonsisten yang perlu dibersihkan dari run-run sebelumnya — tidak pernah ada run yang berhasil menulis ke target via pipeline ini.

## 9. Tindak Lanjut yang Disarankan

1. Menautkan dokumen ini ke issue Beads `sync-mail-0yo` ("Debug dry-run error untuk table area_publik") sebagai design reference, lalu menurunkan sub-issue tersendiri untuk: (a) perbaikan pemanggilan, (b) penambahan smoke test integrasi, (c) penegakan linting/pre-commit guard.
2. Memprioritaskan perbaikan ini sebelum perbaikan TUI lainnya, karena seluruh fitur produksi (dry-run, migrasi, introspeksi) bergantung padanya.
3. Memutuskan apakah perbaikan didistribusikan dalam satu commit besar (lebih sedikit churn riwayat) atau beberapa commit per-modul (lebih mudah ditinjau). Rekomendasi: satu commit per-modul disertai uji integrasi tunggal yang menutup ketiganya.
4. Setelah perbaikan diterapkan, menjalankan `graphify update .` agar peta dependensi proyek mencerminkan keadaan terbaru dan tidak lagi membingungkan agent masa depan.
5. Menyimpan catatan permanen di sistem memori (`bd remember`) bahwa pola panggilan event yang benar adalah memanggil kelas `Event` langsung, bukan via atribut `event_bus`.
