# CSV-driven Browser Automation Video Recorder

A Python + Playwright tool that reads rows from a CSV file and records a short
video of automated browser actions for each row. Built for producing polished
demo videos with a custom on-screen cursor, smooth movement, human-like typing,
click ripples and text callouts.

The automation scenario opens a search page, types a query (`Magento developer
in <city>`), submits the search, and clicks the first result — recording
everything to a `.webm` file per CSV row.

## Features

- Reads a UTF-8 CSV file (delimiter `;`, quote `"`).
- One `.webm` video per CSV row, saved as `<Company Name>.webm`.
- Custom SVG arrow cursor (white fill, black outline, 32×32) — Playwright's
  video does **not** capture the OS cursor, so it is injected via
  `context.add_init_script(...)`.
- Yellow semi-transparent highlight circle that follows the pointer.
- Smooth, eased cursor movement (`smoothstep`) — no teleporting.
- Character-by-character human-like typing with randomized delays.
- The search is submitted by moving the cursor to the Search button and
  clicking it with the mouse (the Enter key is never used).
- Expanding click ripple on every click.
- Auto-sized callout box (yellow background, black text) with fade-in/out.

## Requirements

- Python 3.9+
- Playwright for Python (sync API)
- Chromium browser (installed via Playwright)

No other third-party libraries are required — CSV reading uses the standard
library `csv` module.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
python -m playwright install chromium
```

## Usage

```bash
python capture_video.py                # uses ./input.csv
python capture_video.py path/to/my.csv # or pass a custom CSV path
```

Videos are written to `./video/` (or whatever `qscript.PATH_TO_VIDEO_FOLDER`
is set to). Each file is named `<Company Name>.webm`.

## CSV format

Encoding UTF-8, delimiter `;`, quote `"`. The header row must contain these
exact column names (one logical line in the file):

```text
URL; Company Name; Language; Country; Postcode; City; Street; HouseNo
```

Example (`input.csv`):

```text
URL; Company Name; Language; Country; Postcode; City; Street; HouseNo
https://duckduckgo.com/; Acme Corp; en; France; 75001; Paris; Rue de Rivoli; 10
https://duckduckgo.com/; Globex; en; Germany; 10115; Berlin; Unter den Linden; 5
```

## Project structure

```text
.
├── capture_video.py       # CSV reader + per-row loop, entry point
├── qscript.py             # CaptureVideo_Magento() + ShowCallout() + cursor script
├── requirements.txt       # playwright>=1.40.0
├── input.csv              # sample input
└── video/                 # recorded videos (created automatically, committed to the repo)
```

## How it works

### `capture_video.py`

- Opens the CSV with `csv.DictReader(delimiter=";", quotechar='"', skipinitialspace=True)`.
- For every row, calls `qscript.CaptureVideo_Magento(...)` with all column
  values.
- Prints the returned absolute path per row and a summary at the end.

### `qscript.py`

- `PATH_TO_VIDEO_FOLDER` — module-level global, overridable by the main
  script.
- `CURSOR_SCRIPT` — injected IIFE that installs the SVG cursor, highlight
  circle, ripple and callout helpers into the page.
- `ShowCallout(text, bgColor="yellow", textColor="black", fade=2000)` —
  shows a callout on the currently active page.
- `CaptureVideo_Magento(url, company_name, language, country, postcode, city,
  street, house_no)` — runs the scenario and returns the absolute path to the
  produced `.webm`, or `None` on failure.

Recording is finalized by closing the context (`context.close()`) before
calling `video.path()`, then the file is moved to
`<PATH_TO_VIDEO_FOLDER>/<company_name>.webm`.

## Troubleshooting

- **`playwright install` errors** — make sure you ran
  `python -m playwright install chromium` after activating the venv.
- **Empty videos / no cursor** — Chromium runs in a visible (non-headless)
  window; the injected SVG cursor is what you see in the video, not a real OS
  cursor. After a page navigation the injected cursor is gone, so
  `qscript.py` puts it back at the last mouse position.
- **Search results don't appear** — DuckDuckGo renders results client-side
  and can take 10+ seconds. `qscript.py` polls for up to ~30 s across several
  selector fallbacks.
- **CAPTCHA** — if DuckDuckGo shows a bot-check page, the run fails with an
  error (switch IP/VPN or try again later). The browser's default
  User-Agent is used on purpose (it is not overridden), so it matches the
  installed Chromium.
- **No video for a failed row** — when a run fails, its partial recording is
  deleted instead of being left in the video folder.
- **`Company Name` becomes `row_N`** — the CSV header had spaces around the
  field names. `skipinitialspace=True` plus key trimming in `capture_video.py`
  handles this.
