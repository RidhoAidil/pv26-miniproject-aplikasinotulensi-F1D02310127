"""
controllers/task_controller.py
Layer controller: logika bisnis untuk tugas/tindak lanjut rapat (SoC - Controller)
"""

from datetime import date, datetime
from database.db_manager import DatabaseManager


class TaskController:
    """Jembatan antara View dan Model untuk entitas Task."""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def add_task(self, meeting_id: int, description: str,
                 pic: str, deadline: str) -> tuple[bool, str]:
        """Validasi lalu simpan tugas baru."""
        if not description.strip():
            return False, "Deskripsi tugas tidak boleh kosong."
        if not pic.strip():
            return False, "Penanggung jawab tidak boleh kosong."
        if not deadline.strip():
            return False, "Deadline tidak boleh kosong."

        try:
            new_id = self.db.create_task(meeting_id, description.strip(),
                                         pic.strip(), deadline.strip())
            return True, f"Tugas berhasil ditambahkan (ID: {new_id})."
        except Exception as e:
            return False, f"Gagal menambahkan tugas: {e}"

    def edit_task(self, task_id: int, description: str,
                  pic: str, deadline: str, status: str) -> tuple[bool, str]:
        if not description.strip():
            return False, "Deskripsi tugas tidak boleh kosong."
        try:
            self.db.update_task(task_id, description.strip(),
                                pic.strip(), deadline.strip(), status)
            return True, "Tugas berhasil diperbarui."
        except Exception as e:
            return False, f"Gagal memperbarui tugas: {e}"

    def toggle_status(self, task_id: int) -> tuple[bool, str]:
        try:
            self.db.toggle_task_status(task_id)
            return True, "Status tugas berhasil diubah."
        except Exception as e:
            return False, f"Gagal mengubah status: {e}"

    def remove_task(self, task_id: int) -> tuple[bool, str]:
        try:
            self.db.delete_task(task_id)
            return True, "Tugas berhasil dihapus."
        except Exception as e:
            return False, f"Gagal menghapus tugas: {e}"

    def get_tasks_for_meeting(self, meeting_id: int) -> list:
        return self.db.read_tasks_by_meeting(meeting_id)

    def get_pending_tasks(self) -> list:
        return self.db.read_all_pending_tasks()

    def get_overdue_tasks(self) -> list:
        """Tugas yang sudah lewat deadline dan belum selesai."""
        today = date.today().isoformat()
        all_pending = self.db.read_all_pending_tasks()
        return [t for t in all_pending if t["deadline"] < today]
