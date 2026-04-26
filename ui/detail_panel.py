"""
views/detail_panel.py
Panel detail notulensi + manajemen tugas (SoC - View)

Mahasiswa : Muhammad Ridho Aidil Furqon
NIM       : F1D02310127
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QScrollArea, QSizePolicy,
    QMessageBox, QFileDialog, QSplitter
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont

from logic.task_controller import TaskController
from ui.task_dialog import TaskDialog
from logic.exporter import export_to_txt, export_to_pdf


class DetailPanel(QWidget):
    """Panel kanan yang menampilkan detail satu notulensi dan task-task-nya."""

    task_changed = Signal()     # emit saat task berubah agar dashboard refresh

    TASK_COLS = ["Deskripsi", "PIC", "Deadline", "Status", "Aksi"]

    def __init__(self, task_ctrl: TaskController, parent=None):
        super().__init__(parent)
        self.task_ctrl = task_ctrl
        self.current_meeting: dict | None = None
        self._build_ui()

    # ──────────────────────────────────────────────────────────── #
    # UI Builder
    # ──────────────────────────────────────────────────────────── #

    def _build_ui(self):
        self.setObjectName("DetailPanel")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Placeholder (saat belum ada rapat dipilih)
        self.placeholder = QLabel("← Pilih notulensi dari daftar\nuntuk melihat detailnya")
        self.placeholder.setObjectName("PlaceholderLabel")
        self.placeholder.setAlignment(Qt.AlignCenter)
        root.addWidget(self.placeholder)

        # Container detail (tersembunyi awalnya)
        self.detail_container = QWidget()
        self.detail_container.hide()
        detail_root = QVBoxLayout(self.detail_container)
        detail_root.setContentsMargins(0, 0, 0, 0)
        detail_root.setSpacing(0)

        # ── Header detail ─────────────────────────────────────
        header = QFrame()
        header.setObjectName("DetailHeader")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(20, 16, 20, 12)

        title_row = QHBoxLayout()
        self.title_lbl = QLabel("Judul Rapat")
        self.title_lbl.setObjectName("DetailTitle")
        title_row.addWidget(self.title_lbl)
        title_row.addStretch()

        export_btn = QPushButton("📤 Export")
        export_btn.setObjectName("BtnSecondary")
        export_btn.clicked.connect(self._on_export)
        title_row.addWidget(export_btn)
        header_layout.addLayout(title_row)

        meta_row = QHBoxLayout()
        self.date_lbl  = QLabel()
        self.date_lbl.setObjectName("MetaLabel")
        self.participants_lbl = QLabel()
        self.participants_lbl.setObjectName("MetaLabel")
        self.participants_lbl.setWordWrap(True)
        meta_row.addWidget(self.date_lbl)
        meta_row.addWidget(QLabel("·"))
        meta_row.addWidget(self.participants_lbl, 1)
        header_layout.addLayout(meta_row)

        detail_root.addWidget(header)

        # ── Scrollable notulensi content ─────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setObjectName("DetailScroll")

        notes_widget = QWidget()
        notes_layout = QVBoxLayout(notes_widget)
        notes_layout.setContentsMargins(20, 16, 20, 8)
        notes_layout.setSpacing(12)

        for attr, label in [
            ("agenda_lbl",     "📌 Agenda"),
            ("discussion_lbl", "💬 Hasil Diskusi"),
            ("decisions_lbl",  "✅ Keputusan"),
        ]:
            section = QFrame()
            section.setObjectName("NoteSection")
            s_layout = QVBoxLayout(section)
            s_layout.setContentsMargins(12, 10, 12, 10)
            s_layout.setSpacing(4)
            head = QLabel(label)
            head.setObjectName("NoteSectionHead")
            body = QLabel()
            body.setObjectName("NoteSectionBody")
            body.setWordWrap(True)
            body.setTextInteractionFlags(Qt.TextSelectableByMouse)
            s_layout.addWidget(head)
            s_layout.addWidget(body)
            notes_layout.addWidget(section)
            setattr(self, attr, body)

        notes_layout.addStretch()
        scroll.setWidget(notes_widget)
        detail_root.addWidget(scroll, 1)

        # ── Tabel Tugas ──────────────────────────────────────
        task_header = QFrame()
        task_header.setObjectName("TaskTableHeader")
        task_header_layout = QHBoxLayout(task_header)
        task_header_layout.setContentsMargins(16, 10, 16, 10)
        task_lbl = QLabel("📋 Tugas Tindak Lanjut")
        task_lbl.setObjectName("SectionLabel")
        add_task_btn = QPushButton("+ Tambah Tugas")
        add_task_btn.setObjectName("BtnPrimary")
        add_task_btn.clicked.connect(self._on_add_task)
        task_header_layout.addWidget(task_lbl)
        task_header_layout.addStretch()
        task_header_layout.addWidget(add_task_btn)
        detail_root.addWidget(task_header)

        self.task_table = QTableWidget()
        self.task_table.setObjectName("TaskTable")
        self.task_table.setColumnCount(len(self.TASK_COLS))
        self.task_table.setHorizontalHeaderLabels(self.TASK_COLS)
        self.task_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.task_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.task_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.task_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.task_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.task_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.task_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.task_table.setAlternatingRowColors(True)
        self.task_table.setMinimumHeight(180)
        detail_root.addWidget(self.task_table)

        root.addWidget(self.detail_container)

    # ──────────────────────────────────────────────────────────── #
    # Public API
    # ──────────────────────────────────────────────────────────── #

    def load_meeting(self, meeting: dict):
        """Tampilkan detail notulensi yang dipilih."""
        self.current_meeting = meeting
        self.placeholder.hide()
        self.detail_container.show()

        self.title_lbl.setText(meeting["title"])
        self.date_lbl.setText(f"🗓 {meeting['date']}  ⏰ {meeting['time']}")
        self.participants_lbl.setText(f"👥 {meeting['participants']}")
        self.agenda_lbl.setText(meeting["agenda"] or "—")
        self.discussion_lbl.setText(meeting["discussion"] or "—")
        self.decisions_lbl.setText(meeting["decisions"] or "—")

        self._load_tasks()

    def clear(self):
        self.current_meeting = None
        self.detail_container.hide()
        self.placeholder.show()

    # ──────────────────────────────────────────────────────────── #
    # Internal helpers
    # ──────────────────────────────────────────────────────────── #

    def _load_tasks(self):
        if not self.current_meeting:
            return
        tasks = self.task_ctrl.get_tasks_for_meeting(self.current_meeting["id"])
        self.task_table.setRowCount(0)
        for row, t in enumerate(tasks):
            self.task_table.insertRow(row)
            self.task_table.setItem(row, 0, QTableWidgetItem(t["description"]))
            self.task_table.setItem(row, 1, QTableWidgetItem(t["pic"]))
            self.task_table.setItem(row, 2, QTableWidgetItem(t["deadline"]))

            status_item = QTableWidgetItem(t["status"])
            if t["status"] == "Selesai":
                status_item.setForeground(QColor("#22c55e"))
            else:
                from datetime import date
                if t["deadline"] < date.today().isoformat():
                    status_item.setForeground(QColor("#ef4444"))
                else:
                    status_item.setForeground(QColor("#f97316"))
            self.task_table.setItem(row, 3, status_item)

            # Kolom Aksi: tombol toggle + hapus
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(4, 2, 4, 2)
            action_layout.setSpacing(4)

            toggle_btn = QPushButton("✓" if t["status"] == "Belum Selesai" else "↩")
            toggle_btn.setObjectName("BtnToggle")
            toggle_btn.setToolTip("Tandai Selesai" if t["status"] == "Belum Selesai" else "Tandai Belum Selesai")
            toggle_btn.setFixedWidth(32)
            toggle_btn.clicked.connect(lambda _, tid=t["id"]: self._on_toggle_task(tid))

            edit_btn = QPushButton("✏")
            edit_btn.setObjectName("BtnEdit")
            edit_btn.setFixedWidth(32)
            edit_btn.clicked.connect(lambda _, td=dict(t): self._on_edit_task(td))

            del_btn = QPushButton("🗑")
            del_btn.setObjectName("BtnDanger")
            del_btn.setFixedWidth(32)
            del_btn.clicked.connect(lambda _, tid=t["id"]: self._on_delete_task(tid))

            action_layout.addWidget(toggle_btn)
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(del_btn)
            self.task_table.setCellWidget(row, 4, action_widget)

    # ──────────────────────────────────────────────────────────── #
    # Slots / event handlers
    # ──────────────────────────────────────────────────────────── #

    def _on_add_task(self):
        if not self.current_meeting:
            return
        dlg = TaskDialog(self)
        if dlg.exec():
            data = dlg.get_form_data()
            ok, msg = self.task_ctrl.add_task(
                self.current_meeting["id"],
                data["description"], data["pic"], data["deadline"]
            )
            if ok:
                self._load_tasks()
                self.task_changed.emit()
            else:
                QMessageBox.warning(self, "Gagal", msg)

    def _on_edit_task(self, task_data: dict):
        dlg = TaskDialog(self, task_data)
        if dlg.exec():
            data = dlg.get_form_data()
            ok, msg = self.task_ctrl.edit_task(
                task_data["id"], data["description"],
                data["pic"], data["deadline"], data["status"]
            )
            if ok:
                self._load_tasks()
                self.task_changed.emit()
            else:
                QMessageBox.warning(self, "Gagal", msg)

    def _on_toggle_task(self, task_id: int):
        ok, msg = self.task_ctrl.toggle_status(task_id)
        if ok:
            self._load_tasks()
            self.task_changed.emit()

    def _on_delete_task(self, task_id: int):
        reply = QMessageBox.question(
            self, "Konfirmasi Hapus",
            "Yakin ingin menghapus tugas ini?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            ok, msg = self.task_ctrl.remove_task(task_id)
            if ok:
                self._load_tasks()
                self.task_changed.emit()

    def _on_export(self):
        if not self.current_meeting:
            return
        tasks = self.task_ctrl.get_tasks_for_meeting(self.current_meeting["id"])
        tasks_list = [dict(t) for t in tasks]
        meeting_dict = dict(self.current_meeting)

        filepath, selected_filter = QFileDialog.getSaveFileName(
            self, "Ekspor Notulensi",
            f"Notulensi_{meeting_dict['title'].replace(' ', '_')}",
            "PDF Files (*.pdf);;Text Files (*.txt)"
        )
        if not filepath:
            return

        if "pdf" in selected_filter.lower() or filepath.endswith(".pdf"):
            if not filepath.endswith(".pdf"):
                filepath += ".pdf"
            ok, msg = export_to_pdf(meeting_dict, tasks_list, filepath)
        else:
            if not filepath.endswith(".txt"):
                filepath += ".txt"
            ok, msg = export_to_txt(meeting_dict, tasks_list, filepath)

        if ok:
            QMessageBox.information(self, "Export Berhasil", msg)
        else:
            QMessageBox.warning(self, "Export Gagal", msg)
