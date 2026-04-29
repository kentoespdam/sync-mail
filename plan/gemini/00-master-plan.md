### Arsitektur Direktori (Folder Tree)

```text
data-migration-engine/
├── app/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         (Manajemen environment, parsing YAML & validasi batch_size statis)
│   ├── database/
│   │   ├── __init__.py
│   │   └── connection.py       (Manajemen koneksi & Server-Side Cursors)
│   ├── introspection/
│   │   ├── __init__.py
│   │   ├── schema_reader.py    (Ekstraksi metadata dari information_schema)
│   │   └── yaml_generator.py   (Pembuatan template YAML otomatis dengan proteksi timestamp)
│   ├── migration/
│   │   ├── __init__.py
│   │   ├── extractor.py        (Pengambilan data via Keyset Pagination & Static Batching)
│   │   ├── transformer.py      (Resolusi tipe data, retensi objek timestamp native)
│   │   ├── loader.py           (Eksekusi Bulk Insert & Transaksi Atomik dengan Fail-Fast)
│   │   └── pipeline.py         (Orkestrasi utama ETL & Hard Stop Handler)
│   └── utils/
│       ├── __init__.py
│       ├── logger.py           (Rotasi Log, STDOUT, & Pencatatan Fatal Error)
│       └── state_manager.py    (Manajemen state.json untuk Resume Capability)
├── templates/
│   └── mapping_template.yaml   (File hasil auto-generate, diedit manual oleh user)
├── logs/
│   └── migration.log           (Pencatatan error dan anomali)
├── state.json                  (Pencatatan Last Evaluated Primary Key)
└── main.py                     (Entry point / CLI Controller)
```

---

### Phased Work Plan (Rencana Pengembangan Berfase)

#### Phase 1: Project Setup, Configuration & Database Connection

> **SOP DELEGASI WAJIB**
> *PENTING: Sebelum mengeksekusi penulisan kode untuk task ini, Anda wajib mencari referensi terbaru di internet. Gunakan `context 7` untuk pencarian data best practice, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan up-to-date dan berkinerja tinggi.*
>
> **KLAUSA PENGAMAN ARSITEKTUR:**
> 1. **Data Integrity Over Availability:** Jika terjadi *error* saat fase *Load*, wajib lakukan `ROLLBACK` total untuk *batch* tersebut dan matikan aplikasi (`sys.exit(1)`). Dilarang membuat logika *auto-retry* per baris.
> 2. **Static Batching:** Ukuran *batch* sepenuhnya dikontrol dari parameter YAML (`batch_size`). Dilarang membuat algoritma penghitung *byte* paket dinamis.
> 3. **Time-Preservation:** Perlakukan stempel waktu (*timestamp*) sebagai objek *immutable*. Gunakan *Direct Mapping* ("NONE") tanpa menyuntikkan fungsi SQL dinamis (seperti `NOW()`) kecuali diinstruksikan eksplisit oleh YAML untuk kolom baru.

* **File Target:** `app/config/settings.py`
    * **Logika High-Level:** Buat modul pemuatan konfigurasi lingkungan (database *credentials*). Implementasikan *parser* YAML yang secara ketat memvalidasi keberadaan properti wajib, khususnya parameter `batch_size`. Jika `batch_size` absen atau bernilai tidak rasional, hentikan inisialisasi aplikasi secara aman.
* **File Target:** `app/utils/logger.py`
    * **Logika High-Level:** Konfigurasikan sistem *logging* ganda (Konsol untuk info *real-time* dan File berotasi untuk *error*). Siapkan format khusus untuk *Fatal Error* yang mampu menangkap pesan *error* asli dari MariaDB, rentang *Primary Key*, dan tumpukan eksekusi (*stack trace*) sebelum aplikasi dimatikan secara paksa.
* **File Target:** `app/database/connection.py`
    * **Logika High-Level:** Kembangkan kelas manajer koneksi database (menggunakan *Context Manager*). Pastikan koneksi *Source* menggunakan konfigurasi *Server-Side Cursors* untuk pembacaan aliran (*streaming*), dan matikan semua fitur pembuatan log kueri statemen di level *driver* untuk mencegah kebocoran memori.

#### Phase 2: Schema Introspection & YAML Generator

> **SOP DELEGASI WAJIB**
> *PENTING: Sebelum mengeksekusi penulisan kode untuk task ini, Anda wajib mencari referensi terbaru di internet. Gunakan `context 7` untuk pencarian data best practice, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan up-to-date dan berkinerja tinggi.*
> *(Terapkan Klausa Pengaman Arsitektur yang sama seperti di Phase 1)*

* **File Target:** `app/introspection/schema_reader.py`
    * **Logika High-Level:** Tulis fungsi ekstraksi metadata ke `information_schema.columns` untuk *Source* dan *Target*. Ekstrak nama kolom, tipe data, dan *nullability*, kemudian simpan dalam bentuk struktur kamus (*dictionary*) yang ternormalisasi.
* **File Target:** `app/introspection/yaml_generator.py`
    * **Logika High-Level:** Buat logika komparasi (*diffing*). Terapkan aturan ketat: untuk kolom *timestamp* (`created_at`, `updated_at`) yang identik namanya, otomatis set `transformation_type` menjadi `"NONE"` (pemetaan langsung). Susun hasil rekonsiliasi ke dalam format `mapping_template.yaml` dan tambahkan parameter global `batch_size` di tingkat atas dengan nilai aman (misal: 2500) sebagai panduan *user*.

#### Phase 3: Transformation Engine & State Management

> **SOP DELEGASI WAJIB**
> *PENTING: Sebelum mengeksekusi penulisan kode untuk task ini, Anda wajib mencari referensi terbaru di internet. Gunakan `context 7` untuk pencarian data best practice, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan up-to-date dan berkinerja tinggi.*
> *(Terapkan Klausa Pengaman Arsitektur yang sama seperti di Phase 1)*

* **File Target:** `app/utils/state_manager.py`
    * **Logika High-Level:** Susun logika baca/tulis sinkron untuk file `state.json`. Fokus pada pencatatan *Primary Key* terakhir yang berhasil di-*commit*. Pastikan file ini diperbarui secara instan pada setiap akhir *batch* agar proses *Resume Capability* selalu akurat meskipun aplikasi dimatikan secara mendadak.
* **File Target:** `app/migration/transformer.py`
    * **Logika High-Level:** Bangun *Transformation Engine* menggunakan fungsi *generator* (`yield`). Terapkan logika pemetaan dari YAML per baris data. Pastikan nilai *datetime* bawaan dari *Source* tidak dimanipulasi dan dipertahankan sebagai objek *native* Python saat dipetakan secara langsung ("NONE"), guna menjaga presisi mili-detik antara *Source* dan *Target*.

#### Phase 4: Batch Migration Pipeline (Extract, Transform, Load)

> **SOP DELEGASI WAJIB**
> *PENTING: Sebelum mengeksekusi penulisan kode untuk task ini, Anda wajib mencari referensi terbaru di internet. Gunakan `context 7` untuk pencarian data best practice, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan up-to-date dan berkinerja tinggi.*
> *(Terapkan Klausa Pengaman Arsitektur yang sama seperti di Phase 1)*

* **File Target:** `app/migration/extractor.py`
    * **Logika High-Level:** Terapkan kueri ekstraksi dengan metode *Keyset Pagination*. Jadikan nilai `batch_size` dari konfigurasi YAML sebagai batas absolut (`LIMIT`) untuk mencegah pelanggaran ukuran paket memori (*max_allowed_packet*).
* **File Target:** `app/migration/loader.py`
    * **Logika High-Level:** Buat mekanisme *Bulk Insert* di dalam sebuah blok transaksi tertutup (*BEGIN/COMMIT*). Implementasikan blok *try-except* (Fail-Fast): jika terdapat kegagalan *insert* pada *batch* tersebut, eksekusi perintah `ROLLBACK` seketika untuk menjaga konsistensi database Target, lalu teruskan sinyal *error* beserta data konteks (pesan MariaDB, *Primary Key* awal/akhir) ke modul orkestrator tanpa melakukan percobaan ulang (*no retries*).
* **File Target:** `app/migration/pipeline.py`
    * **Logika High-Level:** Orkestrasikan *Extractor*, *Transformer*, dan *Loader* dalam sebuah *loop*. Saat sinyal *error* dan *rollback* diterima dari *Loader*, hentikan *loop* seketika (*Hard Stop*), minta modul *Logger* untuk mencatat detail insiden berstatus fatal, dan akhiri siklus program dengan meneruskan kode *exit failure*. Jika sukses, catat status terbaru ke *State Manager*.

#### Phase 5: Entry Point & CLI Controller

> **SOP DELEGASI WAJIB**
> *PENTING: Sebelum mengeksekusi penulisan kode untuk task ini, Anda wajib mencari referensi terbaru di internet. Gunakan `context 7` untuk pencarian data best practice, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan up-to-date dan berkinerja tinggi.*
> *(Terapkan Klausa Pengaman Arsitektur yang sama seperti di Phase 1)*

* **File Target:** `main.py`
    * **Logika High-Level:** Kembangkan *Command Line Interface* (CLI) sebagai pengontrol utama. Sediakan argumen untuk menjalankan fungsi "Generate YAML" atau "Run Migration". Implementasikan proteksi *Graceful Shutdown* untuk sinyal interupsi pengguna (misal: `SIGINT` / `Ctrl+C`) agar jika sistem diminta berhenti, ia menyelesaikan *batch* yang sedang berproses, melakukan *commit*, menyimpan state terakhir, lalu keluar dengan rapi.