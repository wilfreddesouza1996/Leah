# Leah

Tools for the study group.

## June Sparrow Posting Calendar

A printable, one-page PDF calendar showing **which sparrow image/PDF to post on
which day**. Each source file carries its posting date in its filename (e.g.
`2026-06-08 QotD W11 - Sleep Disorders ICSD-3 (Q).png`); the generator reads
those dates and lays them out on a full-month grid with thumbnails.

The current deliverable is **[`june-sparrow-calendar.pdf`](june-sparrow-calendar.pdf)**.

### Regenerating it

1. Put the dated sparrow files (images and/or PDFs) in `assets/sparrows/`
   (this folder is git-ignored, so the raw files aren't committed).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Generate the PDF:
   ```bash
   python3 generate_calendar.py --src assets/sparrows \
       --out june-sparrow-calendar.pdf --month 2026-06
   ```

The script prints a report of every file it scheduled and flags any whose date
it couldn't read (rename those to include a date, then re-run).

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--src` | `assets/sparrows` | Folder of source images/PDFs |
| `--out` | `june-sparrow-calendar.pdf` | Output PDF path |
| `--month` | `2026-06` | Target month, `YYYY-MM` |
| `--week-start` | `sun` | First day of week (`sun` or `mon`) |
| `--title` | auto | Custom calendar title |

### Supported filename date formats

ISO (`2026-06-08`, `20260608`), month-name (`June 8`, `8 Jun 2026`), and bare
`MM-DD` (year assumed from `--month`). Images include `.jpg/.png/.gif/.webp` and
`.heic/.heif`; `.pdf` files are previewed by their first page.
