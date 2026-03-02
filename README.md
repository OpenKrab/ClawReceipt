# 🦞 ClawReceipt

**ClawReceipt** is a lightweight receipt management system for OpenClaw/OpenKrab ecosystem.  
It captures expenses fast, tracks monthly budget, and provides both CLI automation and TUI dashboard for human review.

<p align="center">
  <img src="/public/banner.png" alt="ClawReceipt Banner" width="700">
</p>

## Features

- **Fast CLI**: Add receipts with structured fields (`date`, `time`, `store`, `amount`, `category`)
- **Budget Tracking**: Real-time monthly budget monitoring with overflow alerts (`exit code 1`)
- **Rich TUI Dashboard**: Interactive terminal interface for data review and export
- **Data Export**: Export to `CSV` and `Excel` directly from TUI
- **OpenClaw Integration**: Ready for agents via included `SKILL.md`
- **Local First**: SQLite database with no cloud dependencies
- **Cross Platform**: Windows, Linux, macOS support with proper encoding

---

## Quick Start

### Prerequisites

- Python 3.10+
- OpenClaw CLI (recommended for automation)

### Installation

1. Clone repository

```bash
git clone https://github.com/OpenKrab/ClawReceipt.git
cd ClawReceipt
```

2. Create virtual environment and install

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
```

3. Set monthly budget

```bash
python run.py budget --set 5000
```

4. Add first receipt

```bash
python run.py add --date "2026-02-27" --time "15:30:00" --store "Seven Eleven" --amount 120.50 --category "Food"
```

---

## Core Commands

### Receipt Management

```bash
python run.py add --date "2026-02-27" --time "15:30:00" --store "Seven Eleven" --amount 120.50 --category "Food"
python run.py list
```

### Budget Operations

```bash
python run.py budget                    # Show current status
python run.py budget --set 5000        # Set new monthly budget
python run.py alert                    # Silent check (exit 0=ok, 1=exceeded)
```

### Dashboard & Export

```bash
python run.py tui                      # Open interactive dashboard
```

---

## OpenClaw Integration

This repo includes `SKILL.md` so OpenClaw agents can:

- Extract receipt details from images or text
- Call `python run.py add ...` with structured data
- Check budget status using `budget` or `alert`
- List receipt history via `list`
- Export data through TUI (user-initiated)

**Note**: Agents should avoid running `python run.py tui` in non-interactive sessions.

---

## Tech Stack

- **Python 3.10+** - Core runtime
- **SQLite** - Local database storage
- **Rich** - CLI styling and tables
- **Textual** - TUI dashboard framework
- **Pandas + OpenPyXL** - Data export functionality
- **Pydantic** - Data validation
- **Pillow** - Image processing support

---

## Data Structure

### Database Schema

```sql
CREATE TABLE receipts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,           -- YYYY-MM-DD
    time TEXT,           -- HH:MM:SS (optional)
    store TEXT,          -- Store/merchant name
    amount REAL,         -- Total amount
    category TEXT        -- Expense category
);

CREATE TABLE config (
    key TEXT PRIMARY KEY,
    value TEXT          -- e.g., monthly_budget
);
```

### File Locations

- SQLite DB: `data/receipts.db`
- Main entrypoint: `run.py`
- Core modules: `src/`
- Banner image: `public/banner.png`

---

## Typical Workflow

1. **Setup**: Configure monthly budget once with `budget --set`
2. **Capture**: Add receipts continuously with `add` command
3. **Monitor**: Use `alert` for automation checks and `list` for quick history
4. **Review**: Open `tui` for dashboard view and export options

---

## Project Structure

```
ClawReceipt/
├── data/
│   └── receipts.db          # SQLite database
├── public/
│   └── banner.png          # Project banner
├── src/
│   ├── cli.py              # CLI commands and argument parsing
│   ├── db.py              # Database operations
│   ├── tui.py             # Terminal dashboard
│   └── styling.py         # Rich styling utilities
├── run.py                 # Main entry point
├── requirements.txt       # Python dependencies
├── SKILL.md              # OpenClaw integration guide
└── README.md             # This file
```

---

## OpenClaw Skill Integration

The `SKILL.md` file provides complete instructions for OpenClaw agents to:

- Process receipt images using OCR/vision
- Extract structured data (date, time, store, amount, category)
- Store receipts with proper validation
- Handle budget alerts and notifications
- Generate spending reports

---

## Testing

```bash
# Test basic functionality
python run.py add --date "2026-01-01" --store "Test" --amount 100 --category "Test"
python run.py list
python run.py budget --set 1000
python run.py alert
```

---

## Contributing

PRs are welcome! Please ensure:

1. Code follows existing style patterns
2. Add tests for new functionality
3. Update documentation as needed
4. Test cross-platform compatibility

---

## License

MIT

---

*Built for the Lobster Way 🦞*
