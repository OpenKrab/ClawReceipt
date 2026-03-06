"""
ClawReceipt TUI Dashboard 🦞
Smart terminal dashboard with live insights, sparklines, and budget visualization.
"""

from datetime import datetime
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Static, Button, Input, Label
from textual.containers import Horizontal, Vertical, Container
from textual.binding import Binding
from db import (
    get_receipts, get_budget, get_total_spent, init_db,
    export_to_csv, export_to_excel, delete_receipt,
    get_category_stats, get_daily_spending, get_monthly_totals,
    search_receipts_db
)
from intelligence import (
    predict_monthly_spending, generate_insights, detect_recurring_expenses,
    format_sparkline
)


class BudgetGauge(Static):
    """Visual budget gauge with prediction."""

    def update_gauge(self):
        current_month = datetime.now().strftime("%Y-%m")
        budget = get_budget()
        spent = get_total_spent(current_month)

        if budget <= 0:
            self.update("[dim]No budget set. Use: python run.py budget --set <amount>[/dim]")
            return

        pct = min(spent / budget * 100, 150)
        bar_len = 40
        fill = min(int(pct / 100 * bar_len), bar_len)

        if pct < 60:
            color = "green"
            status_icon = "✅"
        elif pct < 90:
            color = "yellow"
            status_icon = "⚠️"
        else:
            color = "red"
            status_icon = "🚨"

        remaining = max(budget - spent, 0)
        bar = f"[{color}]{'█' * fill}[/][dim]{'░' * (bar_len - fill)}[/]"

        # Prediction
        df = get_receipts(current_month)
        pred = predict_monthly_spending(df, current_month, budget)

        pred_line = ""
        if pred.get("has_data"):
            if pred.get("on_track"):
                pred_line = f"\n🔮 [green]On track[/] — projected: {pred['predicted_total']:,.0f} ฿ | safe: {pred['safe_daily_limit']:,.0f} ฿/day"
            else:
                pred_line = f"\n🔮 [red]Over-spending![/] — projected: {pred['predicted_total']:,.0f} ฿ | limit to {pred['safe_daily_limit']:,.0f} ฿/day"

        self.update(
            f"{status_icon} [b]Budget: {pct:.0f}%[/b]\n"
            f"{bar} {spent:,.0f} / {budget:,.0f} ฿\n"
            f"💰 Remaining: [bold {'green' if remaining > 0 else 'red'}]{remaining:,.0f} ฿[/]"
            f"{pred_line}"
        )


class StatsPanel(Static):
    """Statistics overview panel."""

    def update_stats(self):
        current_month = datetime.now().strftime("%Y-%m")
        spent = get_total_spent(current_month)
        total_all = get_total_spent()
        df = get_receipts(current_month)
        count = len(df)
        avg = spent / count if count > 0 else 0

        # Category breakdown mini
        cat_df = get_category_stats(current_month)
        cats_line = ""
        if not cat_df.empty:
            top_cats = []
            for _, row in cat_df.head(3).iterrows():
                pct = row['total'] / spent * 100 if spent > 0 else 0
                top_cats.append(f"[cyan]{row['category']}[/] {pct:.0f}%")
            cats_line = f"\n📌 Top: {' | '.join(top_cats)}"

        # Monthly trend sparkline
        monthly = get_monthly_totals()
        spark_line = ""
        if not monthly.empty and len(monthly) > 1:
            values = monthly['total'].tolist()
            spark = format_sparkline(values, width=16)
            spark_line = f"\n📈 Trend: [cyan]{spark}[/]"

        self.update(
            f"📅 [b cyan]{current_month}[/b cyan]\n"
            f"💰 Spent: [b yellow]{spent:,.0f}[/] ฿ ({count} receipts)\n"
            f"📊 Avg/receipt: {avg:,.0f} ฿\n"
            f"📦 All-time: {total_all:,.0f} ฿"
            f"{cats_line}"
            f"{spark_line}"
        )


class InsightsPanel(Static):
    """Smart insights panel."""

    def update_insights(self):
        current_month = datetime.now().strftime("%Y-%m")
        df = get_receipts()
        budget = get_budget()
        insights = generate_insights(df, budget, current_month)

        if not insights:
            self.update("[dim]No insights yet — add more receipts![/dim]")
            return

        lines = []
        for insight in insights[:5]:
            lines.append(f"{insight['icon']} {insight['message']}")

        self.update("\n".join(lines))


class ClawReceiptTUI(App):
    CSS = """
    Screen {
        layout: vertical;
    }
    #top-panels {
        height: auto;
        layout: horizontal;
        margin: 0 1;
    }
    #budget-panel {
        width: 1fr;
        padding: 1;
        background: $boost;
        margin: 0 1 0 0;
        border: solid $accent;
        height: auto;
    }
    #stats-panel {
        width: 1fr;
        padding: 1;
        background: $boost;
        margin: 0 0 0 1;
        border: solid $accent;
        height: auto;
    }
    #insights-panel {
        padding: 1;
        background: $surface;
        margin: 1;
        border: solid $warning;
        height: auto;
    }
    #insights-panel Static {
        height: auto;
    }
    DataTable {
        height: 1fr;
        margin: 0 1;
    }
    #actions {
        height: auto;
        padding: 1;
        layout: horizontal;
        align: center middle;
    }
    #search-bar {
        height: auto;
        padding: 0 1;
        layout: horizontal;
        align: left middle;
    }
    #search-bar Input {
        width: 40;
    }
    #search-bar Label {
        width: auto;
        padding: 0 1 0 0;
    }
    Button {
        margin: 0 1;
    }
    .btn-danger {
        background: $error;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("c", "export_csv", "CSV"),
        Binding("e", "export_excel", "Excel"),
        Binding("d", "delete_row", "Delete"),
        Binding("slash", "focus_search", "Search"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal(id="top-panels"):
            self.budget_gauge = BudgetGauge(id="budget-panel")
            yield self.budget_gauge
            self.stats_panel = StatsPanel(id="stats-panel")
            yield self.stats_panel

        with Container(id="insights-panel"):
            yield Label("💡 [b]Smart Insights[/b]")
            self.insights = InsightsPanel()
            yield self.insights

        with Horizontal(id="search-bar"):
            yield Label("🔍")
            self.search_input = Input(placeholder="Search receipts...", id="search-input")
            yield self.search_input
            yield Button("Search", id="btn_search", variant="primary")
            yield Button("Clear", id="btn_clear", variant="default")

        with Horizontal(id="actions"):
            yield Button("📤 CSV", id="btn_csv", variant="primary")
            yield Button("📊 Excel", id="btn_excel", variant="success")
            yield Button("🔄 Refresh", id="btn_refresh", variant="warning")
            yield Button("🗑️ Delete", id="btn_delete", variant="error")
            yield Button("❌ Quit", id="btn_quit", variant="error")

        self.table = DataTable()
        yield self.table
        yield Footer()

    def on_mount(self) -> None:
        init_db()
        self.title = "🧾 ClawReceipt — Smart Receipt Dashboard"
        self.sub_title = "🧠 AI-Powered Analytics"
        self.table.add_columns("ID", "Date", "Time", "Store", "Amount (฿)", "Category", "Tags")
        self.table.cursor_type = "row"
        self.populate_data()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn = event.button.id
        if btn == "btn_refresh":
            self.action_refresh()
        elif btn == "btn_csv":
            self.action_export_csv()
        elif btn == "btn_excel":
            self.action_export_excel()
        elif btn == "btn_delete":
            self.action_delete_row()
        elif btn == "btn_quit":
            self.exit()
        elif btn == "btn_search":
            self._do_search()
        elif btn == "btn_clear":
            self.search_input.value = ""
            self.populate_data()
            self.notify("Search cleared")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "search-input":
            self._do_search()

    def _do_search(self):
        query = self.search_input.value.strip()
        if not query:
            self.populate_data()
            return

        df = search_receipts_db(query)
        self.table.clear()
        rows = []
        for _, row in df.iterrows():
            tags = row.get('tags', '')
            rows.append((
                str(row['id']), row['date'], row['time'], row['store'],
                f"{row['amount']:,.2f}", row['category'],
                tags if tags else "—"
            ))
        self.table.add_rows(rows)
        self.notify(f"Found {len(df)} result(s) for '{query}'")

    def action_focus_search(self) -> None:
        self.search_input.focus()

    def action_refresh(self) -> None:
        self.populate_data()
        self.notify("🔄 Data refreshed!")

    def action_export_csv(self) -> None:
        export_to_csv("receipts_export.csv")
        self.notify("📤 Exported to receipts_export.csv")

    def action_export_excel(self) -> None:
        export_to_excel("receipts_export.xlsx")
        self.notify("📊 Exported to receipts_export.xlsx")

    def action_delete_row(self) -> None:
        selection = self.table.cursor_row
        if selection is not None:
            try:
                row_data = self.table.get_row_at(selection)
                receipt_id = int(row_data[0])
                if delete_receipt(receipt_id):
                    self.notify(f"🗑️ Deleted receipt #{receipt_id}")
                    self.populate_data()
                else:
                    self.notify(f"Receipt #{receipt_id} not found", severity="error")
            except Exception as e:
                self.notify(f"Error: {e}", severity="error")

    def populate_data(self) -> None:
        self.budget_gauge.update_gauge()
        self.stats_panel.update_stats()
        self.insights.update_insights()
        self.table.clear()

        df = get_receipts()

        rows = []
        for _, row in df.iterrows():
            tags = row.get('tags', '')
            rows.append((
                str(row['id']),
                row['date'],
                row['time'],
                row['store'],
                f"{row['amount']:,.2f}",
                row['category'],
                tags if tags else "—"
            ))

        self.table.add_rows(rows)


if __name__ == "__main__":
    app = ClawReceiptTUI()
    app.run()
