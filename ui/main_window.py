"""
views/main_window.py
Jendela utama aplikasi Smart Meeting Notes (SoC - View)
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QFrame, QSplitter, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction

from database.db_manager import DatabaseManager
from logic.meeting_controller import MeetingController
from logic.task_controller import TaskController
from ui.meeting_dialog import MeetingDialog
from ui.detail_panel import DetailPanel

# Identitas Mahasiswa — tidak bisa diubah pengguna
STUDENT_NAME = "Muhammad Ridho Aidil Furqon"
STUDENT_NIM  = "F1D02310127"


class MainWindow(QMainWindow):
    """Jendela utama: daftar rapat di kiri, detail di kanan."""

    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db           = db
        self.meeting_ctrl = MeetingController(db)
        self.task_ctrl    = TaskController(db)
        self._selected_meeting_id = None

        self.setWindowTitle("Aplikasi Notulensi")
        self.setMinimumSize(1050, 680)
        self.setObjectName("MainWindow")

        self._build_menubar()
        self._build_ui()
        self._load_meetings()
        self._update_dashboard()

        self._reminder_timer = QTimer(self)
        self._reminder_timer.timeout.connect(self._check_reminders)
        self._reminder_timer.start(60_000)
        self._check_reminders()

    # ── Menu Bar ──────────────────────────────────────────────── #

    def _build_menubar(self):
        menubar = self.menuBar()
        menubar.setObjectName("AppMenuBar")

        file_menu = menubar.addMenu("File")
        new_action = QAction("Notulensi Baru", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._on_add_meeting)
        file_menu.addAction(new_action)
        file_menu.addSeparator()
        exit_action = QAction("Keluar", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        about_menu = menubar.addMenu("Tentang")
        about_action = QAction("Tentang Aplikasi", self)
        about_action.triggered.connect(self._show_about)
        about_menu.addAction(about_action)

    # ── UI Builder ─────────────────────────────────────────────── #

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ────────────────────────────────────────────────
        header = QFrame()
        header.setObjectName("AppHeader")
        header.setFixedHeight(58)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(20, 0, 16, 0)
        hl.setSpacing(10)

        logo = QLabel("📝  Aplikasi Notulensi")
        logo.setObjectName("AppLogoLabel")
        hl.addWidget(logo)
        hl.addStretch()

        self.stat_total   = self._make_badge("0", "Rapat",   "📅")
        self.stat_pending = self._make_badge("0", "Pending", "⏳")
        self.stat_overdue = self._make_badge("0", "Overdue", "🔴")
        for b in (self.stat_total, self.stat_pending, self.stat_overdue):
            hl.addWidget(b)

        root.addWidget(header)

        # ── Splitter ──────────────────────────────────────────────
        splitter = QSplitter(Qt.Horizontal)
        splitter.setObjectName("MainSplitter")
        splitter.setHandleWidth(1)

        # Panel kiri
        left = QFrame()
        left.setObjectName("LeftPanel")
        left.setMinimumWidth(240)
        left.setMaximumWidth(320)
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(0)

        sf = QFrame()
        sf.setObjectName("SearchFrame")
        sfl = QHBoxLayout(sf)
        sfl.setContentsMargins(10, 10, 10, 10)
        sfl.setSpacing(8)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari rapat...")
        self.search_input.setObjectName("SearchInput")
        self.search_input.textChanged.connect(self._on_search)

        add_btn = QPushButton("+")
        add_btn.setObjectName("BtnAdd")
        add_btn.setFixedSize(34, 34)
        add_btn.setToolTip("Tambah Notulensi Baru (Ctrl+N)")
        add_btn.clicked.connect(self._on_add_meeting)

        sfl.addWidget(self.search_input, 1)
        sfl.addWidget(add_btn)
        ll.addWidget(sf)

        self.meeting_list = QListWidget()
        self.meeting_list.setObjectName("MeetingList")
        self.meeting_list.itemClicked.connect(self._on_meeting_selected)
        ll.addWidget(self.meeting_list, 1)

        ab = QFrame()
        ab.setObjectName("ListActionBar")
        abl = QHBoxLayout(ab)
        abl.setContentsMargins(10, 8, 10, 8)
        abl.setSpacing(8)

        self.edit_btn   = QPushButton("Edit")
        self.delete_btn = QPushButton("Hapus")
        self.edit_btn.setObjectName("BtnSecondary")
        self.delete_btn.setObjectName("BtnDanger")
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.edit_btn.clicked.connect(self._on_edit_meeting)
        self.delete_btn.clicked.connect(self._on_delete_meeting)

        abl.addWidget(self.edit_btn)
        abl.addWidget(self.delete_btn)
        ll.addWidget(ab)

        # Panel kanan
        self.detail_panel = DetailPanel(self.task_ctrl)
        self.detail_panel.task_changed.connect(self._update_dashboard)

        splitter.addWidget(left)
        splitter.addWidget(self.detail_panel)
        splitter.setSizes([270, 780])
        root.addWidget(splitter, 1)

        # ── Footer — nama & NIM permanen ──────────────────────────
        footer = QFrame()
        footer.setObjectName("AppFooter")
        footer.setFixedHeight(30)
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(16, 0, 16, 0)

        name_lbl = QLabel(f"  {STUDENT_NAME}")
        name_lbl.setObjectName("FooterLabel")

        nim_lbl = QLabel(f"NIM: {STUDENT_NIM}")
        nim_lbl.setObjectName("FooterLabel")

        fl.addWidget(name_lbl)
        fl.addStretch()
        fl.addWidget(nim_lbl)
        root.addWidget(footer)

    # ── Badge helper ───────────────────────────────────────────── #

    def _make_badge(self, value: str, label: str, icon: str) -> QFrame:
        badge = QFrame()
        badge.setObjectName("StatBadge")
        badge.setMinimumWidth(95)

        bl = QHBoxLayout(badge)
        bl.setContentsMargins(10, 4, 10, 4)
        bl.setSpacing(6)

        icon_lbl = QLabel(icon)
        icon_lbl.setObjectName("BadgeIcon")
        icon_lbl.setFixedWidth(20)

        right = QVBoxLayout()
        right.setSpacing(1)

        val_lbl = QLabel(value)
        val_lbl.setObjectName("BadgeValue")

        lbl_lbl = QLabel(label)
        lbl_lbl.setObjectName("BadgeLabel")

        right.addWidget(val_lbl)
        right.addWidget(lbl_lbl)

        bl.addWidget(icon_lbl)
        bl.addLayout(right)

        badge._val_lbl = val_lbl
        return badge

    # ── Data ───────────────────────────────────────────────────── #

    def _load_meetings(self, search: str = ""):
        self.meeting_list.clear()
        meetings = self.meeting_ctrl.get_all_meetings(search)
        for m in meetings:
            item = QListWidgetItem()
            item.setText(f"  {m['title']}\n    {m['date']}  ·  {m['participants'][:35]}")
            item.setData(Qt.UserRole, m["id"])
            self.meeting_list.addItem(item)

    def _update_dashboard(self):
        s = self.meeting_ctrl.get_summary()
        self.stat_total._val_lbl.setText(str(s["total_meetings"]))
        self.stat_pending._val_lbl.setText(str(s["pending_tasks"]))
        self.stat_overdue._val_lbl.setText(str(s["overdue_tasks"]))

    # ── Slots ──────────────────────────────────────────────────── #

    def _on_search(self, text: str):
        self._load_meetings(text)
        self.detail_panel.clear()
        self._selected_meeting_id = None
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)

    def _on_meeting_selected(self, item: QListWidgetItem):
        mid = item.data(Qt.UserRole)
        self._selected_meeting_id = mid
        meeting = self.meeting_ctrl.get_meeting(mid)
        if meeting:
            self.detail_panel.load_meeting(dict(meeting))
        self.edit_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)

    def _on_add_meeting(self):
        dlg = MeetingDialog(self)
        if dlg.exec():
            ok, msg = self.meeting_ctrl.add_meeting(**dlg.get_form_data())
            if ok:
                self._load_meetings(self.search_input.text())
                self._update_dashboard()
            else:
                QMessageBox.warning(self, "Gagal Menyimpan", msg)

    def _on_edit_meeting(self):
        if not self._selected_meeting_id:
            return
        meeting = self.meeting_ctrl.get_meeting(self._selected_meeting_id)
        if not meeting:
            return
        dlg = MeetingDialog(self, dict(meeting))
        if dlg.exec():
            ok, msg = self.meeting_ctrl.edit_meeting(
                self._selected_meeting_id, **dlg.get_form_data()
            )
            if ok:
                self._load_meetings(self.search_input.text())
                self._update_dashboard()
                updated = self.meeting_ctrl.get_meeting(self._selected_meeting_id)
                if updated:
                    self.detail_panel.load_meeting(dict(updated))
            else:
                QMessageBox.warning(self, "Gagal Memperbarui", msg)

    def _on_delete_meeting(self):
        if not self._selected_meeting_id:
            return
        meeting = self.meeting_ctrl.get_meeting(self._selected_meeting_id)
        if not meeting:
            return
        reply = QMessageBox.question(
            self, "Konfirmasi Hapus",
            f"Yakin ingin menghapus notulensi:\n\n\"{meeting['title']}\"?\n\n"
            "Semua tugas terkait juga akan dihapus.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            ok, _ = self.meeting_ctrl.remove_meeting(self._selected_meeting_id)
            if ok:
                self._selected_meeting_id = None
                self.detail_panel.clear()
                self.edit_btn.setEnabled(False)
                self.delete_btn.setEnabled(False)
                self._load_meetings(self.search_input.text())
                self._update_dashboard()

    def _check_reminders(self):
        pass  # reminder overdue bisa ditambahkan sebagai notif di sini

    def _show_about(self):
        QMessageBox.about(
            self, "Tentang Smart Meeting Notes",
            "<h2>Smart Meeting Notes</h2>"
            "<p>Aplikasi notulensi rapat terstruktur dan profesional.</p>"
            "<hr>"
            f"<p><b>Mahasiswa :</b> {STUDENT_NAME}<br>"
            f"<b>NIM &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:</b> {STUDENT_NIM}</p>"
            "<p>Dibuat menggunakan <b>PySide6</b> + <b>SQLite</b><br>"
            "Mata Kuliah: Pemrograman Visual</p>"
        )