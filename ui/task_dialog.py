"""
views/task_dialog.py
Dialog form untuk tambah/edit tugas tindak lanjut (SoC - View)
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QDateEdit, QPushButton,
    QFrame, QComboBox, QTextEdit
)
from PySide6.QtCore import QDate


class TaskDialog(QDialog):
    """Dialog untuk menambah atau mengedit tugas tindak lanjut."""

    STATUS_OPTIONS = ["Belum Selesai", "Selesai"]

    def __init__(self, parent=None, task_data: dict = None):
        super().__init__(parent)
        self.task_data = task_data
        self._build_ui()
        if task_data:
            self._populate_fields(task_data)

    def _build_ui(self):
        is_edit = self.task_data is not None
        self.setWindowTitle("Edit Tugas" if is_edit else "Tambah Tugas Baru")
        self.setMinimumWidth(480)
        self.setObjectName("MeetingDialog")

        root = QVBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # ── Header ──────────────────────────────────────────────
        header = QFrame()
        header.setObjectName("DialogHeader")
        hl = QVBoxLayout(header)
        title_lbl = QLabel("✏️ Edit Tugas" if is_edit else "✅ Tambah Tugas Baru")
        title_lbl.setObjectName("DialogTitle")
        hl.addWidget(title_lbl)
        root.addWidget(header)

        # ── Form ────────────────────────────────────────────────
        form_widget = QFrame()
        form_widget.setObjectName("DialogFormWidget")
        form_layout = QFormLayout(form_widget)
        form_layout.setContentsMargins(28, 20, 28, 20)
        form_layout.setSpacing(14)

        # Field 1: Deskripsi tugas
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Deskripsikan tugas yang harus dilakukan...")
        self.desc_input.setObjectName("FormTextArea")
        self.desc_input.setFixedHeight(90)
        form_layout.addRow("Deskripsi Tugas *", self.desc_input)

        # Field 2: Penanggung jawab
        self.pic_input = QLineEdit()
        self.pic_input.setPlaceholderText("Nama penanggung jawab tugas")
        self.pic_input.setObjectName("FormInput")
        form_layout.addRow("Penanggung Jawab *", self.pic_input)

        # Field 3: Deadline
        self.deadline_input = QDateEdit()
        self.deadline_input.setObjectName("FormInput")
        self.deadline_input.setCalendarPopup(True)
        self.deadline_input.setDate(QDate.currentDate())
        self.deadline_input.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow("Deadline *", self.deadline_input)

        # Field 4: Status (hanya tampil saat edit)
        self.status_combo = QComboBox()
        self.status_combo.setObjectName("FormInput")
        self.status_combo.addItems(self.STATUS_OPTIONS)
        if is_edit:
            form_layout.addRow("Status", self.status_combo)

        root.addWidget(form_widget)

        # ── Tombol ──────────────────────────────────────────────
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
        self.desc_input.setPlainText(data.get("description", ""))
        self.pic_input.setText(data.get("pic", ""))
        deadline_str = data.get("deadline", "")
        if deadline_str:
            self.deadline_input.setDate(QDate.fromString(deadline_str, "yyyy-MM-dd"))
        idx = self.STATUS_OPTIONS.index(data.get("status", "Belum Selesai"))
        self.status_combo.setCurrentIndex(idx)

    def get_form_data(self) -> dict:
        return {
            "description": self.desc_input.toPlainText(),
            "pic":         self.pic_input.text(),
            "deadline":    self.deadline_input.date().toString("yyyy-MM-dd"),
            "status":      self.status_combo.currentText(),
        }
