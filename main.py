"""
Smart Meeting Notes - Aplikasi Notulensi Pintar
Entry point utama aplikasi
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui.main_window import MainWindow
from database.db_manager import DatabaseManager


def load_stylesheet(app: QApplication) -> None:
    """Memuat file QSS eksternal untuk styling aplikasi."""
    qss_path = os.path.join(os.path.dirname(__file__), "assets", "style.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Aplikasi Notulensi")
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # Inisialisasi database
    db = DatabaseManager()
    db.initialize()

    # Muat stylesheet eksternal
    load_stylesheet(app)

    # Tampilkan jendela utama
    window = MainWindow(db)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
