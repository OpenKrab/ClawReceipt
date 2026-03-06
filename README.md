# 🦞 ClawReceipt

**ClawReceipt** is an AI-powered receipt management system for the OpenClaw/OpenKrab ecosystem.  
It captures expenses fast, auto-categorizes them, tracks monthly budgets with predictive analytics, detects recurring expenses, and provides smart financial insights — all from the CLI or a rich TUI dashboard.

<p align="center">
  <img src="/public/banner.png" alt="ClawReceipt Banner" width="700">
</p>

## ✨ Features

### Core

- **⚡ Quick Add**: Record receipts with just store name and amount — date, time, and category are auto-filled
- **🧠 Smart Auto-Categorize**: AI pattern matching detects categories from store names (200+ patterns for Food, Transport, Shopping, etc.)
- **🏷️ Tags & Notes**: Attach tags and memos to any receipt for better organization
- **✏️ Edit & Delete**: Full CRUD operations on all receipts

### Analytics & Intelligence

- **🔮 Predictive Budgeting**: Forecasts end-of-month spending based on daily rate
- **📈 Trend Analysis**: Weekday spending patterns, sparkline charts, and statistical breakdowns
- **🔁 Recurring Detection**: Automatically finds recurring expenses by analyzing store/amount patterns
- **💡 Smart Insights**: AI-generated actionable observations about your spending habits
- **⚖️ Month Comparison**: Side-by-side comparison of any two months
- **🏪 Store Ranking**: Leaderboard of where your money goes

### Interface

- **🖥️ Rich TUI Dashboard**: Full terminal UI with budget gauge, insights panel, search bar, and sparklines
- **📤 Data Export**: Export to CSV and Excel from CLI or TUI
- **🔍 Full-Text Search**: Search receipts by store, category, notes, tags, or date

### Integration

- **🦞 OpenClaw Ready**: Comprehensive `SKILL.md` for agent automation
- **💾 Local First**: SQLite with WAL mode, indexed queries, zero cloud dependencies
- **🌍 Cross Platform**: Windows, Linux, macOS with UTF-8 encoding support

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

1. Create virtual environment and install

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
```

1. Set monthly budget

```bash
python run.py budget --set 5000
```

1. Add first receipt (with auto-category!)

```bash
python run.py quick "Seven Eleven" 85.50
# → Auto-detects category: Food, uses today's date & time
```

---

## All Commands

### Receipt Management

```bash
# Standard add
python run.py add --date "2026-03-06" --time "15:30:00" --store "Seven Eleven" --amount 120.50 --category "Food" --notes "lunch" --tags "daily,food"

# Quick add (today, auto-category)
python run.py quick "Starbucks" 165

# List all / filter
python run.py list
python run.py list --month "2026-03" --category "Food" --limit 20

# Search
python run.py search "Starbucks"

# Edit a receipt
python run.py edit 5 --amount 200 --notes "corrected amount"

# Delete a receipt
python run.py delete 5
```

### Budget & Alerts

```bash
python run.py budget                    # Budget status + prediction
python run.py budget --set 10000        # Set new budget
python run.py budget --month "2026-02"  # Check specific month
python run.py alert                     # Silent check (exit 0=ok, 1=over, 2=warning)
```

### Analytics & Insights

```bash
python run.py summary                   # Category breakdown
python run.py trends                    # Full trend analysis with sparklines
python run.py predict                   # End-of-month prediction
python run.py compare "2026-01" "2026-02"  # Compare two months
python run.py recurring                 # Find recurring expenses
python run.py stores                    # Store spending leaderboard
python run.py insights                  # AI-powered smart insights
```

### Export

```bash
python run.py export csv
python run.py export excel --filename "my_report.xlsx"
```

### Dashboard

```bash
python run.py tui                      # Open interactive dashboard
```

---

## 📸 Examples

### ⚡ Quick Add (Auto-Category)

```bash
python run.py quick "Grab" 150
python run.py quick "Starbucks" 165
python run.py quick "Lazada" 890 --tags "gadget" --notes "USB-C cable"
```

> Category is auto-detected from the store name — `Grab → Transport`, `Starbucks → Food`, `Lazada → Shopping`!

<p align="center">
  <img src="/assets/quick_add.png" alt="Quick Add Example" width="700">
</p>

### 📊 Category Summary

```bash
python run.py summary
```

> Visual breakdown of all spending by category with progress bars and percentages.

<p align="center">
  <img src="/assets/summary.png" alt="Summary Example" width="700">
</p>

### 🔮 Predict End-of-Month

```bash
python run.py predict
```

> Forecasts your total spending by month-end based on your current daily rate. Shows safe daily spending limit to stay within budget.

<p align="center">
  <img src="/assets/predict.png" alt="Predict Example" width="700">
</p>

### 🔍 Search

```bash
python run.py search "Starbucks"
```

> Full-text search across store names, categories, notes, tags, and dates.

<p align="center">
  <img src="/assets/search.png" alt="Search Example" width="700">
</p>

### 💡 Smart Insights

```bash
python run.py insights
```

> AI-powered analysis of your spending habits — budget warnings, recurring expenses, month-over-month changes, and actionable advice.

<p align="center">
  <img src="/assets/insights.png" alt="Insights Example" width="700">
</p>

---

## Smart Auto-Categorization

ClawReceipt uses a dual-layer categorization engine:

1. **Pattern Matching**: 200+ regex patterns covering Thai and English store names
2. **Learning Engine**: Remembers your categorization choices and applies them to future receipts

### Supported Categories

| Category | Example Stores |
|---|---|
| Food | Seven Eleven, McDonald's, Starbucks, GrabFood, MK Suki |
| Transport | Grab, BTS, MRT, PTT, Shell, Toll |
| Shopping | Lazada, Shopee, Central, Big C, IKEA |
| Entertainment | Netflix, Spotify, Major Cinema, Steam |
| Health | Hospitals, Watson, Boots, Gym |
| Bills | AIS, True, Electric, Water, Rent |
| Education | Books, Udemy, Coursera |
| Travel | Agoda, Airbnb, Airlines |

---

## Predictive Budgeting

The system calculates:

- **Daily spending rate** from current month's data
- **Projected end-of-month total** based on remaining days
- **Safe daily limit** to stay within budget
- **Days until budget exhaustion** at current rate

The `alert` command now returns exit code `2` when spending is within budget but predicted to exceed — perfect for automated early warnings.

---

## Tech Stack

- **Python 3.10+** — Core runtime
- **SQLite** — Local database with WAL mode & indexing
- **Rich** — CLI styling, tables, progress bars
- **Textual** — TUI dashboard framework
- **Pandas + OpenPyXL** — Data analysis & export
- **Pydantic** — Data validation
- **Pillow** — Image processing support

---

## Data Structure

### Database Schema

```sql
CREATE TABLE receipts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    time TEXT DEFAULT '',
    store TEXT NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    notes TEXT DEFAULT '',
    tags TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now','localtime'))
);

CREATE TABLE config (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE category_learn (
    store_pattern TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    confidence REAL DEFAULT 1.0,
    updated_at TEXT
);
```

### File Locations

- SQLite DB: `data/receipts.db`
- Main entrypoint: `run.py`
- Core modules: `src/`
  - `cli.py` — CLI commands (16 commands)
  - `db.py` — Database operations with smart queries
  - `intelligence.py` — AI engine (categorization, analytics, prediction)
  - `tui.py` — Terminal dashboard
  - `styling.py` — Rich styling utilities
- Banner image: `public/banner.png`

---

## Project Structure

```
ClawReceipt/
├── data/
│   └── receipts.db              # SQLite database (auto-created)
├── public/
│   └── banner.png              # Project banner
├── src/
│   ├── cli.py                  # CLI commands (16 commands)
│   ├── db.py                   # Smart database layer
│   ├── intelligence.py         # 🧠 AI engine
│   ├── tui.py                  # Smart TUI dashboard
│   └── styling.py              # Rich styling utilities
├── run.py                      # Main entry point
├── requirements.txt            # Python dependencies
├── SKILL.md                    # OpenClaw agent integration guide
└── README.md                   # This file
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

*Built for the Lobster Way 🦞 — Now with 🧠 AI Superpowers*
