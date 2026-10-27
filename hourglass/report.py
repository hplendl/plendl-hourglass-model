"""Render the markdown report to PDF with reportlab (no browser needed)."""
import re
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak

def _esc(s):
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return re.sub(r"`([^`]+)`", r"<font face='Courier'>\1</font>", s)

def write_pdf(path, md_lines, yearly=None, hist=None, images=()):
    st = getSampleStyleSheet(); body = st["BodyText"]; body.fontSize = 9; body.leading = 11.5
    doc = SimpleDocTemplate(path, pagesize=landscape(letter), leftMargin=.6*inch, rightMargin=.6*inch, topMargin=.5*inch, bottomMargin=.5*inch)
    flow, table = [], []
    def flush():
        if table:
            rows = [[Paragraph(_esc(c.strip()), body) for c in r] for r in table]
            t = Table(rows, repeatRows=1)
            t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), .3, colors.grey), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8ecf3")),
                                   ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 1)]))
            flow.extend([t, Spacer(1, 6)]); table.clear()
    for ln in md_lines:
        if ln.startswith("|"):
            cells = ln.strip("|").split("|")
            if not all(set(c.strip()) <= set("-") for c in cells):
                table.append(cells)
            continue
        flush()
        if ln.startswith("!["):
            m = re.search(r"\((.+?)\)", ln); img = next((i for i in images if i.endswith(m.group(1))), None)
            if img:
                flow += [Image(img, width=9.2*inch, height=9.2*inch*(4.5/12 if "context" in img else 6.5/12)), Spacer(1, 6)]
        elif ln.startswith("# "):
            flow.append(Paragraph(_esc(ln[2:]), st["Title"]))
        elif ln.startswith("## "):
            flow.append(Paragraph(_esc(ln[3:]), st["Heading2"]))
        elif ln.strip():
            flow.append(Paragraph(_esc(ln.lstrip("- ")) if not ln.startswith("- ") else "&bull; " + _esc(ln[2:]), body))
    flush()
    doc.build(flow)
