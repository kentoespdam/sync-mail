# Issue: 02 - Database Connection Manager

## 🎯 Tujuan
Menyediakan satu pintu masuk koneksi database yang **selalu** menggunakan server-side cursor (tidak pernah membuffer hasil query di memori klien) dan **selalu** mematikan logging query di driver. Modul ini akan dipakai oleh introspection, extractor, dan loader, sehingga semua jalur akses MariaDB tunduk pada aturan low-memory yang sama.

## 🔗 Dependensi
- Issue 01 (Setup Foundation) — paket `sync_mail` dan logger sudah tersedia.

## 📝 Alur Kerja / Logika Sistem (Step-by-Step)

**Langkah 1: Buat modul `src/sync_mail/db/connection.py`.**
- Modul ini adalah satu-satunya tempat yang boleh meng-import `pymysql` di seluruh proyek. Modul lain hanya boleh berinteraksi via fungsi/factory yang disediakan di sini.

**Langkah 2: Definisikan fungsi factory `connect(role, dsn_params)`.**
- Parameter `role` boleh bernilai `"source"` atau `"target"`. Tujuannya supaya tuning future (mis. read-only flag di source) terpusat di sini.
- Parameter `dsn_params` adalah dictionary dengan host, port, user, password, database.
- Saat membuka koneksi, **wajib** mengaktifkan `cursorclass=SSDictCursor` (Server-Side Dictionary Cursor). Konsep: server MariaDB akan mengirim baris secara streaming, bukan men-dump semua hasil ke memori klien sekaligus.
- Set `autocommit=False` — kita kelola transaksi manual per batch (BEGIN/COMMIT/ROLLBACK).
- Set `init_command` untuk mematikan query log session-level di driver (mis. `SET SESSION sql_log_off=1` jika privilege mengizinkan, atau setara). Tujuannya: tidak ada teks SQL yang ditahan di memori atau di-log ke disk.
- Pastikan opsi character set diatur eksplisit (mis. `utf8mb4`) untuk menghindari masalah encoding.

**Langkah 3: Bungkus koneksi dengan context manager.**
- Sediakan helper `connection_scope(role, dsn_params)` berbasis `contextlib.contextmanager`. Tugasnya: yield koneksi, lalu `close()` di blok `finally` walaupun exception terjadi. Ini mencegah koneksi nyangkut saat error.

**Langkah 4: Sediakan helper transaksi atomic untuk koneksi target.**
- Tambahkan fungsi `begin(conn)`, `commit(conn)`, `rollback(conn)` (atau context manager `transaction(conn)`).
- `transaction(conn)` saat masuk: kirim `BEGIN`. Saat keluar normal: `COMMIT`. Saat exception: `ROLLBACK` lalu re-raise.
- Loader di Issue 06 akan memakai helper ini agar batch insert benar-benar atomic.

**Langkah 5: Tangani error koneksi dengan exception domain.**
- Jika `pymysql.connect()` gagal, bungkus error aslinya menjadi `sync_mail.errors.ConnectionError` dengan context `{role, host, port, database}` lalu re-raise. Jangan biarkan exception mentah PyMySQL bocor ke layer lain.

**Langkah 6: Smoke test manual.**
- Buat skrip dummy di terminal yang membuka koneksi source, fetch satu baris dari `information_schema.tables`, lalu tutup. Pastikan tidak error.
- Coba `BEGIN ... ROLLBACK` di koneksi target. Pastikan tidak error.
- Cek file log — tidak boleh ada teks SQL muncul di sana.

## ✅ Kriteria Penerimaan (Acceptance Criteria)
- [ ] Koneksi source berhasil membuka cursor `SSDictCursor` dan fetch 1 baris dari `information_schema.tables` tanpa error.
- [ ] Koneksi target dapat menjalankan `BEGIN ... ROLLBACK` lewat helper transaksi tanpa error.
- [ ] Tidak ada teks SQL yang muncul di `logs/sync-mail.log` saat koneksi dibuka, fetch, dan ditutup.
- [ ] Saat DSN salah (host tidak ada), error yang muncul adalah `sync_mail.errors.ConnectionError`, bukan exception mentah PyMySQL.
- [ ] Verifikasi memori kasar (mis. dengan `psutil`): fetch satu baris dari tabel `information_schema` tidak menyebabkan lonjakan RAM proporsional ukuran tabel.

## 🤖 SOP Eksekusi (Wajib Dibaca)

**PENTING: Sebelum mengeksekusi penulisan kode untuk task ini, Anda wajib mencari referensi terbaru. Ikuti urutan prioritas berikut:**

1. **JALAN PERTAMA: `/graphify query`** — Gunakan selalu untuk pemindaian file atau mencari logika aplikasi. Hindari pemindaian file secara rekursif (`find`, `ls -R`, dll).
2. **JALAN KEDUA: `context7`** — Selalu utamakan `context7` untuk mendapatkan *best practice*, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan *up-to-date*, aman, dan berkinerja tinggi.
3. **JALAN KETIGA: Pencarian Internet** — Gunakan pencarian internet hanya jika `context7` tidak memberikan informasi yang cukup.

**Prioritas riset untuk task ini:**
- Dokumentasi mutakhir `PyMySQL` `SSDictCursor`
- Opsi koneksi MariaDB 11.x untuk menonaktifkan query log/profiling driver-side
- Praktik connection lifecycle (context manager, ConnectionPool jika relevan) di Python 3.14
