# sync-mail: High-Performance Data Migration & Schema Transformation Engine

`sync-mail` adalah engine migrasi data dan transformasi skema performa tinggi yang dibangun dengan Python 3.14+. Tool ini dirancang khusus untuk menangani migrasi batch skala besar (jutaan baris) antar host MariaDB dengan konsumsi memori yang sangat rendah.

## ✨ Fitur Utama

- **Low-Memory Footprint:** Menggunakan server-side cursors (`SSDictCursor`) dan generator-based streaming untuk memproses data dalam chunk.
- **Schema Transformation:** Menangani konversi tipe data kompleks (contoh: `ENUM` ke `VARCHAR`), injeksi kolom yang hilang, dan normalisasi struktural melalui aturan pemetaan berbasis YAML.
- **TUI (Terminal User Interface):** Antarmuka interaktif berbasis library **Textual** untuk monitoring real-time, introspeksi skema, dan manajemen state.
- **Multi-Table Orchestration:** Mendukung migrasi seluruh skema sekaligus dengan resolusi dependensi otomatis (Topological Sorting) berdasarkan foreign key.
- **Atomic & Resilient:** Menggunakan checkpointing otomatis (`state.json`) untuk memungkinkan penghentian dan melanjutkan migrasi (resume) tanpa kehilangan progres.

## 🚀 Persiapan & Instalasi

### Prasyarat
- Python 3.14+
- MariaDB/MySQL (Source & Target)
- `uv` (rekomendasi untuk manajemen paket)

### Instalasi
```bash
# Clone repository
git clone https://github.com/kentoespdam/sync-mail.git
cd sync-mail

# Buat virtual environment dan install dependensi
uv sync
```

## 🛠 Panduan Operasional (Quickstart)

### 1. Introspeksi Skema & Generate Mapping
Jalankan TUI utama:
```bash
uv run sync-mail
```
Pilih menu **"Introspect Schema → Generate YAML"**:
1. Masukkan DSN Source dan Target (format: `mariadb+pymysql://user:pass@host:port/db`).
2. Masukkan nama tabel (Single-Table) atau aktifkan **Schema Mode** untuk seluruh database.
3. Klik **Generate**. File mapping akan muncul di folder `mappings/`.

### 2. Konfigurasi Pemetaan (YAML)
Buka file YAML yang dihasilkan di `mappings/`. Periksa bagian yang ditandai dengan `ACTION_REQUIRED`. Anda dapat mengubah `transformation_type` (NONE, CAST, INJECT_DEFAULT, dll) sesuai kebutuhan target skema.

### 3. Jalankan Migrasi
Kembali ke menu utama TUI, pilih **"Run Migration Job"**:
1. Masukkan nama job.
2. Masukkan path ke file YAML mapping (atau folder jika dalam Batch Mode).
3. Masukkan DSN Source & Target.
4. Klik **Start**. Pantau progress, throughput, dan ETA secara real-time.

### 4. Melanjutkan Migrasi (Resume)
Jika proses terhenti (abort/crash), cukup jalankan kembali job dengan konfigurasi yang sama. Sistem akan membaca file state di folder `state/` dan otomatis melanjutkan dari Primary Key (PK) terakhir yang sukses di-commit.

## 📖 Dokumentasi Lanjutan
- [Operational Runbook](docs/operational-runbook.md): Panduan lengkap pre-flight, in-flight, dan troubleshooting.
- [Architecture](graphify-out/GRAPH_REPORT.md): Detail teknis dan struktur kode (via Graphify).

## ⚖ Lisensi
Copyright (c) 2026 Google DeepMind / Advanced Agentic Coding. All rights reserved.
