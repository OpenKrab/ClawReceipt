"""
ClawReceipt CLI 🦞 — The Smartest Receipt Manager
Now with auto-categorization, predictive alerts, trend analysis, search, and more.
"""

import argparse
import sys
import os

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich import box

from datetime import datetime
from db import (
    init_db, add_receipt, get_budget, set_budget, get_total_spent,
    get_receipts, delete_receipt, get_category_stats, update_receipt,
    get_receipt_by_id, search_receipts_db, get_daily_spending,
    get_store_stats, get_monthly_totals, get_learned_category,
    get_all_categories, get_all_stores, export_to_csv, export_to_excel
)
from intelligence import (
    auto_categorize, learn_categorization, get_category_suggestions,
    analyze_spending_trends, compare_months, predict_monthly_spending,
    detect_recurring_expenses, generate_insights, search_receipts,
    format_sparkline
)
from styling import (
    print_banner, print_section, print_success, print_error,
    print_warning, print_info, print_key_value, COLORS
)


def main():
    init_db()
    parser = argparse.ArgumentParser(
        description="ClawReceipt 🧾🧠 — Smart Receipt Manager with AI-powered Insights"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ── add ──
    p_add = subparsers.add_parser("add", help="Add a new receipt")
    p_add.add_argument("--date", required=True, help="Date (YYYY-MM-DD)")
    p_add.add_argument("--time", default="", help="Time (HH:MM:SS)")
    p_add.add_argument("--store", required=True, help="Store/merchant name")
    p_add.add_argument("--amount", required=True, type=float, help="Total amount")
    p_add.add_argument("--category", default=None, help="Category (auto-detected if omitted)")
    p_add.add_argument("--notes", default="", help="Optional memo/notes")
    p_add.add_argument("--tags", default="", help="Comma-separated tags")

    # ── quick ── (quick add with minimal args)
    p_quick = subparsers.add_parser("quick", help="Quick add: just store and amount (today's date, auto-category)")
    p_quick.add_argument("store", help="Store name")
    p_quick.add_argument("amount", type=float, help="Amount")
    p_quick.add_argument("--tags", default="", help="Tags")
    p_quick.add_argument("--notes", default="", help="Notes")

    # ── tui ──
    subparsers.add_parser("tui", help="Open interactive TUI dashboard")

    # ── budget ──
    p_budget = subparsers.add_parser("budget", help="Budget management")
    p_budget.add_argument("--set", type=float, help="Set monthly budget")
    p_budget.add_argument("--month", help="Target month (YYYY-MM)")

    # ── alert ──
    subparsers.add_parser("alert", help="Silent budget check (exit code 0=ok, 1=over)")

    # ── list ──
    p_list = subparsers.add_parser("list", help="List receipts")
    p_list.add_argument("--month", help="Filter by month (YYYY-MM)")
    p_list.add_argument("--category", help="Filter by category")
    p_list.add_argument("--limit", type=int, default=50, help="Max rows to show")

    # ── delete ──
    p_delete = subparsers.add_parser("delete", help="Delete a receipt by ID")
    p_delete.add_argument("id", type=int, help="Receipt ID")

    # ── edit ──
    p_edit = subparsers.add_parser("edit", help="Edit a receipt field")
    p_edit.add_argument("id", type=int, help="Receipt ID")
    p_edit.add_argument("--date", help="New date")
    p_edit.add_argument("--time", help="New time")
    p_edit.add_argument("--store", help="New store")
    p_edit.add_argument("--amount", type=float, help="New amount")
    p_edit.add_argument("--category", help="New category")
    p_edit.add_argument("--notes", help="New notes")
    p_edit.add_argument("--tags", help="New tags")

    # ── summary ──
    p_summary = subparsers.add_parser("summary", help="Category spending breakdown")
    p_summary.add_argument("--month", help="Target month (YYYY-MM)")

    # ── search ──
    p_search = subparsers.add_parser("search", help="Search receipts by keyword")
    p_search.add_argument("query", help="Search query")

    # ── trends ──
    p_trends = subparsers.add_parser("trends", help="Spending trend analysis")
    p_trends.add_argument("--month", help="Focus on month (YYYY-MM)")

    # ── predict ──
    p_predict = subparsers.add_parser("predict", help="Predict end-of-month spending")
    p_predict.add_argument("--month", help="Target month (YYYY-MM)")

    # ── compare ──
    p_compare = subparsers.add_parser("compare", help="Compare two months")
    p_compare.add_argument("month1", help="First month (YYYY-MM)")
    p_compare.add_argument("month2", help="Second month (YYYY-MM)")

    # ── recurring ──
    subparsers.add_parser("recurring", help="Detect recurring expenses")

    # ── insights ──
    subparsers.add_parser("insights", help="AI-powered smart spending insights")

    # ── stores ──
    p_stores = subparsers.add_parser("stores", help="All-time store ranking")
    p_stores.add_argument("--month", help="Filter by month (YYYY-MM)")

    # ── export ──
    p_export = subparsers.add_parser("export", help="Export data to CSV or Excel")
    p_export.add_argument("format", choices=["csv", "excel"], help="Export format")
    p_export.add_argument("--filename", help="Custom output filename")

    args = parser.parse_args()
    console = Console()
    current_month = datetime.now().strftime("%Y-%m")
    today = datetime.now().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%H:%M:%S")

    # ════════════════════════════════════
    # 📝 ADD
    # ════════════════════════════════════
    if args.command == "add":
        print_banner("Recording New Receipt")

        # Smart auto-categorize if not provided
        category = args.category
        if not category:
            category = auto_categorize(args.store)
            print_info(f"Auto-detected category: [bold cyan]{category}[/]")

            # Show alternatives
            suggestions = get_category_suggestions(args.store)
            if len(suggestions) > 1:
                others = ", ".join(suggestions[:3])
                print_info(f"Other suggestions: {others}")

        # Check learned mapping
        learned = get_learned_category(args.store)
        if learned and not args.category:
            category = learned['category']
            print_info(f"Using learned category: [bold cyan]{category}[/] (confidence: {learned['confidence']:.0%})")

        receipt_id = add_receipt(args.date, args.time, args.store, args.amount, category, args.notes, args.tags)
        learn_categorization(args.store, category)

        print_section("✅ Receipt Saved")
        print_key_value("ID", f"[bold]{receipt_id}[/]")
        print_key_value("Store", args.store)
        print_key_value("Amount", f"[bold yellow]{args.amount:,.2f} ฿[/]")
        print_key_value("Category", category)
        if args.notes:
            print_key_value("Notes", args.notes)
        if args.tags:
            print_key_value("Tags", args.tags)

        # Budget warning
        budget = get_budget()
        spent = get_total_spent(current_month)
        if budget > 0:
            pct = spent / budget * 100
            print_key_value("Budget Usage", f"{pct:.0f}% ({spent:,.0f} / {budget:,.0f} ฿)")
            if spent > budget:
                console.print()
                print_error(f"🚨 OVER BUDGET by {spent - budget:,.2f} ฿!")
            elif pct > 80:
                console.print()
                print_warning(f"⚠️ {budget - spent:,.0f} ฿ remaining — approaching limit!")

    # ════════════════════════════════════
    # ⚡ QUICK ADD
    # ════════════════════════════════════
    elif args.command == "quick":
        category = auto_categorize(args.store)
        learned = get_learned_category(args.store)
        if learned:
            category = learned['category']

        receipt_id = add_receipt(today, now_time, args.store, args.amount, category, args.notes, args.tags)
        learn_categorization(args.store, category)

        print_banner("⚡ Quick Receipt")
        print_success(f"Saved! #{receipt_id} — {args.store}: {args.amount:,.2f} ฿ [{category}]")

        budget = get_budget()
        spent = get_total_spent(current_month)
        if budget > 0:
            remaining = budget - spent
            bar_len = 30
            fill = min(int(spent / budget * bar_len), bar_len)
            bar_color = "green" if fill < bar_len * 0.8 else ("yellow" if fill < bar_len else "red")
            bar = f"[{bar_color}]{'█' * fill}[/][dim]{'░' * (bar_len - fill)}[/]"
            console.print(f"  {bar} {spent:,.0f}/{budget:,.0f} ฿ ({spent/budget*100:.0f}%)")

    # ════════════════════════════════════
    # 🖥️ TUI
    # ════════════════════════════════════
    elif args.command == "tui":
        from tui import ClawReceiptTUI
        app = ClawReceiptTUI()
        app.run()

    # ════════════════════════════════════
    # 💰 BUDGET
    # ════════════════════════════════════
    elif args.command == "budget":
        print_banner("Budget Management")
        if args.set is not None:
            set_budget(args.set)
            print_section("Update Success")
            print_success(f"Monthly budget → [bold yellow]{args.set:,.2f} ฿[/]")
        else:
            target_month = args.month or current_month
            budget = get_budget()
            spent = get_total_spent(target_month)
            remaining = max(budget - spent, 0) if budget > 0 else 0

            print_section(f"Budget Status: {target_month}")
            print_key_value("Monthly Budget", f"[bold cyan]{budget:,.2f} ฿[/]")
            print_key_value("Total Spent", f"[bold yellow]{spent:,.2f} ฿[/]")
            print_key_value("Remaining", f"[bold green]{remaining:,.2f} ฿[/]" if remaining > 0 else f"[bold red]-{abs(budget-spent):,.2f} ฿[/]")

            if budget > 0:
                pct = spent / budget * 100
                bar_len = 40
                fill = min(int(pct / 100 * bar_len), bar_len)
                bar_color = "green" if pct < 60 else ("yellow" if pct < 90 else "red")
                bar = f"[{bar_color}]{'█' * fill}[/][dim]{'░' * (bar_len - fill)}[/]"
                console.print(f"\n  {bar} {pct:.1f}%")

                if pct > 100:
                    print_error(f"Exceeded by {spent - budget:,.2f} ฿!")
                elif pct > 80:
                    print_warning("Approaching budget limit.")
                else:
                    print_success("On track! 👍")

            # Show prediction
            df = get_receipts(target_month)
            prediction = predict_monthly_spending(df, target_month, budget)
            if prediction.get("has_data") and budget > 0:
                console.print()
                print_section("🔮 Prediction")
                print_key_value("Daily Rate", f"{prediction['daily_rate']:,.0f} ฿/day")
                print_key_value("Projected Total", f"{prediction['predicted_total']:,.0f} ฿")
                print_key_value("Safe Daily Limit", f"{prediction['safe_daily_limit']:,.0f} ฿/day")
                if prediction.get('on_track'):
                    print_success(f"Projected to finish under budget by {prediction.get('under_by', 0):,.0f} ฿")
                else:
                    print_warning(f"Projected to exceed budget by {prediction.get('over_by', 0):,.0f} ฿")

    # ════════════════════════════════════
    # 🚨 ALERT
    # ════════════════════════════════════
    elif args.command == "alert":
        budget = get_budget()
        spent = get_total_spent(current_month)

        # Enhanced alert with prediction
        df = get_receipts(current_month)
        prediction = predict_monthly_spending(df, current_month, budget)

        if budget > 0 and spent > budget:
            console.print(f"[bold red]🚨 EXCEEDED! Spent: {spent:,.0f}/{budget:,.0f} ฿[/bold red]")
            sys.exit(1)
        elif prediction.get("has_data") and not prediction.get("on_track", True):
            console.print(f"[bold yellow]⚠️ Within budget ({spent:,.0f}/{budget:,.0f} ฿) but projected to exceed: {prediction['predicted_total']:,.0f} ฿[/bold yellow]")
            sys.exit(2)  # New exit code for "warning"
        else:
            console.print(f"[green]✅ Budget OK ({spent:,.0f}/{budget:,.0f} ฿)[/green]")
            sys.exit(0)

    # ════════════════════════════════════
    # 📋 LIST
    # ════════════════════════════════════
    elif args.command == "list":
        target_month = args.month
        title = f"Receipts {f'({target_month})' if target_month else 'History'}"
        print_banner(title)
        df = get_receipts(target_month)

        if hasattr(args, 'category') and args.category:
            df = df[df['category'].str.lower() == args.category.lower()]

        if df.empty:
            print_info("No receipts found.")
            return

        df = df.head(args.limit)

        table = Table(
            title=f"🧾 {title}",
            title_style=f"bold {COLORS['primary']}",
            header_style=f"bold {COLORS['info']}",
            border_style=COLORS['gray'],
            box=box.ROUNDED
        )
        table.add_column("ID", style=COLORS['gray'], width=5)
        table.add_column("Date", style="cyan", width=12)
        table.add_column("Time", style="blue", width=10)
        table.add_column("Store", style="magenta", width=20)
        table.add_column("Amount", justify="right", style=COLORS['warning'], width=12)
        table.add_column("Category", style=COLORS['success'], width=14)
        table.add_column("Tags", style="dim", width=12)

        for _, row in df.iterrows():
            tags_display = row.get('tags', '')
            table.add_row(
                str(row['id']), row['date'], row['time'], row['store'],
                f"{row['amount']:,.2f}", row['category'],
                tags_display if tags_display else "—"
            )

        console.print(table)

        total = df['amount'].sum()
        console.print(f"\n  [dim]Showing {len(df)} receipts — Total: [bold yellow]{total:,.2f} ฿[/][/dim]")

    # ════════════════════════════════════
    # 🗑️ DELETE
    # ════════════════════════════════════
    elif args.command == "delete":
        receipt = get_receipt_by_id(args.id)
        if receipt is not None:
            print_banner(f"Delete Receipt #{args.id}")
            print_key_value("Store", receipt['store'])
            print_key_value("Amount", f"{receipt['amount']:,.2f} ฿")
            print_key_value("Date", receipt['date'])
            delete_receipt(args.id)
            print_success(f"Receipt #{args.id} deleted successfully.")
        else:
            print_error(f"Receipt #{args.id} not found.")

    # ════════════════════════════════════
    # ✏️ EDIT
    # ════════════════════════════════════
    elif args.command == "edit":
        fields = {}
        for field in ['date', 'time', 'store', 'amount', 'category', 'notes', 'tags']:
            val = getattr(args, field, None)
            if val is not None:
                fields[field] = val

        if not fields:
            print_error("No fields specified to edit. Use --date, --store, --amount, etc.")
            return

        print_banner(f"Editing Receipt #{args.id}")
        if update_receipt(args.id, **fields):
            for k, v in fields.items():
                print_key_value(k.capitalize(), str(v))
            print_success("Updated successfully!")
        else:
            print_error(f"Receipt #{args.id} not found.")

    # ════════════════════════════════════
    # 📊 SUMMARY
    # ════════════════════════════════════
    elif args.command == "summary":
        target_month = args.month or current_month
        print_banner(f"Spending Summary: {target_month}")
        df = get_category_stats(target_month)

        if df.empty:
            print_info(f"No data for {target_month}")
            return

        total = df['total'].sum()
        table = Table(
            title=f"Category Breakdown ({target_month})",
            border_style="dim",
            box=box.DOUBLE_EDGE
        )
        table.add_column("Category", style="bold cyan", width=16)
        table.add_column("Receipts", justify="center", style="dim", width=8)
        table.add_column("Amount", justify="right", style="yellow", width=14)
        table.add_column("Share", justify="right", width=8)
        table.add_column("Bar", width=22)

        for _, row in df.iterrows():
            pct = (row['total'] / total * 100) if total > 0 else 0
            bar_len = 20
            fill = int(pct / 100 * bar_len)
            bar = f"[cyan]{'█' * fill}[/][dim]{'░' * (bar_len - fill)}[/]"
            count_str = str(int(row['count'])) if 'count' in row else "—"
            table.add_row(row['category'], count_str, f"{row['total']:,.2f} ฿", f"{pct:.1f}%", bar)

        console.print(table)
        print_section("Total")
        print_info(f"Total: [bold yellow]{total:,.2f} ฿[/]")

    # ════════════════════════════════════
    # 🔍 SEARCH
    # ════════════════════════════════════
    elif args.command == "search":
        print_banner(f"Search: \"{args.query}\"")
        df = search_receipts_db(args.query)

        if df.empty:
            print_info("No matches found.")
            return

        table = Table(title=f"Results for \"{args.query}\"", border_style="dim", box=box.SIMPLE)
        table.add_column("ID", style=COLORS['gray'])
        table.add_column("Date", style="cyan")
        table.add_column("Store", style="magenta")
        table.add_column("Amount", justify="right", style="yellow")
        table.add_column("Category", style="green")
        table.add_column("Notes", style="dim")

        for _, row in df.iterrows():
            notes = row.get('notes', '')
            table.add_row(
                str(row['id']), row['date'], row['store'],
                f"{row['amount']:,.2f}", row['category'],
                (notes[:30] + "...") if len(notes) > 30 else notes
            )

        console.print(table)
        console.print(f"\n  [dim]{len(df)} result(s) found[/dim]")

    # ════════════════════════════════════
    # 📈 TRENDS
    # ════════════════════════════════════
    elif args.command == "trends":
        target_month = args.month or current_month
        print_banner(f"Trend Analysis: {target_month}")

        df = get_receipts(target_month)
        if df.empty:
            print_info("No data to analyze.")
            return

        analysis = analyze_spending_trends(df)

        if not analysis.get("has_data"):
            print_info("Insufficient data.")
            return

        # Overview stats
        print_section("📊 Overview")
        print_key_value("Total Receipts", str(analysis['total_receipts']))
        print_key_value("Total Spent", f"[bold yellow]{analysis['total_amount']:,.2f} ฿[/]")
        print_key_value("Average Receipt", f"{analysis['avg_per_receipt']:,.2f} ฿")
        print_key_value("Largest Receipt", f"{analysis['max_receipt']:,.2f} ฿")
        print_key_value("Smallest Receipt", f"{analysis['min_receipt']:,.2f} ฿")
        print_key_value("Median", f"{analysis['median_receipt']:,.2f} ฿")

        # Daily average
        print_section("📅 Daily Breakdown")
        print_key_value("Daily Average", f"{analysis['daily_avg']:,.2f} ฿")
        print_key_value("Biggest Day", f"{analysis['daily_max']:,.2f} ฿ on {analysis['daily_max_date']}")

        # Weekday pattern
        if 'weekday_pattern' in analysis:
            print_section("📅 Weekday Spending Pattern")
            for day, avg in analysis['weekday_pattern'].items():
                bar_len = 20
                max_val = max(analysis['weekday_pattern'].values())
                fill = int(avg / max_val * bar_len) if max_val > 0 else 0
                marker = " 👈 PEAK" if day == analysis.get('peak_spending_day') else ""
                console.print(f"  [cyan]{day}[/] [yellow]{'█' * fill}[/][dim]{'░' * (bar_len - fill)}[/] {avg:,.0f} ฿{marker}")

        # Top stores
        if analysis.get('top_stores'):
            print_section("🏪 Top Stores")
            for i, s in enumerate(analysis['top_stores'], 1):
                medal = ["🥇", "🥈", "🥉", "4.", "5."][i-1]
                console.print(f"  {medal} [magenta]{s['store']}[/] — {s['total']:,.2f} ฿ ({s['count']}x)")

        # Monthly sparkline
        monthly = get_monthly_totals()
        if not monthly.empty and len(monthly) > 1:
            print_section("📈 Monthly Trend")
            values = monthly['total'].tolist()
            spark = format_sparkline(values)
            months_range = f"{monthly.iloc[0]['month']} → {monthly.iloc[-1]['month']}"
            console.print(f"  [cyan]{spark}[/] ({months_range})")

    # ════════════════════════════════════
    # 🔮 PREDICT
    # ════════════════════════════════════
    elif args.command == "predict":
        target_month = args.month or current_month
        print_banner(f"🔮 Spending Prediction: {target_month}")

        budget = get_budget()
        df = get_receipts(target_month)
        prediction = predict_monthly_spending(df, target_month, budget)

        if not prediction.get("has_data"):
            print_info("No data to predict from.")
            return

        print_section("Current Status")
        print_key_value("Days Elapsed", f"{prediction['days_elapsed']} / {prediction['days_in_month']}")
        print_key_value("Days Remaining", str(prediction['days_remaining']))
        print_key_value("Current Spent", f"[bold yellow]{prediction['current_spent']:,.2f} ฿[/]")
        print_key_value("Daily Rate", f"{prediction['daily_rate']:,.2f} ฿/day")

        print_section("🔮 Projection")
        print_key_value("Predicted End-of-Month", f"[bold]{prediction['predicted_total']:,.2f} ฿[/]")

        if budget > 0:
            print_key_value("Budget", f"{budget:,.2f} ฿")
            print_key_value("Safe Daily Limit", f"[bold green]{prediction['safe_daily_limit']:,.2f} ฿/day[/]")

            if prediction.get('on_track'):
                print_success(f"✅ On track! Projected to stay under budget by {prediction.get('under_by', 0):,.0f} ฿")
            else:
                print_error(f"⚠️ Projected to EXCEED budget by {prediction.get('over_by', 0):,.0f} ฿!")

            if 'days_until_exceed' in prediction:
                if prediction['days_until_exceed'] > 0:
                    print_warning(f"At current rate, budget will be exceeded in ~{prediction['days_until_exceed']:.0f} days")
                else:
                    print_error("Budget already exceeded!")

    # ════════════════════════════════════
    # ⚖️ COMPARE
    # ════════════════════════════════════
    elif args.command == "compare":
        print_banner(f"Compare: {args.month1} vs {args.month2}")

        df = get_receipts()
        result = compare_months(df, args.month1, args.month2)

        table = Table(title="Month Comparison", box=box.DOUBLE_EDGE)
        table.add_column("Metric", style="cyan")
        table.add_column(args.month1, justify="right", style="yellow")
        table.add_column(args.month2, justify="right", style="green")
        table.add_column("Change", justify="right")

        table.add_row("Total Spent", f"{result['total1']:,.2f} ฿", f"{result['total2']:,.2f} ฿",
                       f"{'🔺' if result['change'] > 0 else '🔻'} {abs(result['change']):,.2f} ฿ ({result['change_pct']}%)")
        table.add_row("Receipts", str(result['count1']), str(result['count2']),
                       str(result['count2'] - result['count1']))

        # Per-receipt average
        avg1 = result['total1'] / result['count1'] if result['count1'] > 0 else 0
        avg2 = result['total2'] / result['count2'] if result['count2'] > 0 else 0
        table.add_row("Avg/Receipt", f"{avg1:,.2f} ฿", f"{avg2:,.2f} ฿", "")

        console.print(table)

        # Verdict
        if result['direction'] == 'up':
            print_warning(f"Spending increased by {result['change_pct']}%")
        elif result['direction'] == 'down':
            print_success(f"Spending decreased by {abs(result['change_pct'])}% 🎉")
        else:
            print_info("Spending remained flat.")

    # ════════════════════════════════════
    # 🔁 RECURRING
    # ════════════════════════════════════
    elif args.command == "recurring":
        print_banner("🔁 Recurring Expense Detection")
        df = get_receipts()
        recurring = detect_recurring_expenses(df, min_occurrences=2)

        if not recurring:
            print_info("No recurring patterns detected yet.")
            return

        table = Table(title="Recurring Expenses", box=box.ROUNDED)
        table.add_column("Store", style="magenta")
        table.add_column("Category", style="cyan")
        table.add_column("Avg Amount", justify="right", style="yellow")
        table.add_column("Frequency", style="green")
        table.add_column("Occurrences", justify="center")
        table.add_column("Last", style="dim")

        total_recurring = 0
        for r in recurring:
            table.add_row(
                r['store'], r['category'],
                f"{r['avg_amount']:,.2f} ฿", r['frequency'],
                str(r['occurrences']), r['last_date']
            )
            total_recurring += r['avg_amount']

        console.print(table)
        print_section("Summary")
        print_info(f"Total recurring: ~[bold yellow]{total_recurring:,.0f} ฿/cycle[/]")

    # ════════════════════════════════════
    # 💡 INSIGHTS
    # ════════════════════════════════════
    elif args.command == "insights":
        print_banner("💡 Smart Insights Engine")
        df = get_receipts()
        budget = get_budget()
        insights = generate_insights(df, budget, current_month)

        if not insights:
            print_info("Not enough data for insights yet.")
            return

        for insight in insights:
            severity_color = {
                "critical": "bold red",
                "high": "yellow",
                "medium": "cyan",
                "low": "dim",
            }
            color = severity_color.get(insight['severity'], 'white')
            console.print(f"  {insight['icon']} [{color}]{insight['message']}[/]")

        console.print()
        print_info(f"{len(insights)} insight(s) generated for {current_month}")

    # ════════════════════════════════════
    # 🏪 STORES
    # ════════════════════════════════════
    elif args.command == "stores":
        target_month = args.month
        print_banner(f"Store Rankings {f'({target_month})' if target_month else ''}")
        df = get_store_stats(target_month)

        if df.empty:
            print_info("No store data.")
            return

        table = Table(title="🏪 Store Leaderboard", box=box.ROUNDED)
        table.add_column("#", style="dim", width=4)
        table.add_column("Store", style="magenta")
        table.add_column("Category", style="cyan")
        table.add_column("Total", justify="right", style="yellow")
        table.add_column("Visits", justify="center")

        for i, (_, row) in enumerate(df.iterrows(), 1):
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, str(i))
            table.add_row(medal, row['store'], row['category'], f"{row['total']:,.2f} ฿", str(int(row['count'])))

        console.print(table)

    # ════════════════════════════════════
    # 📤 EXPORT
    # ════════════════════════════════════
    elif args.command == "export":
        if args.format == "csv":
            fname = args.filename or f"receipts_export_{current_month}.csv"
            export_to_csv(fname)
            print_success(f"Exported to {fname}")
        else:
            fname = args.filename or f"receipts_export_{current_month}.xlsx"
            export_to_excel(fname)
            print_success(f"Exported to {fname}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
