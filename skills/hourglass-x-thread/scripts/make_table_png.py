#!/usr/bin/env python3
"""Render tables from a Predictive Hourglass .md file as phone-legible PNGs (Pillow only).

Usage:
  python3 make_table_png.py Predictive_Hourglass_YYYY-MM-DD.md [--out table.png]
         [--thresholds-out thresholds.png] [--last-year 2045]

- Central projection table: finds the '## Central projection' section, keeps columns
  Year, Debt, Interest, Revenue, Mandatory, r %, I/R %, Flag, and years up to --last-year.
- Thresholds table (optional): the first table containing a 'Hypothesis' header.
Run date is read from the 'Run date:' line (e.g. 'Run date: 5 October 2026.').
"""
import argparse, re, sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
COLS = ["Year", "Debt", "Interest", "Revenue", "Mandatory", "r %", "I/R %", "Flag"]
FOOTER = "Hypotheses under status-quo inertia. Not official. Not advice."

# Repair common mis-encodings (UTF-8 read as cp1252 etc.)
FIXES = {"\u00e2\u20ac\u201d": "\u2014", "\u00e2\u20ac\u201c": "\u2013", "\u00e2\u02c6\u2019": "\u2212",
         "\u00ce\u201d": "\u0394", "\ufffd?\"": "\u2014", "\ufffd^'": "\u2212", "I\"r": "\u0394r"}

def clean(s):
    for k, v in FIXES.items():
        s = s.replace(k, v)
    return s

def parse_tables(md):
    """Return list of (heading, header_list, rows) for every pipe table."""
    tables, heading, cur = [], "", None
    for line in md.splitlines():
        if line.startswith("#"):
            heading = line.lstrip("#").strip()
        if line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cur is None:
                cur = (heading, cells, [])
            elif all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                continue
            else:
                cur[2].append(cells)
        elif cur is not None:
            tables.append(cur); cur = None
    if cur is not None:
        tables.append(cur)
    return tables

def run_date(md):
    m = re.search(r"Run date:\s*([0-9]{1,2} [A-Za-z]+ [0-9]{4})", md)
    if not m:
        return None, None
    d = datetime.strptime(m.group(1), "%d %B %Y")
    return d, f"{d.day} {d.strftime('%b %Y')}"

def font(path, size):
    return ImageFont.truetype(path, size)

def wrap(draw, text, f, maxw):
    words, lines, line = text.split(" "), [], ""
    for w in words:
        t = (line + " " + w).strip()
        if draw.textlength(t, font=f) <= maxw or not line:
            line = t
        else:
            lines.append(line); line = w
    lines.append(line)
    return lines

def wrap_title(draw, text, f, maxw):
    # Prefer breaking right after an em dash so dates/units stay together
    if draw.textlength(text, font=f) > maxw and " \u2014 " in text:
        a, b = text.split(" \u2014 ", 1)
        return wrap(draw, a + " \u2014", f, maxw) + wrap(draw, b, f, maxw)
    return wrap(draw, text, f, maxw)

def render(title, header, rows, out, width=1200, min_h=1200, numeric_from=1,
           numeric_to=None, highlight=lambda r: False, base_size=48):
    pad, gap = 40, 26
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    size = base_size
    while True:  # shrink font until all columns fit
        f, fb = font(FONT, size), font(FONT_B, size)
        widths = [max(tmp.textlength(header[i], font=fb),
                      *[tmp.textlength(r[i], font=fb) for r in rows]) + gap for i in range(len(header))]
        ft = font(FONT_B, int(size * 1.25))
        tl = wrap_title(tmp, title, ft, width - 2 * pad)
        need = pad + int(size * 1.25 * 1.35) * len(tl) + 20 + int(size * 1.6) * (len(rows) + 1) + 30 + int(size * 1.6) + pad
        if (sum(widths) <= width - 2 * pad and need <= min_h) or size <= 14:
            break
        size -= 1
    extra = (width - 2 * pad - sum(widths)) / len(widths)
    widths = [w + extra for w in widths]
    ft, ff = font(FONT_B, int(size * 1.25)), font(FONT, int(size * 0.8))
    tlines = wrap_title(tmp, title, ft, width - 2 * pad)
    th = int(size * 1.25 * 1.35)
    fixed = pad + th * len(tlines) + 20 + 30 + int(size * 1.6) + pad
    rh = max(int(size * 1.6), min(int(size * 2.1), (min_h - fixed) // (len(rows) + 1)))
    height = max(min_h, fixed + rh * (len(rows) + 1))
    img = Image.new("RGB", (width, height), "white")
    d = ImageDraw.Draw(img)
    y = pad
    for ln in tlines:
        d.text((pad, y), ln, font=ft, fill="#111111"); y += th
    y += 20
    numeric_to = len(header) if numeric_to is None else numeric_to
    def row(cells, y, fnt, fill=None, color="#111111"):
        if fill:
            d.rectangle([pad, y, width - pad, y + rh], fill=fill)
        x = pad
        for i, c in enumerate(cells):
            tw = d.textlength(c, font=fnt)
            if numeric_from <= i < numeric_to:   # right-align numbers
                tx = x + widths[i] - gap / 2 - tw
            else:
                tx = x + gap / 2
            d.text((tx, y + (rh - size) / 2 - 2), c, font=fnt, fill=color)
            x += widths[i]
    row(header, y, fb, fill="#1f2a44", color="white"); y += rh
    for k, r in enumerate(rows):
        fill = "#fff1c9" if highlight(r) else ("#f2f4f7" if k % 2 else None)
        row(r, y, fb if highlight(r) else f, fill=fill); y += rh
    d.line([pad, y, width - pad, y], fill="#1f2a44", width=2)
    y += 30
    for ln in wrap(d, FOOTER, ff, width - 2 * pad):
        d.text((pad, y), ln, font=ff, fill="#444444"); y += int(size * 1.1)
    img.save(out)
    return out, img.size, size

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("md")
    ap.add_argument("--out")
    ap.add_argument("--thresholds-out")
    ap.add_argument("--last-year", type=int, default=2045)
    a = ap.parse_args()
    md = clean(open(a.md, encoding="utf-8", errors="replace").read())
    d, label = run_date(md)
    stamp = d.strftime("%Y-%m-%d") if d else "undated"
    tables = parse_tables(md)
    cen = next((t for t in tables if t[0].lower().startswith("central projection")), None)
    if not cen:
        sys.exit("Central projection table not found")
    hdr = cen[1]
    idx = [hdr.index(c) for c in COLS]
    rows = [[r[i] if i < len(r) else "" for i in idx] for r in cen[2]
            if r[0].isdigit() and int(r[0]) <= a.last_year]
    title = f"Predictive Hourglass Model \u2014 Central projection (nominal $T), run {label}"
    out = a.out or f"table_{stamp}.png"
    print(render(title, COLS, rows, out, numeric_from=1, numeric_to=7,
                 highlight=lambda r: bool(r[-1].strip())))
    if a.thresholds_out:
        th = next((t for t in tables if t[1] and t[1][0].lower() == "hypothesis"), None)
        if th:
            print(render(f"Predictive Hourglass Model \u2014 Threshold hypotheses, run {label}",
                         th[1], th[2], a.thresholds_out, width=1600, min_h=620,
                         numeric_from=99, base_size=48, highlight=lambda r: "already" in r[1]))

if __name__ == "__main__":
    main()
