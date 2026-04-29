# Product Requirements Document (PRD): Data Migration & Schema Transformation Engine

## 1. Executive Summary & Objectives

Dokumen ini menetapkan spesifikasi teknis dan desain arsitektur untuk pengembangan aplikasi "Data Migration & Schema Transformation" berbasis Python. Sistem ini dirancang untuk memfasilitasi *One-time Batch Migration* skala besar (jutaan baris) dari MariaDB Host 1 (Source) ke MariaDB Host 2 (Target). 

Tantangan utama yang diselesaikan oleh arsitektur ini meliputi rekonsiliasi perbedaan skema, resolusi tipe data (seperti konversi `ENUM` ke `VARCHAR`), penanganan *missing columns* pada target akibat proses optimasi struktur, serta kebutuhan pemrosesan data dengan efisiensi memori yang ketat (*low-footprint*) guna mencegah *resource exhaustion* selama eksekusi ETL (Extract, Transform, Load).

---

## 2. System Architecture & Data Flow

### 2.1 Alur Pemrosesan ETL (Data Flow)
Arsitektur dirancang menggunakan pola *streaming pipeline* untuk mencegah penumpukan data di RAM:
1. **Extract:** Mengambil aliran data dari Source menggunakan *Server-Side Cursors*. Database akan mengirimkan baris data secara bertahap melalui *socket network* alih-alih memuat seluruh *result set* sekaligus ke dalam memori aplikasi.
2. **Transform:** Data difilter dan ditransformasi per *chunk/batch* di memori menggunakan generator Python. Mesin akan mengevaluasi setiap baris terhadap aturan pemetaan YAML untuk melakukan *type casting*, injeksi *default value*, dan normalisasi struktur.
3. **Load:** Menyuntikkan data yang telah ditransformasi ke Target menggunakan operasi *Bulk Insert* untuk meminimalkan *network round-trips* dan mengurangi *overhead* pada MariaDB engine.

### 2.2 Alur Auto-Generate YAML
Fitur *Introspection* bertujuan untuk membuat *mapping template* awal secara otomatis:
1. **Schema Introspection:** Aplikasi mengeksekusi *query* pada `information_schema.columns` di kedua MariaDB hosts untuk mengekstraksi metadata tabel (nama kolom, tipe data, *nullability*).
2. **Reconciliation Logic:** Menggunakan heuristik dasar untuk mencocokkan kolom yang identik. Kolom target yang tidak ada di *source* akan diidentifikasi sebagai *missing columns*.
3. **YAML Generation:** Menyimpan hasil rekonsiliasi dalam format `mapping_template.yaml` dengan indikator parameter yang memerlukan intervensi manual (misal: ditandai dengan flag `ACTION_REQUIRED`).

### 2.3 Rekomendasi Library Python
Untuk mencapai *low-memory processing* terbaik pada jutaan baris data:
* **Database Connector:** `PyMySQL`. Penggunaan kelas `SSDictCursor` (Server-Side Dictionary Cursor) sangat direkomendasikan karena hanya memuat baris yang di-`fetch` ke memori tanpa melakukan *buffering* klien.
* **Database Core (Opsional):** `SQLAlchemy 2.0` (Core layer) dengan konfigurasi `yield_per()` untuk memaksa iterasi *server-side*. Hindari penggunaan layer ORM untuk data skala ini karena *overhead* pemrosesan objek yang sangat tinggi.
* **Transformasi Data:** Generator Python native. Penggunaan `Pandas` umumnya dihindari untuk meminimalkan *overhead* RAM ganda, namun jika transformasi matriks mutlak diperlukan, gunakan integrasi `Pandas` dengan parameter `chunksize` secara ketat.
* **Konfigurasi:** `PyYAML` atau `ruamel.yaml` untuk *parsing* dan penulisan metadata konfigurasi.

---

## 3. Schema Transformation Rules

Mesin pemroses akan memuat konfigurasi dari file YAML sebelum koneksi database dibuka. File ini berfungsi sebagai *Single Source of Truth* untuk resolusi skema.

> **Spesifikasi Aturan YAML**

```yaml
migration_job:
  source_table: "t_transaction_legacy"
  target_table: "tx_transaction_optimized"
  batch_size: 10000
  mappings:
    # Skenario 1: Resolusi Tipe Data (Hardcase ENUM -> VARCHAR)
    - source_column: "status_dokumen"
      target_column: "doc_status"
      transformation_type: "CAST"
      cast_target: "VARCHAR"
      
    # Skenario 2: Direct Mapping (Kolom Identik)
    - source_column: "reference_id"
      target_column: "ref_id"
      transformation_type: "NONE"
      
    # Skenario 3: Resolusi Missing Column (Injeksi Default Value)
    - source_column: null
      target_column: "migrated_at"
      transformation_type: "INJECT_DEFAULT"
      default_value: "CURRENT_TIMESTAMP"
      
    # Skenario 4: Resolusi Missing Column (Injeksi Nilai Statis)
    - source_column: null
      target_column: "system_version"
      transformation_type: "INJECT_DEFAULT"
      default_value: "v2.0"
```

---

## 4. Performance & Resource Strategy

Untuk memproses jutaan baris tanpa memicu kebocoran memori (*memory leak*) atau menghabiskan kapasitas CPU:

* **Keyset Pagination (Watermarking):** Proses *Extract* sangat dilarang menggunakan metode `OFFSET` (seperti `LIMIT 10000 OFFSET 500000`) karena MariaDB harus memindai (*scan*) ulang baris sebelumnya yang menguras *Disk I/O*. Ekstraksi wajib menggunakan klausa `WHERE primary_key > :last_id LIMIT :batch_size`.
* **Generator-Based Processing:** Pembacaan kursor database harus dibungkus dalam fungsi generator (`yield`). Hal ini memastikan setiap iterasi *chunk* membersihkan referensi memori lokal, sehingga *Garbage Collector* (GC) Python secara otomatis dapat menghapus alokasi RAM dari *chunk* sebelumnya.
* **Bulk Loading:** Proses penulisan memanfaatkan metode `cursor.executemany()` yang akan mengompilasi ratusan baris menjadi satu *statement* `INSERT` besar. Ukuran *batch* disarankan antara 5.000 hingga 15.000 baris per eksekusi, disesuaikan dengan konfigurasi `max_allowed_packet` pada MariaDB Target.
* **Disable Profiling:** Selama sesi migrasi, opsi pembuatan log statemen (*query logging*) atau *profiler* pada level driver maupun ORM harus dimatikan agar Python tidak menyimpan riwayat teks SQL di memori.

---

## 5. Error Handling & Logging

Ketahanan sistem (*Resiliency*) menjadi aspek krusial mengingat migrasi skala besar berpotensi terputus akibat fluktuasi jaringan atau interupsi *server*.

* **State Management & Resume Capability:** Aplikasi secara sinkron memperbarui file `state.json` atau tabel *state* kecil di Target DB setiap kali sebuah *chunk* berhasil di-commit. Data yang disimpan mencakup *Last Evaluated Primary Key*. Jika migrasi terputus, aplikasi hanya perlu membaca kunci ini pada *startup* berikutnya untuk melanjutkan eksekusi secara persis pada titik putusnya tanpa menduplikasi data.
* **Atomic Transactions:**
    Setiap *batch* data dimasukkan ke dalam blok transaksi (dikunci dengan `BEGIN` dan diakhiri `COMMIT`). Apabila terdapat anomali pada satu baris dalam *batch*, transaksi di-`ROLLBACK`. Strategi *fallback* dapat diatur untuk mencoba `INSERT` baris demi baris secara lambat pada *batch* yang gagal, demi menemukan dan mencatat anomali spesifik tersebut tanpa menghentikan sisa aliran jutaan data lainnya.
* **Log Pencatatan:**
    Memanfaatkan library `logging` bawaan Python.
    * **STDOUT/Console (INFO):** Menampilkan metrik *real-time* seperti *throughput* (baris per detik), *current chunk*, dan sisa estimasi waktu.
    * **Rotating File (ERROR):** Mencatat gagalnya *casting*, *timeout connection*, atau *constraint violations*. Format log mencakup *Timestamp*, *Batch ID*, *Primary Key*, dan *Stack Trace*, yang dibatasi ukurannya maksimal 50MB per rotasi file guna mencegah disk penuh.