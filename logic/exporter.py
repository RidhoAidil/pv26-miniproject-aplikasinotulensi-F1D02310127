"""
utils/exporter.py
Utilitas ekspor notulensi ke PDF dan TXT (SoC - Utility)
"""

import os
from datetime import datetime


def export_to_txt(meeting: dict, tasks: list, filepath: str) -> tuple[bool, str]:
    """Ekspor notulensi ke file teks terformat."""
    try:
        separator = "=" * 60
        lines = [
            separator,
            "          NOTULENSI RAPAT",
            "      Smart Meeting Notes",
            separator,
            f"Judul Rapat   : {meeting['title']}",
            f"Tanggal       : {meeting['date']}",
            f"Waktu         : {meeting['time']}",
            f"Peserta       : {meeting['participants']}",
            "",
            "── AGENDA ──────────────────────────────────────────",
            meeting["agenda"],
            "",
            "── HASIL DISKUSI ───────────────────────────────────",
            meeting["discussion"],
            "",
            "── KEPUTUSAN ───────────────────────────────────────",
            meeting["decisions"],
        ]

        if tasks:
            lines += [
                "",
                "── TINDAK LANJUT / TUGAS ───────────────────────────",
            ]
            for i, t in enumerate(tasks, 1):
                status_mark = "✓" if t["status"] == "Selesai" else "○"
                lines.append(
                    f"{i}. [{status_mark}] {t['description']}"
                    f"\n     PIC: {t['pic']}  |  Deadline: {t['deadline']}"
                    f"  |  Status: {t['status']}"
                )

        lines += [
            "",
            separator,
            f"Diekspor pada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "Oleh  : Muhammad Ridho Aidil Furqon | F1D02310127",
            separator,
        ]

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return True, f"Berhasil diekspor ke:\n{filepath}"
    except Exception as e:
        return False, f"Gagal mengekspor: {e}"


def export_to_pdf(meeting: dict, tasks: list, filepath: str) -> tuple[bool, str]:
    """
    Ekspor ke PDF menggunakan QPrinter (PySide6 built-in).
    Dipanggil dari view setelah mendapat filepath dari QFileDialog.
    Fungsi ini membangun HTML lalu menggunakan QPrinter.
    """
    try:
        from PySide6.QtPrintSupport import QPrinter, QPrintDialog
        from PySide6.QtGui import QTextDocument
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QSizeF, Qt

        task_rows = ""
        for t in tasks:
            status_style = "color:#22c55e;" if t["status"] == "Selesai" else "color:#f97316;"
            task_rows += f"""
            <tr>
                <td>{t['description']}</td>
                <td>{t['pic']}</td>
                <td>{t['deadline']}</td>
                <td style="{status_style} font-weight:bold;">{t['status']}</td>
            </tr>"""

        task_section = ""
        if tasks:
            task_section = f"""
            <h3 style="color:#1e3a5f; border-bottom:1px solid #93c5fd; padding-bottom:4px;">
                Tindak Lanjut / Tugas</h3>
            <table border="1" cellspacing="0" cellpadding="6"
                   style="width:100%; border-collapse:collapse; font-size:12px;">
                <thead style="background:#1e3a5f; color:white;">
                    <tr>
                        <th>Deskripsi</th><th>PIC</th>
                        <th>Deadline</th><th>Status</th>
                    </tr>
                </thead>
                <tbody>{task_rows}</tbody>
            </table>"""

        html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  body {{ font-family: Arial, sans-serif; font-size: 13px; color: #1f2937; margin: 0; }}
  h1   {{ color: #1e3a5f; font-size: 20px; }}
  h3   {{ color: #1e3a5f; margin-top: 18px; }}
  .meta td {{ padding: 3px 8px; }}
  .label {{ font-weight: bold; color: #374151; width: 130px; }}
  .section {{ background: #f8faff; border-left: 4px solid #3b82f6;
              padding: 8px 12px; margin: 8px 0; white-space: pre-wrap; }}
  .footer {{ margin-top: 30px; font-size: 11px; color: #6b7280;
             border-top: 1px solid #e5e7eb; padding-top: 8px; }}
</style></head>
<body>
<h1>📋 NOTULENSI RAPAT</h1>
<p style="color:#6b7280; margin-top:-8px;">Smart Meeting Notes</p>
<table class="meta">
  <tr><td class="label">Judul Rapat</td><td>{meeting['title']}</td></tr>
  <tr><td class="label">Tanggal</td><td>{meeting['date']}</td></tr>
  <tr><td class="label">Waktu</td><td>{meeting['time']}</td></tr>
  <tr><td class="label">Peserta</td><td>{meeting['participants']}</td></tr>
</table>
<h3>Agenda</h3>
<div class="section">{meeting['agenda']}</div>
<h3>Hasil Diskusi</h3>
<div class="section">{meeting['discussion']}</div>
<h3>Keputusan</h3>
<div class="section">{meeting['decisions']}</div>
{task_section}
<div class="footer">
  Diekspor: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} &nbsp;|&nbsp;
  Muhammad Ridho Aidil Furqon &nbsp;|&nbsp; F1D02310127
</div>
</body></html>"""

        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(filepath)
        printer.setPageSize(QPrinter.A4)

        doc = QTextDocument()
        doc.setHtml(html)
        doc.print_(printer)

        return True, f"Berhasil diekspor ke PDF:\n{filepath}"
    except Exception as e:
        return False, f"Gagal mengekspor PDF: {e}"
