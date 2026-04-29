# Operational Runbook: sync-mail Migration

Dokumen ini berisi panduan langkah-demi-langkah bagi operator untuk menjalankan migrasi data menggunakan `sync-mail` di lingkungan produksi.

## 📋 Pre-Flight Checklist (Sebelum Migration Window)

Lakukan pengecekan berikut minimal 24 jam sebelum jadwal migrasi:

1. **Backup Target Database:** Lakukan backup penuh pada database target menggunakan `mysqldump` atau snapshot storage.
2. **Konfigurasi Database:**
   - Pastikan `max_allowed_packet` di MariaDB target ≥ 64MB untuk mendukung batch loading besar.
   - Periksa `wait_timeout` dan `interactive_timeout` agar koneksi tidak terputus saat proses lama.
3. **Persiapan Source:**
   - Pastikan user database memiliki akses `SELECT` pada `information_schema` dan tabel target.
   - Koordinasikan pembekuan data (read-only mode) jika memungkinkan selama migrasi.
4. **Validasi Network:** Lakukan ping test dari server `sync-mail` ke host source dan target. Pastikan latensi rendah dan tidak ada packet loss.
5. **Disk Space:** Pastikan storage di server target mencukupi untuk menampung data baru beserta index-nya.
6. **Dry Run:** Jalankan migrasi untuk 1000 baris pertama atau menggunakan tabel kecil untuk memvalidasi aturan transformasi di YAML.

## 🚀 In-Flight Monitoring

Saat migrasi sedang berjalan, perhatikan indikator berikut di TUI:

- **Throughput (rows/sec):** Jika throughput turun drastis, periksa beban CPU pada database target.
- **ETA:** Perkirakan apakah waktu selesai masih dalam koridor maintenance window.
- **Last PK:** Catat PK terakhir jika Anda harus menghentikan proses secara manual.
- **Logs:** Pantau file log di `logs/sync-mail.log` menggunakan `tail -f`.

## 🏁 Post-Flight Verification

Setelah TUI menunjukkan status "Completed":

1. **Row Count Verification:**
   ```sql
   -- Jalankan di Source
   SELECT COUNT(*) FROM table_name;
   -- Jalankan di Target
   SELECT COUNT(*) FROM table_name;
   ```
   Jumlah harus persis sama.
2. **Data Integrity Sampling:** Pilih 100 row secara acak dan bandingkan nilai kolom-kolom kritikal antara source dan target.
3. **Constraint Integrity:** Jalankan `CHECK TABLE table_name` dan `ANALYZE TABLE table_name` di database target.
4. **Log Audit:** Pastikan tidak ada "BatchFailed" atau "Warning" yang terlewat di file log.

## 🛠 Troubleshooting

| Masalah | Solusi |
| :--- | :--- |
| **"Packet too large"** | Turunkan `batch_size` di file YAML mapping (mis. dari 10000 ke 1000). |
| **"Resume gagal: state file mismatch"** | Jangan mengubah struktur tabel atau file mapping setelah job berjalan. Jika terpaksa diubah, hapus file `.state.json` terkait dan mulai dari awal. |
| **"Connection timeout"** | Periksa firewall atau restart service database. `sync-mail` akan mencoba resume dari PK terakhir setelah koneksi kembali. |
| **"Constraint violation (Duplicate entry)"** | Terjadi jika ada data ganda di target yang bertabrakan dengan source. Bersihkan tabel target atau gunakan `TRUNCATE` sebelum memulai ulang. |

## 📞 Eskalasi
Jika ditemukan masalah sistemik yang tidak tercantum di sini, hubungi Tim Platform / Developer `sync-mail`.
