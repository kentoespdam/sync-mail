# Issue: 01 - Setup Proyek, Dependency & Pondasi Observability

## 🎯 Tujuan
Membangun pondasi proyek `sync-mail` agar dapat dijalankan dan siap menjadi basis seluruh fase berikutnya. Setelah task ini selesai, struktur paket Python sudah terbentuk, dependency utama terpasang, sistem logging dapat menulis ke STDOUT dan file dengan rotasi, dan kerangka exception terstandarisasi sudah tersedia. Selain itu, kontrak event bus untuk komunikasi antara mesin migrasi dengan TUI sudah didefinisikan, sehingga modul-modul berikutnya bisa langsung memakainya tanpa perlu refactor besar.

## 🔗 Dependensi
Tidak ada (ini adalah fondasi awal). Cukup pastikan Python 3.14 tersedia dan repo ini sudah ter-clone.

## 📝 Alur Kerja / Logika Sistem (Step-by-Step)

**Langkah 1: Konfigurasi `pyproject.toml`.**
- Tambahkan blok dependency yang memuat: konektor MariaDB (`PyMySQL`), `SQLAlchemy` versi 2.x untuk layer Core saja, parser YAML yang bisa menjaga urutan dan komentar (`ruamel.yaml`), serta library TUI `textual`.
- Pin minor version supaya hasil install reproducible saat menjelang migration window.
- Aktifkan layout berbasis direktori `src/` dengan menyatakan ke setuptools bahwa root paket berada di `src/`.
- (Opsional) Daftarkan entrypoint `console_scripts` agar perintah `sync-mail` di terminal langsung memanggil fungsi `main()`.

**Langkah 2: Bersihkan dan rapikan `main.py`.**
- Hapus boilerplate bawaan PyCharm.
- Buat satu fungsi `main()` yang isinya hanya memanggil entrypoint TUI di paket `sync_mail.tui.app`. `main.py` **bukan** tempat logika migrasi — ia hanyalah pintu masuk.

**Langkah 3: Bentuk struktur paket di `src/sync_mail/`.**
- Buat folder paket dengan submodul kosong (file `__init__.py`) untuk: `config/`, `db/`, `pipeline/`, `state/`, `reconciliation/`, `observability/`, `errors/`, `tui/`.
- File `__init__.py` di root paket cukup mengekspor versi (mis. `__version__`); jangan ada side-effect import berat.

**Langkah 4: Definisikan hierarki exception di `src/sync_mail/errors/exceptions.py`.**
- Buat satu base class `MigrationError`. Semua exception domain harus turun dari sini.
- Turunkan menjadi: `MappingError` (masalah konfigurasi YAML), `ConnectionError` (gagal konek DB), `IntrospectionError` (gagal baca `information_schema`), `BatchFailedError` (transaksi batch gagal di-commit), `ResumeError` (state.json korup atau tidak konsisten).
- Setiap exception sebaiknya menerima dictionary konteks (mis. `job_name`, `batch_id`, `last_pk`) sehingga logging bisa menampilkan informasi terstruktur tanpa parsing string.

**Langkah 5: Setup logging di `src/sync_mail/observability/logger.py`.**
- Sediakan fungsi `configure_logging(level, log_dir)` yang dipanggil sekali saat aplikasi start.
- Pasang dua handler:
  - **StreamHandler ke STDOUT** dengan level INFO. Format ringkas, fokus pada metrik (job, throughput, ETA, current PK).
  - **RotatingFileHandler** ke `logs/sync-mail.log` dengan level ERROR. Maksimal 50 MB per file, simpan 5 file backup. Format mencakup timestamp, batch_id, primary_key, dan stack trace lengkap.
- Pastikan logger root **tidak** memuat teks SQL apapun — ini kontrak ketat dari PRD.

**Langkah 6: Definisikan kontrak event bus di `src/sync_mail/observability/events.py`.**
- Buat enum/konstanta tipe event: `JobStarted`, `BatchCommitted`, `BatchFailed`, `JobCompleted`, `JobAborted`.
- Sediakan class `EventBus` minimalis dengan API `publish(event)` dan `subscribe(handler)`. Implementasi internal pakai `queue.Queue` thread-safe agar TUI Textual nanti bisa konsumsi event dari worker thread tanpa race condition.
- Setiap event membawa payload dictionary (job_name, batch_id, rows, last_pk, throughput, error, dll. — sesuaikan tipe).

**Langkah 7: Verifikasi instalasi.**
- Jalankan `uv sync` di virtualenv Python 3.14 dan pastikan tidak ada error.
- Coba `uv run main.py`. TUI boleh tampil blank — yang penting tidak crash.

## ✅ Kriteria Penerimaan (Acceptance Criteria)
- [ ] `uv sync` berhasil pada Python 3.14 tanpa warning kritikal.
- [ ] `uv run main.py` membuka TUI tanpa error (boleh layar kosong).
- [ ] Logger berhasil menulis pesan ERROR ke `logs/sync-mail.log` dan rotasi terverifikasi dengan dummy data > 50 MB.
- [ ] Tidak ada query SQL yang muncul di file log saat aplikasi startup.
- [ ] Hierarki exception dapat di-import dari `sync_mail.errors` dan masing-masing menerima context dict.
- [ ] `EventBus` dapat menerima `publish()` dan mengirim ke subscriber tanpa blocking di thread utama.

## 🤖 SOP Eksekusi (Wajib Dibaca)
PENTING: Selalu utamakan mencari referensi terbaru menggunakan `context 7` untuk pencarian data *best practice*, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan *up-to-date*, aman, dan berkinerja tinggi
kemudian melalui internet jika diperlukan. Khusus untuk task ini, prioritaskan riset: layout `src/` modern di `pyproject.toml` setuptools, konfigurasi `RotatingFileHandler` untuk Python 3.14, pola custom exception hierarchy dengan context, dan dokumentasi `queue.Queue` thread-safe pattern. Prioritaskan menggunakan `context7` untuk pencarian dokumentasi eksternal, dan **prioritaskan selalu mencoba mencari informasi melalui `/graphify query` sebelum menggunakan `file_scanner`** untuk memahami konteks internal codebase.
