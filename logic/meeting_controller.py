"""
controllers/meeting_controller.py
Layer controller: logika bisnis untuk notulensi rapat (SoC - Controller)
"""

from database.db_manager import DatabaseManager


class MeetingController:
    """Jembatan antara View dan Model untuk entitas Meeting."""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def add_meeting(self, title: str, date: str, time: str,
                    participants: str, agenda: str,
                    discussion: str, decisions: str) -> tuple[bool, str]:
        """Validasi lalu simpan notulensi. Mengembalikan (sukses, pesan)."""
        # Validasi field wajib
        if not title.strip():
            return False, "Judul rapat tidak boleh kosong."
        if not date.strip():
            return False, "Tanggal rapat tidak boleh kosong."
        if not time.strip():
            return False, "Waktu rapat tidak boleh kosong."
        if not participants.strip():
            return False, "Daftar peserta tidak boleh kosong."
        if not agenda.strip():
            return False, "Agenda tidak boleh kosong."

        try:
            new_id = self.db.create_meeting(
                title.strip(), date.strip(), time.strip(),
                participants.strip(), agenda.strip(),
                discussion.strip(), decisions.strip()
            )
            return True, f"Notulensi berhasil disimpan (ID: {new_id})."
        except Exception as e:
            return False, f"Gagal menyimpan: {e}"

    def edit_meeting(self, meeting_id: int, title: str, date: str, time: str,
                     participants: str, agenda: str,
                     discussion: str, decisions: str) -> tuple[bool, str]:
        if not title.strip():
            return False, "Judul rapat tidak boleh kosong."
        try:
            self.db.update_meeting(
                meeting_id, title.strip(), date.strip(), time.strip(),
                participants.strip(), agenda.strip(),
                discussion.strip(), decisions.strip()
            )
            return True, "Notulensi berhasil diperbarui."
        except Exception as e:
            return False, f"Gagal memperbarui: {e}"

    def remove_meeting(self, meeting_id: int) -> tuple[bool, str]:
        try:
            self.db.delete_meeting(meeting_id)
            return True, "Notulensi berhasil dihapus."
        except Exception as e:
            return False, f"Gagal menghapus: {e}"

    def get_all_meetings(self, search: str = "") -> list:
        return self.db.read_all_meetings(search)

    def get_meeting(self, meeting_id: int):
        return self.db.read_meeting_by_id(meeting_id)

    def get_summary(self) -> dict:
        return self.db.get_summary()
