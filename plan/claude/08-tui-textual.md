# Issue: 08 - TUI (Textual) Frontend

## 🎯 Tujuan
Membangun antarmuka terminal interaktif berbasis library **Textual** sebagai pintu masuk utama operator. TUI hanya **mengkonsumsi** event bus dari engine dan **memanggil** entrypoint orchestrator — TIDAK BOLEH ada logika migrasi, validasi mapping, atau koneksi DB yang ditulis ulang di layer TUI. Tujuannya: separation of concerns yang ketat, sehingga engine bisa diuji headless tanpa TUI, dan TUI bisa diganti future tanpa menyentuh engine.

## 🔗 Dependensi
- Issue 03 (Auto-YAML) — TUI memanggil `generate_mapping()`.
- Issue 04 (Mapping Loader) — untuk preview YAML sebelum run.
- Issue 05 (Checkpoint) — untuk tampilan inspect state.
- Issue 07 (Orchestrator) — entrypoint utama yang TUI panggil.
- Issue 01 (Foundation) — event bus.

## 📝 Alur Kerja / Logika Sistem (Step-by-Step)

**Langkah 1: Buat aplikasi root di `src/sync_mail/tui/app.py`.**
- Definisikan class `SyncMailApp` yang turun dari `textual.app.App`.
- Tetapkan key bindings global: `q` untuk quit, `r` untuk refresh layar.
- Mount layar awal: `MenuScreen`.
- Sediakan fungsi `run()` standalone yang dipanggil oleh `main.py`.

**Langkah 2: Buat menu utama di `src/sync_mail/tui/screens/menu.py`.**
- List opsi vertikal:
  1. **"Introspect schema → generate YAML"** → push `IntrospectScreen`.
  2. **"Run migration job"** → push `MigrateScreen`.
  3. **"Inspect last state"** → push `InspectScreen`.
  4. **"Quit"** → exit.
- Navigasi pakai panah atas/bawah + Enter, atau angka 1–4.

**Langkah 3: Buat layar introspeksi di `src/sync_mail/tui/screens/introspect.py`.**
- Form input: source DSN (host, port, user, password, database), target DSN, source_table, target_table, output path (default `mappings/<source>_to_<target>.yaml`).
- Tombol "Generate" → trigger `auto_yaml.generate_mapping()` di **worker thread** (Textual menyediakan `app.run_worker()` atau `@work` decorator). Jangan blocking event loop UI utama.
- Saat berjalan: tampilkan spinner. Saat selesai: tampilkan path file hasil dan tombol "Open editor" (opsional, panggil `$EDITOR`).
- Jika error: tampilkan exception message dengan format yang ramah operator.

**Langkah 4: Buat layar migrasi di `src/sync_mail/tui/screens/migrate.py`.**
- Layout:
  - **Header**: nama job, source → target.
  - **ProgressBar** total rows (estimasi awal dari `COUNT(*)`).
  - **Panel metrics**: throughput (rows/sec), ETA, rows committed, current PK, batch number.
  - **RichLog panel** untuk event stream (scroll otomatis ke bawah).
- Subscribe ke `EventBus` dari engine. Setiap event yang masuk:
  - Karena event datang dari worker thread (orchestrator), **wajib pakai `app.call_from_thread(update_ui_func)`** untuk update UI. Textual reactive system tidak thread-safe jika dipanggil langsung dari worker.
  - `JobStarted` → set total estimasi & nama job.
  - `BatchCommitted` → update progress bar, throughput, ETA, current PK.
  - `JobCompleted` → tampilkan ringkasan akhir + warna hijau.
  - `JobAborted` → tampilkan error + warna merah + tombol "View state.json".
- Tombol "Abort" → kirim sinyal SIGINT ke proses sendiri (atau set flag di orchestrator) supaya orchestrator graceful shutdown.

**Langkah 5: Buat layar inspect state di `src/sync_mail/tui/screens/inspect.py`.**
- Tampilkan list file di folder `state/*.state.json`.
- Pilih satu → tampilkan isi terformat: status, last_pk, batches_committed, error trace (jika aborted), timestamp started/updated.
- Berguna saat operator ingin cek status sebelum decide resume / fix.

**Langkah 6: Buat custom widgets di `src/sync_mail/tui/widgets/`.**
- `progress.py`: widget gabungan progress bar + ETA + throughput sliding window. Reactive attribute `rows_done`, `total_rows`, `throughput`.
- `log_panel.py`: wrapper di atas `RichLog` Textual dengan auto-scroll dan filter level (toggle INFO/ERROR via key binding).

**Langkah 7: Pastikan orchestrator dipanggil di worker thread, bukan main thread.**
- `MigrationJob.run()` adalah blocking call (loop sinkron). Kalau dijalankan di main thread Textual → UI freeze.
- Solusi: di `MigrateScreen.action_start()`, pakai `self.run_worker(job.run, thread=True)` agar engine berjalan di thread terpisah, sementara UI tetap responsif.

**Langkah 8: Test manual UX.**
- Resize terminal kecil & besar — pastikan layout tetap rapi.
- Mock event bus dengan event dummy → progress bar update real-time, latency UI < 1 detik.
- Test tombol Abort di tengah migrasi — pastikan engine benar-benar berhenti dan state file tersimpan.

## ✅ Kriteria Penerimaan (Acceptance Criteria)
- [ ] `uv run main.py` membuka TUI dan navigasi antar layar (menu → introspect → migrate → inspect) berjalan mulus.
- [ ] Resize terminal tidak membuat TUI crash.
- [ ] Saat migration job berjalan, progress bar & throughput update real-time dengan delay < 1 detik.
- [ ] Tombol "Abort" di MigrateScreen menghentikan job dengan checkpoint tersimpan; layar Inspect langsung menampilkan status `aborted`.
- [ ] Worker thread tidak men-update UI langsung — semua via `call_from_thread()`.
- [ ] TUI tidak meng-import `pymysql`, `ruamel.yaml`, atau modul DB/transformer langsung — hanya `sync_mail.pipeline.orchestrator` dan `sync_mail.observability.events`.
- [ ] Saat orchestrator melempar exception, TUI menangkap dan menampilkan error message dengan format yang readable, bukan stack trace mentah.

## 🤖 SOP Eksekusi (Wajib Dibaca)

**PENTING: Sebelum mengeksekusi penulisan kode untuk task ini, Anda wajib mencari referensi terbaru. Ikuti urutan prioritas berikut:**

1. **JALAN PERTAMA: `/graphify query`** — Gunakan selalu untuk pemindaian file atau mencari logika aplikasi. Hindari pemindaian file secara rekursif (`find`, `ls -R`, dll).
2. **JALAN KEDUA: `context7`** — Selalu utamakan `context7` untuk mendapatkan *best practice*, dokumentasi library Python mutakhir, dan pola optimasi agar kode yang dihasilkan *up-to-date*, aman, dan berkinerja tinggi.
3. **JALAN KETIGA: Pencarian Internet** — Gunakan pencarian internet hanya jika `context7` tidak memberikan informasi yang cukup.

**Prioritas riset untuk task ini:**
- Dokumentasi Textual mutakhir (`App`, `Screen`, `Widget`, reactive attributes, `@work` decorator, `call_from_thread`)
- Pola integrasi worker thread untuk long-running task non-async
- Widget bawaan terbaru: `ProgressBar`, `DataTable`, `RichLog`
