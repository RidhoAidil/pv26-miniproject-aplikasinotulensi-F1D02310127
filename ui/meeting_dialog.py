"""
views/meeting_dialog.py
Dialog form untuk tambah/edit notulensi rapat (SoC - View)
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QTextEdit, QDateEdit, QTimeEdit,
    QPushButton, QFrame, QScrollArea, QWidget
)
from PySide6.QtCore import Qt, QDate, QTime
from PySide6.QtGui import QFont


class MeetingDialog(QDialog):
    """Dialog untuk menambah atau mengedit notulensi rapat."""

    def __init__(self, parent=None, meeting_data: dict = None):
        super().__init__(parent)
        self.meeting_data = meeting_data  # None = mode tambah
        self._build_ui()
        if meeting_data:
            self._populate_fields(meeting_data)

    def _build_ui(self):
        is_edit = self.meeting_data is not None
        self.setWindowTitle("Edit Notulensi" if is_edit else "Tambah Notulensi Baru")
        self.setMinimumSize(620, 620)
        self.setObjectName("MeetingDialog")

        root = QVBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # ── Header ──────────────────────────────────────────────
        header = QFrame()
        header.setObjectName("DialogHeader")
        header_layout = QVBoxLayout(header)
        title_lbl = QLabel("✏️ Edit Notulensi" if is_edit else "📋 Tambah Notulensi Baru")
        title_lbl.setObjectName("DialogTitle")
        header_layout.addWidget(title_lbl)
        root.addWidget(header)

        # ── Scroll area untuk form ───────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        form_widget = QWidget()
        form_widget.setObjectName("DialogFormWidget")
        form_layout = QFormLayout(form_widget)
        form_layout.setContentsMargins(28, 20, 28, 20)
        form_layout.setSpacing(14)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Field 1: Judul rapat
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Contoh: Rapat Mingguan Divisi IT")
        self.title_input.setObjectName("FormInput")
        form_layout.addRow("Judul Rapat *", self.title_input)

        # Field 2 & 3: Tanggal & Waktu (satu baris)
        dt_widget = QWidget()
        dt_layout = QHBoxLayout(dt_widget)
        dt_layout.setContentsMargins(0, 0, 0, 0)
        dt_layout.setSpacing(10)

        self.date_input = QDateEdit()
        self.date_input.setObjectName("FormInput")
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("yyyy-MM-dd")

        self.time_input = QTimeEdit()
        self.time_input.setObjectName("FormInput")
        self.time_input.setTime(QTime.currentTime())
        self.time_input.setDisplayFormat("HH:mm")

        dt_layout.addWidget(self.date_input)
        dt_layout.addWidget(QLabel("⏰"))
        dt_layout.addWidget(self.time_input)
        form_layout.addRow("Tanggal & Waktu *", dt_widget)

        # Field 4: Peserta
        self.participants_input = QLineEdit()
        self.participants_input.setPlaceholderText("Pisahkan dengan koma, cth: Budi, Sari, Andi")
        self.participants_input.setObjectName("FormInput")
        form_layout.addRow("Peserta Rapat *", self.participants_input)

        # Field 5: Agenda
        self.agenda_input = QTextEdit()
        self.agenda_input.setPlaceholderText("Tulis agenda rapat di sini...")
        self.agenda_input.setObjectName("FormTextArea")
        self.agenda_input.setFixedHeight(80)
        form_layout.addRow("Agenda *", self.agenda_input)

        # Field 6: Hasil Diskusi
        self.discussion_input = QTextEdit()
        self.discussion_input.setPlaceholderText("Ringkasan hasil diskusi selama rapat...")
        self.discussion_input.setObjectName("FormTextArea")
        self.discussion_input.setFixedHeight(100)
        form_layout.addRow("Hasil Diskusi", self.discussion_input)

        # Field 7: Keputusan
        self.decisions_input = QTextEdit()
        self.decisions_input.setPlaceholderText("Keputusan-keputusan yang diambil dalam rapat...")
        self.decisions_input.setObjectName("FormTextArea")
        self.decisions_input.setFixedHeight(80)
        form_layout.addRow("Keputusan", self.decisions_input)

        scroll.setWidget(form_widget)
        root.addWidget(scroll)

        # ── Tombol aksi ─────────────────────────────────────────
        btn_frame = QFrame()
        btn_frame.setObjectName("DialogFooter")
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setContentsMargins(24, 12, 24, 12)

        self.cancel_btn = QPushButton("Batal")
        self.cancel_btn.setObjectName("BtnSecondary")
        self.cancel_btn.clicked.connect(self.reject)

        self.save_btn = QPushButton("💾 Simpan" if is_edit else "➕ Tambahkan")
        self.save_btn.setObjectName("BtnPrimary")
        self.save_btn.setDefault(True)
        self.save_btn.clicked.connect(self.accept)

        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        root.addWidget(btn_frame)

    def _populate_fields(self, data: dict):
        """Isi form dengan data yang sudah ada (mode edit)."""
        self.title_input.setText(data.get("title", ""))
        self.date_input.setDate(QDate.fromString(data.get("date", ""), "yyyy-MM-dd"))
        self.time_input.setTime(QTime.fromString(data.get("time", ""), "HH:mm"))
        self.participants_input.setText(data.get("participants", ""))
        self.agenda_input.setPlainText(data.get("agenda", ""))
        self.discussion_input.setPlainText(data.get("discussion", ""))
        self.decisions_input.setPlainText(data.get("decisions", ""))

    def get_form_data(self) -> dict:
        """Mengembalikan data form sebagai dictionary."""
        return {
            "title":        self.title_input.text(),
            "date":         self.date_input.date().toString("yyyy-MM-dd"),
            "time":         self.time_input.time().toString("HH:mm"),
            "participants": self.participants_input.text(),
            "agenda":       self.agenda_input.toPlainText(),
            "discussion":   self.discussion_input.toPlainText(),
            "decisions":    self.decisions_input.toPlainText(),
        }
