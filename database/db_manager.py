"""
models/database.py
Layer database: semua operasi SQLite (SoC - Model)
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional


class DatabaseManager:
    """Mengelola koneksi dan operasi SQLite untuk Smart Meeting Notes."""

    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "meeting_notes.db")

    def __init__(self):
        self.conn: Optional[sqlite3.Connection] = None

    # ------------------------------------------------------------------ #
    # Koneksi
    # ------------------------------------------------------------------ #

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.DB_PATH)
        conn.row_factory = sqlite3.Row          # akses kolom by name
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def initialize(self) -> None:
        """Membuat tabel-tabel jika belum ada."""
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS meetings (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    title       TEXT    NOT NULL,
                    date        TEXT    NOT NULL,
                    time        TEXT    NOT NULL,
                    participants TEXT   NOT NULL,
                    agenda      TEXT    NOT NULL,
                    discussion  TEXT    NOT NULL,
                    decisions   TEXT    NOT NULL,
                    created_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
                );

                CREATE TABLE IF NOT EXISTS tasks (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    meeting_id   INTEGER NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
                    description  TEXT    NOT NULL,
                    pic          TEXT    NOT NULL,
                    deadline     TEXT    NOT NULL,
                    status       TEXT    NOT NULL DEFAULT 'Belum Selesai',
                    created_at   TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
                );
            """)

    # ------------------------------------------------------------------ #
    # CRUD Meetings
    # ------------------------------------------------------------------ #

    def create_meeting(self, title: str, date: str, time: str,
                       participants: str, agenda: str,
                       discussion: str, decisions: str) -> int:
        """Menyimpan notulensi baru. Mengembalikan id baris baru."""
        sql = """
            INSERT INTO meetings (title, date, time, participants, agenda, discussion, decisions)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with self._connect() as conn:
            cur = conn.execute(sql, (title, date, time, participants, agenda, discussion, decisions))
            return cur.lastrowid

    def read_all_meetings(self, search: str = "") -> list[sqlite3.Row]:
        """Mengambil semua notulensi, opsional filter pencarian."""
        sql = """
            SELECT * FROM meetings
            WHERE title LIKE ? OR participants LIKE ? OR date LIKE ?
            ORDER BY date DESC, time DESC
        """
        pattern = f"%{search}%"
        with self._connect() as conn:
            return conn.execute(sql, (pattern, pattern, pattern)).fetchall()

    def read_meeting_by_id(self, meeting_id: int) -> Optional[sqlite3.Row]:
        with self._connect() as conn:
            return conn.execute("SELECT * FROM meetings WHERE id=?", (meeting_id,)).fetchone()

    def update_meeting(self, meeting_id: int, title: str, date: str, time: str,
                       participants: str, agenda: str,
                       discussion: str, decisions: str) -> None:
        sql = """
            UPDATE meetings
            SET title=?, date=?, time=?, participants=?, agenda=?, discussion=?, decisions=?
            WHERE id=?
        """
        with self._connect() as conn:
            conn.execute(sql, (title, date, time, participants, agenda, discussion, decisions, meeting_id))

    def delete_meeting(self, meeting_id: int) -> None:
        """Hapus notulensi (cascade ke tasks)."""
        with self._connect() as conn:
            conn.execute("DELETE FROM meetings WHERE id=?", (meeting_id,))

    # ------------------------------------------------------------------ #
    # CRUD Tasks
    # ------------------------------------------------------------------ #

    def create_task(self, meeting_id: int, description: str, pic: str, deadline: str) -> int:
        sql = """
            INSERT INTO tasks (meeting_id, description, pic, deadline)
            VALUES (?, ?, ?, ?)
        """
        with self._connect() as conn:
            cur = conn.execute(sql, (meeting_id, description, pic, deadline))
            return cur.lastrowid

    def read_tasks_by_meeting(self, meeting_id: int) -> list[sqlite3.Row]:
        with self._connect() as conn:
            return conn.execute(
                "SELECT * FROM tasks WHERE meeting_id=? ORDER BY deadline",
                (meeting_id,)
            ).fetchall()

    def read_all_pending_tasks(self) -> list[sqlite3.Row]:
        """Semua tugas belum selesai lintas rapat, diurutkan deadline."""
        sql = """
            SELECT t.*, m.title AS meeting_title
            FROM tasks t
            JOIN meetings m ON t.meeting_id = m.id
            WHERE t.status = 'Belum Selesai'
            ORDER BY t.deadline
        """
        with self._connect() as conn:
            return conn.execute(sql).fetchall()

    def update_task(self, task_id: int, description: str, pic: str,
                    deadline: str, status: str) -> None:
        sql = """
            UPDATE tasks SET description=?, pic=?, deadline=?, status=? WHERE id=?
        """
        with self._connect() as conn:
            conn.execute(sql, (description, pic, deadline, status, task_id))

    def toggle_task_status(self, task_id: int) -> None:
        with self._connect() as conn:
            row = conn.execute("SELECT status FROM tasks WHERE id=?", (task_id,)).fetchone()
            if row:
                new_status = "Selesai" if row["status"] == "Belum Selesai" else "Belum Selesai"
                conn.execute("UPDATE tasks SET status=? WHERE id=?", (new_status, task_id))

    def delete_task(self, task_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))

    # ------------------------------------------------------------------ #
    # Statistik Dashboard
    # ------------------------------------------------------------------ #

    def get_summary(self) -> dict:
        with self._connect() as conn:
            total_meetings = conn.execute("SELECT COUNT(*) FROM meetings").fetchone()[0]
            pending_tasks  = conn.execute(
                "SELECT COUNT(*) FROM tasks WHERE status='Belum Selesai'"
            ).fetchone()[0]
            last_meeting   = conn.execute(
                "SELECT title, date FROM meetings ORDER BY date DESC, time DESC LIMIT 1"
            ).fetchone()
            overdue_tasks  = conn.execute(
                "SELECT COUNT(*) FROM tasks WHERE status='Belum Selesai' AND deadline < date('now')"
            ).fetchone()[0]

        return {
            "total_meetings": total_meetings,
            "pending_tasks":  pending_tasks,
            "overdue_tasks":  overdue_tasks,
            "last_meeting":   dict(last_meeting) if last_meeting else None,
        }
