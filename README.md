# 📋 Aplikasi Notulensi

> Aplikasi notulensi rapat terstruktur dan profesional berbasis PySide6

---

## 📌 Deskripsi

**Aplikasi Notulensi** adalah aplikasi GUI desktop yang membantu mencatat hasil rapat secara terstruktur, lengkap dengan manajemen tugas tindak lanjut (*to-do* dari hasil rapat), pencarian, ringkasan statistik, dan fitur ekspor ke PDF/TXT.

Aplikasi ini dibangun sebagai Mini Project Mata Kuliah **Pemrograman Visual** dengan menerapkan prinsip **Separation of Concerns (SoC)**.

---

## 👤 Identitas Mahasiswa

| Field | Info |
|---|---|
| **Nama** | Muhammad Ridho Aidil Furqon |
| **NIM** | F1D02310127 |
| **Mata Kuliah** | Pemrograman Visual |

---

## ✨ Fitur Utama

| Fitur | Keterangan |
|---|---|
| 📄 Input Notulensi Terstruktur | 7 field: judul, tanggal, waktu, peserta, agenda, diskusi, keputusan |
| ✅ Manajemen Tugas (Task) | Tambah, edit, toggle status, hapus tugas tindak lanjut per rapat |
| 🔍 Pencarian | Filter notulensi berdasarkan judul, peserta, atau tanggal |
| 📊 Dashboard Ringkasan | Total rapat, tugas pending, tugas overdue, rapat terakhir |
| 📤 Export | Ekspor notulensi ke PDF dan TXT |
| ⏰ Reminder Overdue | Notifikasi otomatis di status bar untuk tugas yang melewati deadline |
| 🎨 Tema Profesional | UI dark navy dengan QSS dari file eksternal |

---

## 🗂️ Struktur Project (SoC)

```
Aplikasi Notulensi/
│
├── main.py                        # Entry point
│
├── database/
│   └── db_manager.py                # Layer Model: semua operasi SQLite
│
├── logic/
│   ├── meeting_controller.py      # Layer Controller: logika bisnis notulensi
│   └── task_controller.py         # Layer Controller: logika bisnis tugas
|   └── exporter.py                # Utilitas ekspor PDF & TXT
│
├── ui/
│   ├── main_window.py             # Jendela utama (Layer View)
│   ├── detail_panel.py            # Panel detail notulensi + tugas
│   ├── meeting_dialog.py          # Dialog tambah/edit notulensi
│   └── task_dialog.py             # Dialog tambah/edit tugas
│
├── style/
│   └── style.qss                  # Stylesheet QSS eksternal
│
├── meeting_notes.db               # Database SQLite (dibuat otomatis)
└── README.md
```

---

## 🗄️ Desain Database

### Tabel `meetings` (7 kolom data + metadata)

| Kolom | Tipe | Keterangan |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `title` | TEXT | Judul rapat |
| `date` | TEXT | Tanggal (YYYY-MM-DD) |
| `time` | TEXT | Waktu (HH:MM) |
| `participants` | TEXT | Daftar peserta |
| `agenda` | TEXT | Agenda rapat |
| `discussion` | TEXT | Hasil diskusi |
| `decisions` | TEXT | Keputusan rapat |
| `created_at` | TEXT | Waktu dibuat |

### Tabel `tasks` (5 kolom data + metadata)

| Kolom | Tipe | Keterangan |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `meeting_id` | INTEGER FK | Referensi ke `meetings.id` (CASCADE DELETE) |
| `description` | TEXT | Deskripsi tugas |
| `pic` | TEXT | Penanggung jawab |
| `deadline` | TEXT | Deadline (YYYY-MM-DD) |
| `status` | TEXT | `Belum Selesai` / `Selesai` |
| `created_at` | TEXT | Waktu dibuat |

---

## 🚀 Cara Menjalankan

### Prasyarat
```bash
pip install PySide6
```

### Jalankan Aplikasi
```bash
cd Aplikasi Notulensi
python main.py
```

> Database `meeting_notes.db` akan dibuat otomatis di direktori project saat pertama kali dijalankan.

---

## 🛠️ Teknologi

- **Python 3.10+**
- **PySide6** — Framework GUI
- **SQLite** — Database lokal
- **QSS** — Styling eksternal

---

## 📎 Link

- 🎬 **YouTube**: *(link video demo)*
