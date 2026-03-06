---
name: clawreceipt
description: Smart receipt management skill with auto-categorization, predictive budgeting, trend analysis, and AI-powered spending insights for the OpenClaw ecosystem.
---

# ClawReceipt Skill for OpenClaw 🧾🧠

Use this skill when the user needs to manage receipts, track spending, analyze budgets, or get smart financial insights.

## Trigger Conditions

Use this skill when the user wants to:

- Upload or provide a receipt image/text to be recorded
- Add a new expense, bill, or receipt to the database
- Check current budget status or predictions
- List, search, or filter receipts
- Get spending trends, category breakdowns, or insights
- Compare months or detect recurring expenses
- Export receipt data to CSV/Excel

## Core Workflows

### 1) Add a Receipt (Smart Mode)

When the user provides receipt details, extract the fields and save:

```bash
# Full mode — category is auto-detected if omitted
python run.py add --date "YYYY-MM-DD" --time "HH:MM:SS" --store "<Store>" --amount <Amount> --category "<Category>" --notes "<Notes>" --tags "tag1,tag2"

# Quick mode — uses today's date, auto-detects category
python run.py quick "<Store>" <Amount> --notes "note" --tags "tag1"
```

**Important**: If `--category` is omitted in `add`, the system auto-detects the category based on the store name using pattern matching and learned history. Verify the auto-detection with the user.

### 2) Check Budget Status

```bash
python run.py budget                    # Current month overview with prediction
python run.py budget --month "2026-02"  # Specific month
python run.py budget --set 10000        # Set new monthly budget
```

Parse the output which includes spending bar, remaining amount, and prediction (daily rate, projected total, safe daily limit).

### 3) Smart Alert Check

```bash
python run.py alert
```

Exit codes:

- `0` = Within budget
- `1` = Over budget
- `2` = Within budget but **projected** to exceed (warning)

### 4) List and Search Receipts

```bash
python run.py list                          # All receipts
python run.py list --month "2026-03"        # Filter by month
python run.py list --category "Food"        # Filter by category
python run.py list --limit 10               # Limit results

python run.py search "Seven Eleven"         # Full-text search
python run.py search "Food"                 # Search by category/store/notes/tags
```

### 5) Edit and Delete Receipts

```bash
python run.py edit <ID> --amount 250 --category "Shopping"
python run.py delete <ID>
```

### 6) Spending Analytics

```bash
python run.py summary                       # Category breakdown (this month)
python run.py summary --month "2026-02"     # Specific month
python run.py trends                        # Full trend analysis with sparklines
python run.py trends --month "2026-03"      # Monthly trends
python run.py predict                       # End-of-month spending prediction
python run.py compare "2026-01" "2026-02"   # Compare two months
python run.py recurring                     # Detect recurring expenses
python run.py stores                        # Store spending leaderboard
python run.py stores --month "2026-03"      # Monthly store ranking
```

### 7) AI Insights

```bash
python run.py insights
```

This generates intelligent observations including:

- Budget health status
- Spending acceleration warnings
- Category dominance alerts
- Recurring expense summaries
- Month-over-month comparisons
- Large expense notifications

### 8) Export Data

```bash
python run.py export csv                    # Export to CSV
python run.py export excel                  # Export to Excel
python run.py export csv --filename "my_receipts.csv"
```

### 9) Open TUI Dashboard

```bash
python run.py tui
```

*(Note: As an agent, do NOT run `tui` directly. Instruct the user to run it in a terminal)*

## Example Outputs

Below are example outputs for each major command. Use these to understand the response format when parsing CLI results.

### Quick Add

```bash
python run.py quick "Seven Eleven" 85.50
```

```
  ✓ Saved! #1 — Seven Eleven: 85.50 ฿ [Food]
  █░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 86/8,000 ฿ (1%)
```

> The `[Food]` label shows the auto-detected category. The progress bar shows current budget usage.

### Standard Add (with auto-detection)

```bash
python run.py add --date "2026-03-06" --store "Lazada" --amount 890 --notes "USB-C cable" --tags "gadget"
```

```
  ℹ Auto-detected category: Shopping
  ✅ Receipt Saved
  ● ID:       8
  ● Store:    Lazada
  ● Amount:   890.00 ฿
  ● Category: Shopping
  ● Notes:    USB-C cable
  ● Tags:     gadget
  ● Budget Usage: 16% (1,290 / 8,000 ฿)
```

> When `--category` is omitted, the output includes `Auto-detected category:` line. Parse this to confirm with the user.

### Budget Status

```bash
python run.py budget
```

```
┌──────────────────────────────────────────────────────────┐
│ Budget Status: 2026-03                                   │
└──────────────────────────────────────────────────────────┘
  ● Monthly Budget: 8,000.00 ฿
  ● Total Spent:    1,290.50 ฿
  ● Remaining:      6,709.50 ฿

  ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 16.1%
  ✓ On track! 👍

┌──────────────────────────────────────────────────────────┐
│ 🔮 Prediction                                            │
└──────────────────────────────────────────────────────────┘
  ● Daily Rate:        215.08 ฿/day
  ● Projected Total:   6,667.58 ฿
  ● Safe Daily Limit:  268.38 ฿/day
  ✓ Projected to stay under budget by 1,332 ฿
```

> Parse key-value pairs after `●` to extract budget info. Relay the prediction section to the user.

### Alert (Silent Check)

```bash
$ python run.py alert
# Exit code 0:
✅ Budget OK (1,290/8,000 ฿)

# Exit code 1:
🚨 EXCEEDED! Spent: 9,200/8,000 ฿

# Exit code 2 (new):
⚠️ Within budget (6,500/8,000 ฿) but projected to exceed: 10,200 ฿
```

> Use exit codes for automation: `0`=safe, `1`=over, `2`=projected to exceed.

### Category Summary

```bash
python run.py summary
```

```
                     Category Breakdown (2026-03)
╔══════════════╤══════════╤═══════════════╤════════╤══════════════════════╗
║ Category     │ Receipts │        Amount │  Share │ Bar                  ║
╟──────────────┼──────────┼───────────────┼────────┼──────────────────────╢
║ Shopping     │    1     │      890.00 ฿ │  69.0% │ █████████████░░░░░░░ ║
║ Food         │    2     │      250.50 ฿ │  19.4% │ ███░░░░░░░░░░░░░░░░ ║
║ Transport    │    1     │      150.00 ฿ │  11.6% │ ██░░░░░░░░░░░░░░░░░ ║
╚══════════════╧══════════╧═══════════════╧════════╧══════════════════════╝
  Total: 1,290.50 ฿
```

### Predict

```bash
python run.py predict
```

```
┌──────────────────────────────────────────────────────────┐
│ Current Status                                           │
└──────────────────────────────────────────────────────────┘
  ● Days Elapsed:   6 / 31
  ● Days Remaining: 25
  ● Current Spent:  1,290.50 ฿
  ● Daily Rate:     215.08 ฿/day

┌──────────────────────────────────────────────────────────┐
│ 🔮 Projection                                            │
└──────────────────────────────────────────────────────────┘
  ● Predicted End-of-Month: 6,667.58 ฿
  ● Budget:                 8,000.00 ฿
  ● Safe Daily Limit:       268.38 ฿/day
  ✓ On track! Projected to stay under budget by 1,332 ฿
```

> Relay the safe daily limit and on-track status to the user.

### Search

```bash
python run.py search "Starbucks"
```

```
               Results for "Starbucks"

  ID   Date         Store       Amount   Category   Notes
 ─────────────────────────────────────────────────────────
  6    2026-03-06   Starbucks   165.00   Food

  1 result(s) found
```

### Insights

```bash
python run.py insights
```

```
  📊 Budget at 16%. On track for this month.
  💡 Safe to spend up to 268 ฿/day for the remaining 25 days.
  📌 'Shopping' dominates your spending (69% of total). Consider diversifying.
  📉 Great job! Spending is down 59% compared to 2026-02.
  💰 Single large expense: Lazada at 890 ฿ (69% of monthly total).

  ℹ 5 insight(s) generated for 2026-03
```

> Each insight line starts with an emoji icon. Relay all insights to the user as-is.

### Compare

```bash
python run.py compare "2026-02" "2026-03"
```

```
                      Month Comparison
╔═══════════════╤═══════════════╤═══════════════╤═══════════════════════════╗
║ Metric        │       2026-02 │       2026-03 │                   Change ║
╟───────────────┼───────────────┼───────────────┼───────────────────────────╢
║ Total Spent   │    3,150.00 ฿ │    1,290.50 ฿ │  🔻 1,859.50 ฿ (-59.0%) ║
║ Receipts      │             8 │             4 │                       -4 ║
║ Avg/Receipt   │      393.75 ฿ │      322.63 ฿ │                          ║
╚═══════════════╧═══════════════╧═══════════════╧═══════════════════════════╝
  ✓ Spending decreased by 59% 🎉
```

### Recurring

```bash
python run.py recurring
```

```
                       Recurring Expenses
╭──────────────┬──────────┬────────────┬───────────┬─────────────┬────────────╮
│ Store        │ Category │ Avg Amount │ Frequency │ Occurrences │ Last       │
├──────────────┼──────────┼────────────┼───────────┼─────────────┼────────────┤
│ Seven Eleven │ Food     │     102.75 │ weekly    │           6 │ 2026-03-06 │
│ Grab         │ Transport│     145.00 │ weekly    │           4 │ 2026-03-06 │
╰──────────────┴──────────┴────────────┴───────────┴─────────────┴────────────╯
  Total recurring: ~248 ฿/cycle
```

### Stores Leaderboard

```bash
python run.py stores
```

```
                    🏪 Store Leaderboard
╭─────┬──────────────┬──────────┬────────────┬────────╮
│ #   │ Store        │ Category │      Total │ Visits │
├─────┼──────────────┼──────────┼────────────┼────────┤
│ 🥇  │ Lazada       │ Shopping │     890.00 │      1 │
│ 🥈  │ Starbucks    │ Food     │     165.00 │      1 │
│ 🥉  │ Grab         │ Transport│     150.00 │      1 │
│ 4   │ Seven Eleven │ Food     │      85.50 │      1 │
╰─────┴──────────────┴──────────┴────────────┴────────╯
```

### List

```bash
python run.py list --month "2026-03"
```

```
                      🧾 Receipts 2026-03
╭───────┬────────────┬──────────┬──────────────┬────────────┬──────────┬──────╮
│ ID    │ Date       │ Time     │ Store        │     Amount │ Category │ Tags │
├───────┼────────────┼──────────┼──────────────┼────────────┼──────────┼──────┤
│ 7     │ 2026-03-06 │ 08:42:00 │ Lazada       │     890.00 │ Shopping │ gadget│
│ 6     │ 2026-03-06 │ 08:41:00 │ Starbucks    │     165.00 │ Food     │ —    │
│ 5     │ 2026-03-06 │ 08:40:00 │ Grab         │     150.00 │ Transport│ —    │
│ 4     │ 2026-03-06 │ 08:39:00 │ Seven Eleven │      85.50 │ Food     │ —    │
╰───────┴────────────┴──────────┴──────────────┴────────────┴──────────┴──────╯

  Showing 4 receipts — Total: 1,290.50 ฿
```

## Auto-Categorization

The system learns from user categorizations. Supported auto-detected categories include:

- **Food**: Seven Eleven, McDonald's, Starbucks, GrabFood, etc.
- **Transport**: Grab, BTS, MRT, PTT, Shell, etc.
- **Shopping**: Lazada, Shopee, Central, Big C, etc.
- **Entertainment**: Netflix, Spotify, Major Cinema, etc.
- **Health**: Hospitals, clinics, pharmacies, gyms
- **Bills**: AIS, True, electricity, water, rent
- **Education**: Books, courses, Udemy
- **Travel**: Hotels, Agoda, airlines

## Required Checks

- Verify `run.py` is present in the ClawReceipt root folder
- Ensure Python venv is activated: `.\venv\Scripts\activate`
- Always quote string arguments: `--store "Full Name"`
- Check exit codes for `alert` command (0=ok, 1=over, 2=warning)

## Troubleshooting

- `UnicodeEncodeError`: Terminal encoding handled internally; ensure utf-8
- `ModuleNotFoundError`: Run `pip install -r requirements.txt`
- `unrecognized arguments`: Check command syntax with `python run.py <command> --help`

## Completion Checklist

- Required fields accurately extracted and fed to the command
- Command executed successfully (exit code 0)
- Budget alerts and predictions relayed to the user
- Auto-detected category confirmed with user when applicable
