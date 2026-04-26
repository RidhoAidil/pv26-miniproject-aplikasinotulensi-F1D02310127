"""
views/main_window.py
Jendela utama aplikasi Smart Meeting Notes (SoC - View)
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QFrame, QSplitter, QMenuBar, QMenu, QMessageBox,
    QStatusBar, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QDate
from PySide6.QtGui import QAction, QFont, QColor

from database.db_manager import DatabaseManager
from logic.meeting_controller import MeetingController
from logic.task_controller import TaskController
from ui.meeting_dialog import MeetingDialog
from ui.detail_panel import DetailPanel

# Identitas Mahasiswa (tidak bisa diubah pengguna)
STUDENT_NAME = "Muhammad Ridho Aidil Furqon"
STUDENT_NIM  = "F1D02310127"


class MainWindow(QMainWindow):
    """Jendela utama: daftar rapat di kiri, detail di kanan."""

    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db = db
        self.meeting_ctrl = MeetingController(db)
        self.task_ctrl    = TaskController(db)
        self._selected_meeting_id: int | None = None

        self.setWindowTitle("Aplikasi Notulensi")
        self.setMinimumSize(1050, 680)
        self.setObjectName("MainWindow")

        self._build_menubar()
        self._build_ui()
        self._build_statusbar()
        self._load_meetings()
        self._update_dashboard()

        # Reminder: cek overdue tasks setiap 60 detik
        self._reminder_timer = QTimer(self)
        self._reminder_timer.timeout.connect(self._check_reminders)
        self._reminder_timer.start(60_000)
        self._check_reminders()  # langsung cek saat start

    # ──────────────────────────────────────────────────────────── #
    # Menu Bar
    # ──────────────────────────────────────────────────────────── #

    def _build_menubar(self):
        menubar = self.menuBar()
        menubar.setObjectName("AppMenuBar")

        # Menu File
        file_menu = menubar.addMenu("File")
        new_action = QAction("➕ Notulensi Baru", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._on_add_meeting)
        file_menu.addAction(new_action)
        file_menu.addSeparator()
        exit_action = QAction("Keluar", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Menu Tentang
        about_menu = menubar.addMenu("Tentang")
        about_action = QAction("Tentang Aplikasi", self)
        about_action.triggered.connect(self._show_about)
        about_menu.addAction(about_action)

    # ──────────────────────────────────────────────────────────── #
    # UI Builder
    # ──────────────────────────────────────────────────────────── #

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── App Header ────────────────────────────────────────
        app_header = QFrame()
        app_header.setObjectName("AppHeader")
        app_header.setFixedHeight(54)
        header_layout = QHBoxLayout(app_header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        logo_lbl = QLabel("📋  Aplikasi Notulensi")
        logo_lbl.setObjectName("AppLogoLabel")
        header_layout.addWidget(logo_lbl)
        header_layout.addStretch()

        # Stat badges di header (ringkas)
        self.stat_total   = self._stat_badge("📅", "0", "Rapat")
        self.stat_pending = self._stat_badge("⏳", "0", "Pending")
        self.stat_overdue = self._stat_badge("🔴", "0", "Overdue")
        for badge in [self.stat_total, self.stat_pending, self.stat_overdue]:
            header_layout.addWidget(badge)

        main_layout.addWidget(app_header)

        # ── Split: daftar kiri + detail kanan ─────────────────
        splitter = QSplitter(Qt.Horizontal)
        splitter.setObjectName("MainSplitter")
        splitter.setHandleWidth(1)

        # ── Panel kiri ────────────────────────────────────────
        left_panel = QFrame()
        left_panel.setObjectName("LeftPanel")
        left_panel.setMinimumWidth(260)
        left_panel.setMaximumWidth(320)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # Search bar
        search_frame = QFrame()
        search_frame.setObjectName("SearchFrame")
        sf_layout = QHBoxLayout(search_frame)
        sf_layout.setContentsMargins(12, 10, 12, 10)
        sf_layout.setSpacing(8)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari rapat...")
        self.search_input.setObjectName("SearchInput")
        self.search_input.textChanged.connect(self._on_search)

        add_btn = QPushButton("＋")
        add_btn.setObjectName("BtnAdd")
        add_btn.setFixedSize(34, 34)
        add_btn.setToolTip("Tambah Notulensi Baru (Ctrl+N)")
        add_btn.clicked.connect(self._on_add_meeting)

        sf_layout.addWidget(self.search_input, 1)
        sf_layout.addWidget(add_btn)
        left_layout.addWidget(search_frame)

        # Daftar notulensi
        self.meeting_list = QListWidget()
        self.meeting_list.setObjectName("MeetingList")
        self.meeting_list.itemClicked.connect(self._on_meeting_selected)
        left_layout.addWidget(self.meeting_list, 1)

        # Tombol edit/hapus
        action_bar = QFrame()
        action_bar.setObjectName("ListActionBar")
        ab_layout = QHBoxLayout(action_bar)
        ab_layout.setContentsMargins(12, 8, 12, 8)
        ab_layout.setSpacing(8)

        self.edit_btn   = QPushButton("✏  Edit")
        self.delete_btn = QPushButton("🗑  Hapus")
        self.edit_btn.setObjectName("BtnSecondary")
        self.delete_btn.setObjectName("BtnDanger")
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.edit_btn.clicked.connect(self._on_edit_meeting)
        self.delete_btn.clicked.connect(self._on_delete_meeting)

        ab_layout.addWidget(self.edit_btn)
        ab_layout.addWidget(self.delete_btn)
        left_layout.addWidget(action_bar)

        # Panel kanan: detail
        self.detail_panel = DetailPanel(self.task_ctrl)
        self.detail_panel.task_changed.connect(self._update_dashboard)

        splitter.addWidget(left_panel)
        splitter.addWidget(self.detail_panel)
        splitter.setSizes([280, 770])

        main_layout.addWidget(splitter, 1)

        # ── Footer bar: Nama & NIM permanen di bawah ──────────
        footer = QFrame()
        footer.setObjectName("AppFooter")
        footer.setFixedHeight(30)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(16, 0, 16, 0)

        name_lbl = QLabel(f"👤  {STUDENT_NAME}")
        name_lbl.setObjectName("FooterLabel")

        nim_lbl = QLabel(f"NIM: {STUDENT_NIM}")
        nim_lbl.setObjectName("FooterLabel")

        footer_layout.addWidget(name_lbl)
        footer_layout.addStretch()
        footer_layout.addWidget(nim_lbl)
        main_layout.addWidget(footer)

    def _stat_badge(self, icon: str, value: str, label: str) -> QFrame:
        """Stat badge ringkas untuk header bar."""
        badge = QFrame()
        badge.setObjectName("StatBadge")
        layout = QHBoxLayout(badge)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(5)
        val_lbl = QLabel(f"{icon} {value}")
        val_lbl.setObjectName("BadgeValue")
        lbl_lbl = QLabel(label)
        lbl_lbl.setObjectName("BadgeLabel")
        layout.addWidget(val_lbl)
        layout.addWidget(lbl_lbl)
        badge._val_lbl  = val_lbl
        badge._icon     = icon
        return badge

    def _stat_card_UNUSED(self, icon: str, value: str, label: str) -> QFrame:
        card = QFrame()
        card.setObjectName("StatCard")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(8)

        icon_lbl = QLabel(icon)
        icon_lbl.setObjectName("StatIcon")

        text_col = QVBoxLayout()
        val_lbl  = QLabel(value)
        val_lbl.setObjectName("StatValue")
        lbl_lbl  = QLabel(label)
        lbl_lbl.setObjectName("StatLabel")
        text_col.addWidget(val_lbl)
        text_col.addWidget(lbl_lbl)

        layout.addWidget(icon_lbl)
        layout.addLayout(text_col)

        # Simpan referensi ke value label agar bisa diupdate
        card._val_lbl = val_lbl
        return card

    def _build_statusbar(self):
        self.status_bar = QStatusBar()
        self.status_bar.setObjectName("AppStatusBar")
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Siap.")

    # ──────────────────────────────────────────────────────────── #
    # Data Loading
    # ──────────────────────────────────────────────────────────── #

    def _load_meetings(self, search: str = ""):
        self.meeting_list.clear()
        self._meeting_id_map = {}   # row → meeting_id

        meetings = self.meeting_ctrl.get_all_meetings(search)
        for m in meetings:
            item = QListWidgetItem()
            item.setText(f"📋  {m['title']}\n      🗓 {m['date']}  ·  👥 {m['participants'][:30]}")
            item.setData(Qt.UserRole, m["id"])
            self.meeting_list.addItem(item)

        self.status_bar.showMessage(f"{len(meetings)} notulensi ditemukan.")

    def _update_dashboard(self):
        summary = self.meeting_ctrl.get_summary()
        self.stat_total._val_lbl.setText(f"📅 {summary['total_meetings']}")
        self.stat_pending._val_lbl.setText(f"⏳ {summary['pending_tasks']}")
        self.stat_overdue._val_lbl.setText(f"🔴 {summary['overdue_tasks']}")

    # ──────────────────────────────────────────────────────────── #
    # Slots
    # ──────────────────────────────────────────────────────────── #

    def _on_search(self, text: str):
        self._load_meetings(text)
        self.detail_panel.clear()
        self._selected_meeting_id = None
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)

    def _on_meeting_selected(self, item: QListWidgetItem):
        meeting_id = item.data(Qt.UserRole)
        self._selected_meeting_id = meeting_id
        meeting = self.meeting_ctrl.get_meeting(meeting_id)
        if meeting:
            self.detail_panel.load_meeting(dict(meeting))
        self.edit_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)

    def _on_add_meeting(self):
        dlg = MeetingDialog(self)
        if dlg.exec():
            data = dlg.get_form_data()
            ok, msg = self.meeting_ctrl.add_meeting(**data)
            if ok:
                self._load_meetings(self.search_input.text())
                self._update_dashboard()
                self.status_bar.showMessage(msg)
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
            data = dlg.get_form_data()
            ok, msg = self.meeting_ctrl.edit_meeting(self._selected_meeting_id, **data)
            if ok:
                self._load_meetings(self.search_input.text())
                self._update_dashboard()
                updated = self.meeting_ctrl.get_meeting(self._selected_meeting_id)
                if updated:
                    self.detail_panel.load_meeting(dict(updated))
                self.status_bar.showMessage(msg)
            else:
                QMessageBox.warning(self, "Gagal Memperbarui", msg)

    def _on_delete_meeting(self):
        if not self._selected_meeting_id:
            return
        meeting = self.meeting_ctrl.get_meeting(self._selected_meeting_id)
        if not meeting:
            return

        # Konfirmasi penghapusan (QMessageBox)
        reply = QMessageBox.question(
            self, "Konfirmasi Hapus",
            f"Yakin ingin menghapus notulensi:\n\n\"{meeting['title']}\"?\n\n"
            "Semua tugas terkait juga akan dihapus.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            ok, msg = self.meeting_ctrl.remove_meeting(self._selected_meeting_id)
            if ok:
                self._selected_meeting_id = None
                self.detail_panel.clear()
                self.edit_btn.setEnabled(False)
                self.delete_btn.setEnabled(False)
                self._load_meetings(self.search_input.text())
                self._update_dashboard()
                self.status_bar.showMessage(msg)

    def _check_reminders(self):
        """Notifikasi tugas overdue di status bar."""
        overdue = self.task_ctrl.get_overdue_tasks()
        if overdue:
            self.status_bar.showMessage(
                f"⚠️  {len(overdue)} tugas sudah melewati deadline! Segera tindak lanjuti."
            )

    def _show_about(self):
        QMessageBox.about(
            self, "Tentang Smart Meeting Notes",
            "<h2>📋 Smart Meeting Notes</h2>"
            "<p>Aplikasi notulensi rapat terstruktur dan profesional.</p>"
            "<hr>"
            f"<p><b>Mahasiswa :</b> {STUDENT_NAME}<br>"
            f"<b>NIM        :</b> {STUDENT_NIM}</p>"
            "<p>Dibuat menggunakan PySide6 + SQLite<br>"
            "Mata Kuliah: Pemrograman Visual</p>"
        )