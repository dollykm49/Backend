from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def generate_report(user_id: str, comic_id: str, grading_result: dict, report_dir: Path) -> Path:
    """Generate a simple PDF grading report."""
    
    report_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = report_dir / "grading_report.pdf"

    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    w, h = letter
    y = h - 72

    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawString(72, y, "ComicVault Grading Report")

    # Basic info
    y -= 30
    c.setFont("Helvetica", 11)
    c.drawString(72, y, f"User ID: {user_id}")
    y -= 18
    c.drawString(72, y, f"Comic ID: {comic_id}")

    # Final grade
    y -= 30
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, y, f"Final Grade: {grading_result.get('final', 'N/A')}")

    # Confidence
    conf = grading_result.get("confidence")
    if conf is not None:
        c.setFont("Helvetica", 11)
        c.drawString(260, y, f"Confidence: {int(conf * 100)}%")

    # Subgrades
    y -= 30
    c.setFont("Helvetica-Bold", 14)
    c.drawString(72, y, "Subgrades")
    y -= 18
    c.setFont("Helvetica", 11)

    sub = grading_result.get("subgrades", {})
    for label in ["corners", "spine", "surface", "centering", "color"]:
        c.drawString(80, y, f"{label.capitalize():<12}: {sub.get(label, 'N/A')}")
        y -= 16

    # Notes
    y -= 24
    notes = grading_result.get("notes", "")
    if notes:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(72, y, "Grader Notes")
        y -= 18
        c.setFont("Helvetica", 11)

        for line in _wrap_text(notes, 90):
            c.drawString(80, y, line)
            y -= 14
            if y < 72:  # new page
                c.showPage()
                y = h - 72
                c.setFont("Helvetica", 11)

    c.showPage()
    c.save()

    return pdf_path


def _wrap_text(text: str, max_chars: int):
    """Simple line wrapping helper for PDF rendering."""
    words = text.split()
    line = []
    length = 0

    for word in words:
        if length + len(word) + 1 > max_chars:
            yield " ".join(line)
            line = [word]
            length = len(word)
        else:
            line.append(word)
            length += len(word) + 1

    if line:
        yield " ".join(line)

  
