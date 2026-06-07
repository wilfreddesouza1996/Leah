#!/usr/bin/env python3
"""Generate a printable PDF posting calendar for the study group.

Each sparrow image/PDF carries its posting date in its filename. This script
scans a source folder, reads the date out of every filename, and renders a
full-month calendar grid as a real PDF, placing a thumbnail of each file on the
day it should be posted.

Usage:
    python3 generate_calendar.py --src assets/sparrows \
        --out june-sparrow-calendar.pdf --month 2026-06

Run `python3 generate_calendar.py --help` for all options.
"""

from __future__ import annotations

import argparse
import calendar
import datetime as dt
import io
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# --- Third-party deps (see requirements.txt) -------------------------------
try:
    from PIL import Image, ImageOps
except ImportError:  # pragma: no cover
    sys.exit("Pillow is required. Install with: pip install -r requirements.txt")

try:  # HEIC/HEIF support (iCloud photos are frequently HEIC)
    import pillow_heif

    pillow_heif.register_heif_opener()
    _HEIC_OK = True
except ImportError:  # pragma: no cover
    _HEIC_OK = False

try:
    import fitz  # PyMuPDF, for rendering the first page of a PDF
    _PDF_OK = True
except ImportError:  # pragma: no cover
    _PDF_OK = False

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tif", ".tiff"}
HEIC_EXTS = {".heic", ".heif"}
PDF_EXTS = {".pdf"}
SUPPORTED_EXTS = IMAGE_EXTS | HEIC_EXTS | PDF_EXTS

MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}
_MONTH_ALT = "|".join(MONTHS)


# --------------------------------------------------------------------------- #
# Date parsing
# --------------------------------------------------------------------------- #
def parse_date(name: str, default_year: int, default_month: int) -> dt.date | None:
    """Best-effort extraction of a date from a filename (without extension).

    Tries, in order: full ISO-ish dates, month-name forms, then bare
    month/day numbers (year defaults to ``default_year``).
    """
    stem = Path(name).stem
    low = stem.lower()

    # 1. ISO-ish: 2026-06-03 / 2026_06_03 / 2026.06.03 / 20260603
    m = re.search(r"(20\d{2})[-_.]?(0[1-9]|1[0-2])[-_.]?(0[1-9]|[12]\d|3[01])", low)
    if m:
        return _safe_date(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    # 2a. Month-name then day: "June 3", "Jun-03", "june 3rd 2026"
    m = re.search(
        rf"\b({_MONTH_ALT})[a-z]*[\s\-_.]*([0-3]?\d)(?:st|nd|rd|th)?(?:[\s\-_.,]+(20\d{{2}}))?",
        low,
    )
    if m:
        year = int(m.group(3)) if m.group(3) else default_year
        return _safe_date(year, MONTHS[m.group(1)], int(m.group(2)))

    # 2b. Day then month-name: "3 June", "03-jun-2026", "3rd June"
    m = re.search(
        rf"\b([0-3]?\d)(?:st|nd|rd|th)?[\s\-_.]+({_MONTH_ALT})[a-z]*(?:[\s\-_.,]+(20\d{{2}}))?",
        low,
    )
    if m:
        year = int(m.group(3)) if m.group(3) else default_year
        return _safe_date(year, MONTHS[m.group(2)], int(m.group(1)))

    # 3. Bare numeric month-day: "06-03", "6.3" (year assumed)
    m = re.search(r"\b(0?[1-9]|1[0-2])[-_./](0?[1-9]|[12]\d|3[01])\b", low)
    if m:
        return _safe_date(default_year, int(m.group(1)), int(m.group(2)))

    return None


def _safe_date(year: int, month: int, day: int) -> dt.date | None:
    try:
        return dt.date(year, month, day)
    except ValueError:
        return None


# --------------------------------------------------------------------------- #
# Thumbnails
# --------------------------------------------------------------------------- #
@dataclass
class Item:
    path: Path
    date: dt.date
    is_pdf: bool


def make_thumbnail(path: Path, max_px: int = 480) -> Image.Image | None:
    """Return an RGB PIL thumbnail for an image or the first page of a PDF."""
    ext = path.suffix.lower()
    try:
        if ext in PDF_EXTS:
            if not _PDF_OK:
                return None
            with fitz.open(path) as doc:
                if doc.page_count == 0:
                    return None
                page = doc.load_page(0)
                # Render at ~150 DPI then downscale for crisp print output.
                pix = page.get_pixmap(matrix=fitz.Matrix(150 / 72, 150 / 72))
                img = Image.open(io.BytesIO(pix.tobytes("png")))
        else:
            img = Image.open(path)
            img = ImageOps.exif_transpose(img)  # honour camera orientation

        img = img.convert("RGB")
        img.thumbnail((max_px, max_px), Image.LANCZOS)
        return img
    except Exception as exc:  # noqa: BLE001 - report and continue
        print(f"  ! could not render thumbnail for {path.name}: {exc}", file=sys.stderr)
        return None


# --------------------------------------------------------------------------- #
# Scanning
# --------------------------------------------------------------------------- #
@dataclass
class ScanResult:
    by_date: dict[dt.date, list[Item]] = field(default_factory=dict)
    unscheduled: list[Path] = field(default_factory=list)
    out_of_range: list[tuple[Path, dt.date]] = field(default_factory=list)


def scan(src: Path, year: int, month: int) -> ScanResult:
    """Place every dated file into ``by_date`` (any date); files without a
    detectable date go to ``unscheduled``. Whether a date is actually shown is
    decided later against the visible grid (which includes adjacent-month days).
    """
    result = ScanResult()
    files = sorted(
        p for p in src.rglob("*")
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS
    )
    for path in files:
        date = parse_date(path.name, year, month)
        if date is None:
            result.unscheduled.append(path)
            continue
        item = Item(path=path, date=date, is_pdf=path.suffix.lower() in PDF_EXTS)
        result.by_date.setdefault(date, []).append(item)
    return result


def build_weeks(year: int, month: int, week_start: str):
    """Return (weeks, weekday-headers) for the month grid."""
    firstweekday = calendar.SUNDAY if week_start == "sun" else calendar.MONDAY
    headers = WEEKDAYS_SUN if week_start == "sun" else WEEKDAYS_MON
    weeks = calendar.Calendar(firstweekday).monthdatescalendar(year, month)
    return weeks, headers


# --------------------------------------------------------------------------- #
# PDF rendering
# --------------------------------------------------------------------------- #
WEEKDAYS_SUN = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
WEEKDAYS_MON = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

POST_BG = (0.93, 0.97, 0.93)       # soft green for days with a post
POST_BORDER = (0.20, 0.55, 0.32)
EMPTY_BG = (0.97, 0.97, 0.97)
SPILL_BG = (0.90, 0.90, 0.90)      # adjacent-month days
GRID = (0.70, 0.70, 0.70)
INK = (0.13, 0.13, 0.13)


def render_pdf(result: ScanResult, out: Path, year: int, month: int,
               week_start: str, title: str) -> None:
    page_w, page_h = landscape(letter)
    c = canvas.Canvas(str(out), pagesize=(page_w, page_h))
    c.setTitle(title)

    margin = 0.45 * inch
    weeks, headers = build_weeks(year, month, week_start)

    # --- Title ---
    c.setFillColorRGB(*INK)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(page_w / 2, page_h - margin - 6, title)

    # --- Layout regions ---
    top = page_h - margin - 34
    footer_h = 30
    bottom = margin + footer_h
    grid_left = margin
    grid_right = page_w - margin
    grid_w = grid_right - grid_left

    header_h = 18
    col_w = grid_w / 7
    rows = len(weeks)
    grid_top = top - header_h
    cell_h = (grid_top - bottom) / rows

    # --- Weekday header ---
    c.setFont("Helvetica-Bold", 10)
    for i, label in enumerate(headers):
        x = grid_left + i * col_w
        c.setFillColorRGB(*INK)
        c.drawCentredString(x + col_w / 2, top - 13, label)

    # --- Day cells ---
    for r, week in enumerate(weeks):
        for ci, day in enumerate(week):
            x = grid_left + ci * col_w
            y = grid_top - (r + 1) * cell_h
            in_month = day.month == month
            items = result.by_date.get(day, [])

            # Cell background
            if items:
                c.setFillColorRGB(*POST_BG)
            elif not in_month:
                c.setFillColorRGB(*SPILL_BG)
            else:
                c.setFillColorRGB(*EMPTY_BG)
            c.rect(x, y, col_w, cell_h, stroke=0, fill=1)

            # Highlight border on post days
            if items:
                c.setStrokeColorRGB(*POST_BORDER)
                c.setLineWidth(1.6)
            else:
                c.setStrokeColorRGB(*GRID)
                c.setLineWidth(0.6)
            c.rect(x, y, col_w, cell_h, stroke=1, fill=0)

            # Day number
            c.setFont("Helvetica-Bold", 9)
            c.setFillColorRGB(*INK) if in_month else c.setFillColorRGB(0.55, 0.55, 0.55)
            c.drawString(x + 4, y + cell_h - 12, str(day.day))

            if items:
                _draw_day_content(c, items, x, y, col_w, cell_h)

    _draw_footer(c, result, grid_left, margin, grid_w)
    c.showPage()
    c.save()


_DATE_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}[\s_-]*")
IMG_DOT = (0.20, 0.55, 0.32)   # green
PDF_DOT = (0.80, 0.27, 0.22)   # red
LIST_FONT = "Helvetica"
LIST_SIZE = 5.6
LINE_H = 7.0
MAX_LINES = 6


def _short_label(name: str) -> str:
    """Drop the date prefix and extension, leaving the descriptive part."""
    return _DATE_PREFIX.sub("", Path(name).stem).strip() or Path(name).stem


_TRAIL_PAREN = re.compile(r"\s*(\([^()]*\))\s*$")


def _clip(c, text: str, max_w: float, font: str, size: float) -> str:
    if c.stringWidth(text, font, size) <= max_w:
        return text
    ell = "…"
    while text and c.stringWidth(text + ell, font, size) > max_w:
        text = text[:-1]
    return text + ell


def _fit(c, text: str, max_w: float, font: str, size: float) -> str:
    """Truncate to width, preserving a trailing parenthetical (e.g. '(Q)',
    '(Model Answer)') so otherwise-identical paired items stay distinguishable."""
    if c.stringWidth(text, font, size) <= max_w:
        return text
    m = _TRAIL_PAREN.search(text)
    if m:
        suffix = " " + m.group(1)
        head = text[: m.start()]
        sw = c.stringWidth(suffix, font, size)
        if sw < max_w * 0.8:  # only if the suffix leaves room for some head text
            return _clip(c, head, max_w - sw, font, size) + suffix
    return _clip(c, text, max_w, font, size)


def _draw_day_content(c, items, x, y, col_w, cell_h) -> None:
    pad = 3.5
    cx = x + col_w / 2
    top = y + cell_h - 14            # below the day-number row
    bottom = y + pad

    n = len(items)
    shown = items[:MAX_LINES]
    overflow = n - len(shown)
    list_lines = len(shown) + (1 if overflow else 0)
    list_h = list_lines * LINE_H
    thumb_h = max(top - bottom - list_h - 2, 18)
    thumb_w = col_w - 2 * pad

    # --- Primary thumbnail ---
    primary = items[0]
    thumb = make_thumbnail(primary.path)
    if thumb is not None:
        iw, ih = thumb.size
        scale = min(thumb_w / iw, thumb_h / ih)
        dw, dh = iw * scale, ih * scale
        c.drawImage(ImageReader(thumb), cx - dw / 2, top - dh, width=dw, height=dh,
                    preserveAspectRatio=True, mask="auto")
    else:  # fallback badge (e.g. PDF without a renderer)
        bw, bh = min(thumb_w, 44), min(thumb_h, 28)
        bx, by = cx - bw / 2, top - bh
        c.setFillColorRGB(*PDF_DOT)
        c.roundRect(bx, by, bw, bh, 3, stroke=0, fill=1)
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(cx, by + bh / 2 - 3, "PDF")

    # --- Item list (one line per file) ---
    text_x = x + pad + 6           # leave room for the colour dot
    label_w = col_w - pad - (text_x - x)
    ly = top - thumb_h - LINE_H + 1
    for it in shown:
        dot = PDF_DOT if it.is_pdf else IMG_DOT
        c.setFillColorRGB(*dot)
        c.circle(x + pad + 2, ly + LIST_SIZE / 2 - 0.5, 1.7, stroke=0, fill=1)
        c.setFillColorRGB(*INK)
        c.setFont(LIST_FONT, LIST_SIZE)
        c.drawString(text_x, ly, _fit(c, _short_label(it.path.name),
                                      label_w, LIST_FONT, LIST_SIZE))
        ly -= LINE_H
    if overflow:
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.setFont("Helvetica-Oblique", LIST_SIZE)
        c.drawString(text_x, ly, f"+{overflow} more")


def _draw_footer(c, result, left, margin, grid_w) -> None:
    c.setFont("Helvetica", 8)
    # Legend with colour swatches: green dot = image, red dot = PDF.
    lx = left
    c.setFillColorRGB(*INK)
    c.drawString(lx, margin + 14, "Green cell = posting day")
    lx += c.stringWidth("Green cell = posting day", "Helvetica", 8) + 16
    c.setFillColorRGB(*IMG_DOT)
    c.circle(lx + 2, margin + 16.5, 2, stroke=0, fill=1)
    c.setFillColorRGB(*INK)
    c.drawString(lx + 7, margin + 14, "image")
    lx += 7 + c.stringWidth("image", "Helvetica", 8) + 16
    c.setFillColorRGB(*PDF_DOT)
    c.circle(lx + 2, margin + 16.5, 2, stroke=0, fill=1)
    c.setFillColorRGB(*INK)
    c.drawString(lx + 7, margin + 14, "PDF / document")

    notes = []
    if result.out_of_range:
        notes.append(f"{len(result.out_of_range)} file(s) dated outside this month")
    if result.unscheduled:
        notes.append(f"{len(result.unscheduled)} file(s) with no detectable date")
    if notes:
        c.setFillColorRGB(0.6, 0.2, 0.2)
        c.drawString(left, margin + 2, "Note: " + "; ".join(notes)
                     + " — see console output.")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", type=Path, default=Path("assets/sparrows"),
                    help="Folder containing the sparrow image/PDF files.")
    ap.add_argument("--out", type=Path, default=Path("june-sparrow-calendar.pdf"),
                    help="Output PDF path.")
    ap.add_argument("--month", default="2026-06",
                    help="Target month as YYYY-MM (default: 2026-06).")
    ap.add_argument("--week-start", choices=["sun", "mon"], default="sun",
                    help="First day of the week (default: sun).")
    ap.add_argument("--title", default=None,
                    help="Calendar title (defaults to '<Month> <Year> — "
                         "Sparrow Study-Group Posting Calendar').")
    args = ap.parse_args(argv)

    try:
        year, month = (int(x) for x in args.month.split("-"))
    except ValueError:
        ap.error("--month must be in YYYY-MM format, e.g. 2026-06")

    if not args.src.is_dir():
        ap.error(f"source folder not found: {args.src}")

    if not _HEIC_OK:
        print("Note: pillow-heif not installed — .heic/.heif files will be skipped.",
              file=sys.stderr)
    if not _PDF_OK:
        print("Note: PyMuPDF not installed — PDFs will show a badge, not a preview.",
              file=sys.stderr)

    title = args.title or (f"{calendar.month_name[month]} {year} — "
                           "Sparrow Study-Group Posting Calendar")

    result = scan(args.src, year, month)

    # A date is "shown" if it lands on any cell of the visible grid (which
    # includes the adjacent-month days needed to complete the first/last week).
    weeks, _ = build_weeks(year, month, args.week_start)
    visible = {d for week in weeks for d in week}
    result.out_of_range = [
        (i.path, d) for d, items in sorted(result.by_date.items())
        if d not in visible for i in items
    ]

    # --- Console parse report ---
    scheduled = sum(len(v) for d, v in result.by_date.items() if d in visible)
    print(f"Scanned {args.src}: {scheduled} file(s) placed on the "
          f"{calendar.month_name[month]} {year} grid "
          f"({len([d for d in result.by_date if d in visible])} day(s)).")
    for day in sorted(d for d in result.by_date if d in visible):
        tag = "" if day.month == month else "  [adjacent month]"
        names = ", ".join(i.path.name for i in result.by_date[day])
        print(f"  {day.isoformat()} ({day:%a}): {names}{tag}")
    if result.out_of_range:
        print("\nOutside target month (not placed):")
        for path, date in result.out_of_range:
            print(f"  {date.isoformat()}  {path.name}")
    if result.unscheduled:
        print("\nNo date detected (rename to include a date, then re-run):")
        for path in result.unscheduled:
            print(f"  {path.name}")

    render_pdf(result, args.out, year, month, args.week_start, title)
    print(f"\nWrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
