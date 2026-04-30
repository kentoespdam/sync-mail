# Bug Report: Migrasi `area_publik` Gagal Akibat Pelanggaran CHECK Constraint pada Kolom `status` (+ Cascading TUI Threading Error)

- **Tanggal Laporan:** 2026-04-30 (revisi: tambahan galat threading TUI)
- **Pelapor:** Senior Software Architect (otonom debug session)
- **Komponen Terdampak:**
  1. **Primer:** lapisan transformasi pipeline ETL (`pipeline/transformer.py`) dan generator template mapping (`reconciliation/auto_yaml.py`).
  2. **Sekunder (kaskade):** lapisan presentasi TUI — penanganan event bus pada `tui/screens/migrate.py` dan `tui/screens/dry_run.py` yang menggunakan `App.call_from_thread` secara tidak aman.
- **Tingkat Keparahan:** Tinggi (Blocker per-tabel + Blocker UX). Galat database menggagalkan migrasi data; galat threading menyebabkan TUI ikut crash sehingga pengguna kehilangan jendela kerja, log, dan progress yang terkumpul.
- **Status:** Open / Belum diperbaiki
- **Lingkup:** Galat domain nilai berdampak pada semua tabel yang mengalami perubahan enum sumber → CHECK/enum tujuan. Galat threading berdampak pada seluruh alur kerja TUI yang melibatkan event bus saat skenario gagal — bukan hanya `area_publik`.

---

## 🤖 SOP Eksekusi (Wajib Dibaca)
**PENTING: Sebelum mengeksekusi penulisan kode untuk task ini, agen wajib mencari referensi terbaru dengan urutan prioritas:**

1. **JALAN PERTAMA: `/graphify query`** — pemindaian struktur dan alur logika kode (hindari `find`, `ls -R`, scan rekursif).
2. **JALAN KEDUA: `context7`** — best practice & dokumentasi library mutakhir (SQLAlchemy Core, pola transformasi ETL).
3. **JALAN KETIGA: Pencarian Internet** — hanya jika `context7` tidak mencukupi.

---

## 1. Ringkasan Eksekutif
Laporan ini mencakup **dua galat yang saling berurutan dalam satu skenario**:

**Galat Primer — pelanggaran CHECK constraint pada database tujuan.** Job migrasi tabel `area_publik` berhenti pada batch pertama dengan kode galat MariaDB 4025 (`CONSTRAINT chk_publik_status failed`). Akar masalah adalah ketidaksetaraan domain nilai antara enum sumber dan CHECK constraint tujuan — bukan ketidaksetaraan tipe data. Mesin transformasi saat ini hanya mendukung perubahan tipe (CAST), default injection (INJECT_DEFAULT), atau pass-through (NONE); ia tidak memiliki primitif pemetaan nilai-ke-nilai (value lookup). Akibatnya nilai enum sumber `'Draft'` dan `'Ditampilkan'` mengalir apa adanya menuju kolom tujuan yang hanya menerima `'DRAFT'`, `'PUBLISHED'`, `'DELETED'`.

**Galat Sekunder — kaskade ke TUI berupa `RuntimeError: The 'call_from_thread' method must run in a different thread from the app`.** Ketika galat primer dipublikasikan ke event bus, handler TUI mencoba meneruskan event ke widget melalui `App.call_from_thread`. Namun pada jalur publikasi tertentu handler tersebut sudah berada di thread utama (event-loop) aplikasi, sehingga panggilan tersebut melanggar prasyarat Textual ("call_from_thread harus dipanggil dari thread non-utama") dan memicu `RuntimeError`. Akibatnya TUI macet/crash tepat ketika pengguna paling membutuhkan diagnostik kegagalan migrasi.

## 2. Cara Reproduksi
1. Pastikan `connection.yaml` mengarah ke sumber `smartoffice` dan tujuan `smartoffice_mail`.
2. Pastikan tabel tujuan `area_publik` memiliki CHECK constraint `chk_publik_status` (sudah terpasang pada skema baseline).
3. Jalankan job migrasi `area_publik` menggunakan file pemetaan auto-generated `mappings/area_publik_to_area_publik.yaml`.
4. Amati: koneksi sumber dan tujuan terbentuk, ekstraksi batch pertama berhasil, transformasi berhasil, namun fase load dengan `executemany` ditolak oleh server tujuan.

## 3. Observasi Galat

### 3.1 Galat Primer (Database)
- Kelas exception terbungkus: `BatchFailedError` — pesan: *"Failed to load batch into area_publik"*.
- Penyebab langsung: `pymysql.err.OperationalError` kode **4025** dengan teks **"CONSTRAINT `chk_publik_status` failed for `smartoffice_mail`.`area_publik`"**.
- Lokasi gagal: fase Load (bulk insert), bukan fase Extract atau Transform.
- Verifikasi data: kolom sumber `status` bertipe `enum('Draft','Ditampilkan')`; semua nilai distinct di sumber adalah `Draft` dan `Ditampilkan`. Kolom tujuan `status` adalah `varchar(20)` dengan CHECK menerima hanya `'DRAFT'`, `'PUBLISHED'`, `'DELETED'`.
- Konsekuensi transaksional: per-batch atomic transaction melakukan ROLLBACK; checkpoint tidak maju sehingga job akan jatuh di batch yang sama pada setiap retry.

### 3.2 Galat Sekunder (TUI Threading)
- Pesan exception: **`RuntimeError: The 'call_from_thread' method must run in a different thread from the app`**.
- Pemicu: dipublikasikan oleh framework Textual saat `App.call_from_thread(...)` dijalankan dari thread utama aplikasi alih-alih dari thread pekerja.
- Lokasi pemanggilan yang berisiko: handler subscriber event bus pada `tui/screens/migrate.py` (jalur `on_event → handle_event_ui`) dan `tui/screens/dry_run.py` (jalur `on_bus_event → handle_event_ui`), serta blok `except`/`finally` worker yang membungkus `notify` dan `_show_finish` melalui `call_from_thread`.
- Pola pemicu praktis:
  1. Saat job batch dihentikan oleh galat primer, `BatchFailedError` mengalir kembali ke worker; pada beberapa jalur, event bus mendispatch event terakhir secara sinkron dari thread utama (mis. saat dispatcher belum sempat start, atau saat skrip dijalankan tanpa worker latar belakang).
  2. Saat handler dipanggil dari thread utama, `call_from_thread` menolaknya — bukan re-routing otomatis.
- Konsekuensi: TUI crash tepat di momen krusial (saat menampilkan galat migrasi), pesan asli dari database tertelan oleh stack trace `RuntimeError`, dan pengguna kehilangan akses ke panel log untuk diagnosis.

## 4. Pemindaian Arsitektur (Trace Logika)

### 4.1 Jalur Galat Primer
Hasil penelusuran graf dependensi memetakan jalur eksekusi yang terlibat:
- Loader pemetaan (`config/loader.py → load_mapping`) → orkestrator (`pipeline/orchestrator.py → MigrationJob.run`).
- Orkestrator memanggil tiga primitif berurutan: ekstraksi (extractor), transformasi (`pipeline/transformer.py → transform / transform_row`), pemuatan (`pipeline/loader.py → load`).
- Fungsi transformasi mencabang berdasarkan `transformation_type` dengan tiga cabang valid: NONE, CAST, INJECT_DEFAULT. Tidak ada cabang untuk pemetaan nilai diskrit.
- Pada cabang CAST, hanya tipe Python yang diubah (str/int/Decimal/float). Nilai literal sumber dipertahankan apa adanya, sehingga `'Draft'` tetap menjadi `'Draft'` setelah transformasi ke `varchar(20)`.
- Generator template (`reconciliation/auto_yaml.py`) memproduksi mapping berdasarkan kemiripan tipe kolom; ia menandai kolom dengan flag `ACTION_REQUIRED` untuk peninjauan manual, namun tidak memodelkan pergeseran domain nilai (enum) — sehingga reviewer manusia mudah melewatkan kasus ini.

### 4.2 Jalur Galat Sekunder (TUI ↔ Event Bus ↔ Worker)
- `EventBus` (`observability/events.py`) berjalan dengan satu thread dispatcher latar belakang yang menyalurkan event ke setiap subscriber. Asumsi desainnya: handler subscriber selalu dieksekusi dari thread non-utama, sehingga aman memanggil `App.call_from_thread`.
- `MigrateScreen` mendaftarkan dirinya sebagai subscriber dan worker ETL berjalan via `@work(thread=True)`. Saat alur normal, kedua jalur berada di thread non-utama → `call_from_thread` valid.
- Asumsi runtuh pada dua skenario: (a) ketika worker memunculkan exception lalu blok `finally` masih dijalankan dari konteks yang terikat ke event-loop (tergantung urutan teardown Textual), dan (b) ketika test/skrip programatik (mis. eksekusi manual yang menyimulasikan reproduksi) memanggil `MigrationJob.run()` langsung dari thread utama tanpa worker, sehingga handler subscriber pun dipanggil dari thread utama.
- Tidak ada *guard* di kedua screen yang memeriksa "apakah saya saat ini di thread utama?" sebelum memanggil `call_from_thread`. Tidak ada fallback yang memilih `app.call_later`/posting event ke message-pump bila sudah di thread utama.

### 4.3 Hubungan Antar Galat
Galat primer adalah pemicu eksternal; galat sekunder adalah cacat ketahanan (resilience flaw) di lapisan presentasi yang terpapar oleh peristiwa galat. Memperbaiki primer saja akan menyembunyikan sekunder, tetapi sekunder akan kembali muncul pada *setiap* skenario kegagalan migrasi lain (FK, unique, tipe). Karena itu kedua perbaikan harus berjalan paralel.

## 5. Root Cause Analysis
Akar masalah berada pada **tiga lapis** yang saling memperkuat:

**Lapis A — Mesin Transformasi (penyebab teknis galat primer).**
Kontrak `transformation_type` saat ini tidak memiliki primitif untuk *value translation*. CAST yang dipakai hanya mengubah representasi tipe data, bukan domain nilai. Sebagai konsekuensi, perbedaan nilai antara sumber (`Draft`/`Ditampilkan`) dan tujuan (`DRAFT`/`PUBLISHED`/`DELETED`) tidak dapat diekspresikan di YAML mapping tanpa mengubah kode.

**Lapis B — Generator Auto-Mapping (penyebab proses galat primer).**
Auto-YAML hanya menganalisis perbedaan **tipe** kolom; ia tidak membandingkan **isi enum** atau pun memeriksa keberadaan CHECK constraint pada tabel tujuan. Akibatnya, file mapping yang dihasilkan tampak "siap pakai" padahal mengandung jebakan domain nilai. Flag `ACTION_REQUIRED` ada tetapi tidak spesifik terhadap pergeseran enum.

**Lapis C — Kontrak Threading TUI (penyebab galat sekunder).**
Subscriber event bus di TUI memanggil `App.call_from_thread` tanpa memverifikasi konteks thread. Aturan Textual eksplisit: API tersebut dirancang untuk *menyeberangkan* pemanggilan dari thread pekerja ke event-loop aplikasi, dan akan menolak pemanggilan dari thread aplikasi itu sendiri. Karena dispatcher event bus dan worker ETL biasanya berada di thread terpisah, asumsi "selalu non-utama" tampak benar untuk jalur normal — namun bocor pada jalur galat dan jalur reproduksi sinkron. Akar konseptualnya: tidak ada abstraksi tunggal "kirim event ini ke UI dengan aman dari thread mana pun" — setiap screen mengulang pola yang sama dengan asumsi yang berbeda.

## 6. Dampak Logika & Data
- **Korupsi data:** tidak ada — transaksi atomic mencegah baris parsial masuk ke tujuan.
- **Progres job:** terhenti total pada batch pertama; checkpoint tidak maju.
- **Cakupan ledakan (primer):** seluruh tabel sumber yang memiliki kolom enum dengan label berbeda dari CHECK constraint tujuan akan mengalami pola gagal yang sama. Berdasarkan inventaris pemetaan (25 tabel), risiko meluas ke setiap kolom berstatus/berkategori yang mengalami harmonisasi nomenklatur antar skema.
- **Cakupan ledakan (sekunder):** galat threading TUI meluas ke setiap skenario kegagalan migrasi (FK, unique, tipe data, koneksi terputus) — bukan hanya kasus CHECK. Setiap kali galat dipublikasikan ke event bus pada saat handler kebetulan berjalan di thread utama, TUI ikut crash. Selain itu, layar Dry-Run dan Migrate sama-sama terpapar.
- **Risiko regresi diam (silent):** apabila CHECK constraint tujuan dilonggarkan demi "menyelamatkan" job, integritas semantik di tujuan rusak (mis. nilai bahasa Indonesia bercampur dengan nilai bahasa Inggris dalam satu kolom).
- **Pengalaman pengguna:** kombinasi kedua galat memperburuk diagnosa — pesan asli database tertelan oleh stack trace `RuntimeError`, panel log TUI tidak sempat menampilkan konteks, dan pengguna menerima dua jenis kegagalan sekaligus (job dan TUI) sehingga sulit membedakan akar masalah.

## 7. Rencana Perbaikan (Terstruktur, Konseptual)
Perbaikan dirancang berlapis: (a) primitif transformasi baru, (b) deteksi dini, (c) kualitas pesan galat. Tidak ada perubahan pada arsitektur streaming, keyset pagination, atau strategi commit per-batch.

### 7.1 Tambahkan Primitif `MAP_VALUE` pada Mesin Transformasi
- **Tujuan:** memungkinkan pemetaan nilai diskrit sumber → tujuan secara deklaratif di YAML, tanpa menyentuh kode pipeline.
- **Kontrak konseptual:** sebuah entri mapping kolom mendapat tipe transformasi baru (mis. `MAP_VALUE`) yang memuat tabel pencarian (lookup) berisi pasangan nilai-sumber → nilai-tujuan, plus klausa fallback eksplisit (gunakan nilai default tertentu, lewatkan baris, atau gagalkan batch).
- **Aturan validasi:** setiap nilai distinct yang ditemukan di sumber harus tercakup oleh lookup atau tertangani fallback — dilakukan saat fase pra-jalan (lihat 7.2).
- **Komposabilitas:** dapat dirantai dengan CAST (lookup dulu, lalu paksa tipe) bila skema tujuan menuntutnya.

### 7.2 Perkuat Mode Dry-Run dengan Pemeriksaan Domain Nilai
- **Tujuan:** menangkap kasus seperti ini sebelum batch pertama dijalankan.
- **Mekanisme:** mode dry-run yang sudah direncanakan (lihat plan/claude/11) diperluas untuk: (i) membaca CHECK constraint dan definisi enum tujuan dari `information_schema`, (ii) membaca `DISTINCT` nilai sampel dari kolom sumber bertipe enum/varchar dengan kardinalitas rendah, (iii) menyilangkan keduanya untuk mendeteksi nilai yang akan ditolak. Output berupa rekomendasi anomali — kolom mana, nilai mana, saran lookup yang harus diisi.
- **Output:** anomali level `BLOCKER` yang muncul di TUI Dry-Run Screen dan di laporan HTML.

### 7.3 Tingkatkan Generator Auto-YAML
- **Tujuan:** mengurangi peluang kasus ini lolos ke produksi.
- **Mekanisme:** saat sumber bertipe enum dan tujuan memiliki CHECK constraint atau enum dengan nilai berbeda, generator menyisipkan kerangka `MAP_VALUE` kosong dengan komentar `ACTION_REQUIRED: lengkapi pemetaan nilai enum` alih-alih `CAST` polos.
- **Manfaat:** reviewer manusia dipaksa mengisi tabel pencarian sebelum job dapat dijalankan, mencerminkan praktik standar ETL (value-mapping dictionary).

### 7.4 Perkaya Pesan Galat pada Loader
- **Tujuan:** mempercepat triase ketika constraint tetap dilanggar di runtime (mis. nilai baru muncul di sumber setelah pemetaan disusun).
- **Mekanisme:** saat MariaDB mengembalikan kode 4025 (CHECK gagal) atau 1062/1452 (FK), loader mengekstrak nama constraint dari pesan dan menambahkan konteks ke `BatchFailedError`: tabel target, nama kolom yang paling mungkin terkait constraint, contoh nilai yang tertolak (sampel dari batch), dan saran remediasi singkat.

### 7.5 Pemetaan Sementara untuk `area_publik` (Hotfix Operasional)
- **Tujuan:** melepaskan blokade migrasi tabel ini sambil perbaikan struktural 7.1–7.4 berjalan.
- **Mekanisme:** segera setelah primitif `MAP_VALUE` tersedia, file mapping `area_publik` diperbarui dengan tabel pencarian: `Draft → DRAFT`, `Ditampilkan → PUBLISHED`. Tidak ada nilai sumber yang berpadanan dengan `DELETED`, sehingga label `DELETED` di tujuan dibiarkan kosong (tidak ada baris yang menghasilkannya). Fallback: gagalkan batch jika muncul nilai sumber baru di luar kedua label tersebut.

### 7.6 Bridge Thread-Safe untuk Event Bus → UI (Perbaikan Galat Sekunder)
- **Tujuan:** menghilangkan `RuntimeError` `call_from_thread` dan menjadikan jembatan event-bus → UI tahan banting di semua skenario.
- **Mekanisme konseptual:**
  1. Sentralkan satu helper (mis. di lapisan TUI app) yang menerima callable beserta argumennya, lalu memutuskan jalur eksekusi berdasarkan thread saat ini: jika dipanggil dari thread utama, eksekusi langsung; jika dari thread non-utama, lewatkan ke event-loop aplikasi melalui mekanisme resmi Textual (post message / call_from_thread). Tidak ada lagi pemanggilan langsung `call_from_thread` dari subscriber.
  2. Refaktor `MigrateScreen.on_event` dan `DryRunScreen.on_bus_event` agar memanggil helper terpadu tersebut, sehingga aman tanpa peduli thread asal.
  3. Tambahkan unit test yang secara eksplisit menjalankan publikasi event dari thread utama dan thread non-utama serta memverifikasi tidak ada `RuntimeError` dan handler tetap dipanggil tepat satu kali.
  4. Pastikan dispatcher event bus selalu mulai sebelum subscriber pertama menerima event (audit `EventBus.start`/`subscribe` urutan inisialisasi). Bila dispatcher belum aktif, antrekan event ke buffer dan replay setelah start — bukan eksekusi sinkron yang menjebak handler di thread utama.
- **Output yang diharapkan:** TUI tetap responsif di semua skenario kegagalan migrasi; pesan galat asli (mis. CHECK constraint, FK, koneksi) tampil rapi di panel log alih-alih digantikan stack trace threading.

### 7.7 Pengerasan Kontrak Worker pada Layar Migrate & Dry-Run
- **Tujuan:** mencegah jalur exception `finally` membocorkan eksekusi UI ke thread utama secara tidak sengaja.
- **Mekanisme:** semua side-effect UI di blok `except`/`finally` worker melewati helper terpadu (lihat 7.6); blok ini tidak boleh memanggil API Textual secara langsung. Tambahkan pemeriksaan defensif: bila helper mendeteksi worker tidak lagi terikat pada screen aktif (mis. screen sudah pop), aksi dilewatkan diam-diam alih-alih melempar eksepsi sekunder.

## 8. Kriteria Penerimaan
1. Job migrasi `area_publik` berjalan hingga selesai untuk seluruh dataset sumber tanpa pelanggaran CHECK constraint apa pun.
2. Mode dry-run melaporkan anomali domain-nilai dengan tingkat `BLOCKER` ketika file mapping tidak menyediakan terjemahan untuk nilai sumber yang tidak diterima oleh tujuan.
3. Generator Auto-YAML memproduksi kerangka `MAP_VALUE` (bukan `CAST`) untuk kolom enum bila skema tujuan memuat CHECK constraint atau enum dengan nilai berbeda.
4. Pesan galat `BatchFailedError` untuk pelanggaran constraint memuat: nama tabel, nama constraint, kolom terdampak, contoh nilai yang ditolak.
5. Test integrasi baru menyimulasikan pelanggaran CHECK pada `status` dan memverifikasi bahwa pipeline (a) menggagalkan dry-run sebelum eksekusi penuh, dan (b) berhasil ketika `MAP_VALUE` lengkap diberikan.
6. Tidak ada regresi pada job lain yang sudah berhasil; throughput per-batch tetap dalam toleransi.
7. **Threading TUI:** tidak ada `RuntimeError: The 'call_from_thread' method must run in a different thread from the app` yang muncul pada skenario apa pun — termasuk saat job gagal di batch pertama, saat dispatcher event bus belum start, dan saat reproduksi sinkron dari thread utama.
8. **Bridge thread-safe:** test unit memverifikasi bahwa publikasi event bus dari thread utama dan dari thread pekerja sama-sama menjangkau handler UI tepat satu kali tanpa exception.
9. **UX kegagalan:** ketika migrasi gagal, panel log TUI menampilkan pesan asli database (mis. "CHECK constraint chk_publik_status failed pada kolom status, contoh nilai ditolak: 'Draft'") sebelum tombol *Finish* tampil — tidak ada layar putih, tidak ada crash.

## 9. Catatan Tambahan
- Investigasi mengonfirmasi bahwa kontrak streaming, paginasi keyset, dan transaksi atomic per-batch tetap valid; tidak ada perubahan pada arsitektur aliran data.
- Pola lookup-dictionary adalah praktik standar ETL untuk harmonisasi domain nilai antar skema; dengan menambahkannya sebagai primitif YAML, pengguna non-developer dapat menyelesaikan migrasi serupa tanpa modifikasi kode pipeline.
- Galat sekunder threading menunjukkan keterkaitan dengan laporan event-bus 2026-04-30: keduanya berakar pada asumsi tentang konteks thread yang tidak dipaksakan oleh kontrak. Perbaikan 7.6 sebaiknya juga meninjau kembali rekomendasi laporan event-bus agar tidak terjadi tambal-sulam.
- Urutan implementasi yang disarankan: (1) hotfix bridge thread-safe TUI (7.6) — ringan, mengembalikan kegunaan TUI segera; (2) primitif `MAP_VALUE` (7.1) + hotfix mapping `area_publik` (7.5); (3) perluasan dry-run (7.2) dan generator (7.3); (4) perkayaan pesan loader (7.4) dan pengerasan worker (7.7).
