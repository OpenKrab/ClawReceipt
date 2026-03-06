"""
ClawReceipt Intelligence Engine 🧠
Auto-categorization, trend analysis, predictive budgeting, recurring detection, and smart insights.
"""

import re
from datetime import datetime, timedelta
from collections import defaultdict

# ==============================
# 🧠 SMART AUTO-CATEGORIZATION
# ==============================

# Store name -> category mapping patterns (case-insensitive regex)
CATEGORY_PATTERNS = {
    "Food": [
        r"seven.?eleven", r"7.?eleven", r"7.?11", r"family.?mart", r"lawson",
        r"mcdonald", r"kfc", r"burger.?king", r"subway", r"pizza", r"starbucks",
        r"cafe", r"coffee", r"ร้านอาหาร", r"อาหาร", r"food", r"restaurant",
        r"sizzler", r"mk.?suki", r"bar.?b.?q", r"yayoi", r"fuji", r"shabushi",
        r"after.?you", r"bonchon", r"s&p", r"bakery", r"ดัง", r"ส้มตำ",
        r"เซเว่น", r"แมค", r"เคเอฟซี", r"ข้าว", r"ก๋วยเตี๋ยว", r"อร่อย",
        r"noodle", r"ramen", r"sushi", r"thai", r"grill", r"bbq",
        r"tea\b", r"boba", r"milk.?tea", r"ชา\b", r"lunch", r"dinner", r"breakfast",
        r"grab.?food", r"food.?panda", r"line.?man", r"robinhood",
    ],
    "Transport": [
        r"grab", r"bolt", r"uber", r"taxi", r"แท็กซี่", r"bts", r"mrt",
        r"airport", r"rail.?link", r"bus", r"รถ", r"เดินทาง", r"transport",
        r"toll", r"parking", r"ที่จอดรถ", r"gas", r"fuel", r"ปั๊ม",
        r"shell", r"ptt", r"bangchak", r"esso", r"caltex", r"benzin",
        r"ev.?charge", r"เติมน้ำมัน", r"ค่าทาง",
    ],
    "Shopping": [
        r"lazada", r"shopee", r"amazon", r"tokopedia", r"central",
        r"robinson", r"big.?c", r"lotus", r"tesco", r"makro", r"ikea",
        r"uniqlo", r"h&m", r"zara", r"muji", r"daiso", r"miniso",
        r"tops", r"villa.?market", r"gourmet", r"ซื้อของ", r"ช้อปปิ้ง",
        r"mall", r"market", r"ตลาด", r"shop",
    ],
    "Entertainment": [
        r"netflix", r"spotify", r"youtube", r"disney", r"hbo",
        r"major", r"sf.?cinema", r"cinema", r"movie", r"หนัง",
        r"game", r"steam", r"playstation", r"xbox", r"nintendo",
        r"bowling", r"karaoke", r"concert", r"ticket", r"ตั๋ว",
        r"เกม", r"บันเทิง",
    ],
    "Health": [
        r"hospital", r"clinic", r"pharmacy", r"watson", r"boots",
        r"doctor", r"dental", r"ทันตแพทย์", r"โรงพยาบาล", r"คลินิก",
        r"ร้านยา", r"สุขภาพ", r"health", r"gym", r"fitness", r"yoga",
        r"vitamin", r"supplement",
    ],
    "Bills": [
        r"electric", r"water", r"internet", r"phone", r"mobile",
        r"ais", r"dtac", r"true", r"3bb", r"tot", r"ค่าน้ำ", r"ค่าไฟ",
        r"ค่าเน็ต", r"ค่าโทร", r"insurance", r"ประกัน", r"rent", r"ค่าเช่า",
        r"utility", r"bill", r"subscription",
    ],
    "Education": [
        r"book", r"udemy", r"coursera", r"school", r"university",
        r"tutor", r"library", r"หนังสือ", r"เรียน", r"คอร์ส", r"การศึกษา",
        r"education", r"course", r"workshop", r"seminar",
    ],
    "Travel": [
        r"hotel", r"hostel", r"airbnb", r"booking\.com", r"agoda",
        r"flight", r"airline", r"ที่พัก", r"เที่ยว", r"travel",
        r"luggage", r"tour", r"resort",
    ],
}

# Learn from user's historical data
_learned_mappings = {}


def auto_categorize(store_name: str) -> str:
    """
    Intelligently guess a category based on the store name.
    Returns the best-guess category or 'Other' if no match found.
    """
    store_lower = store_name.lower().strip()

    # 1) Check learned mappings first (user's past categorizations take priority)
    if store_lower in _learned_mappings:
        return _learned_mappings[store_lower]

    # 2) Check pattern-based matching
    best_match = None
    best_score = 0

    for category, patterns in CATEGORY_PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, store_lower, re.IGNORECASE)
            if match:
                score = len(match.group())  # Longer match = more specific
                if score > best_score:
                    best_score = score
                    best_match = category

    return best_match or "Other"


def learn_categorization(store_name: str, category: str):
    """Learn from user's categorization choices for future auto-suggest."""
    _learned_mappings[store_name.lower().strip()] = category


def get_category_suggestions(store_name: str) -> list:
    """Return top 3 category suggestions for a store name."""
    store_lower = store_name.lower().strip()
    scores = defaultdict(int)

    for category, patterns in CATEGORY_PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, store_lower, re.IGNORECASE)
            if match:
                scores[category] += len(match.group())

    sorted_cats = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    suggestions = [cat for cat, _ in sorted_cats[:3]]

    # Always include the learned mapping if exists
    if store_lower in _learned_mappings:
        learned = _learned_mappings[store_lower]
        if learned not in suggestions:
            suggestions.insert(0, learned)

    if not suggestions:
        suggestions = ["Other"]

    return suggestions


# ==============================
# 📈 TREND ANALYTICS ENGINE
# ==============================

def analyze_spending_trends(df):
    """
    Analyze spending patterns from a receipts DataFrame.
    Returns a dict with comprehensive analytics.
    """
    if df.empty:
        return {"has_data": False}

    result = {"has_data": True}

    # Daily spending
    df['date_parsed'] = df['date'].apply(lambda x: _safe_parse_date(x))
    df_valid = df.dropna(subset=['date_parsed']).copy()

    if df_valid.empty:
        return {"has_data": False}

    # Basic stats
    result['total_receipts'] = len(df_valid)
    result['total_amount'] = float(df_valid['amount'].sum())
    result['avg_per_receipt'] = float(df_valid['amount'].mean())
    result['max_receipt'] = float(df_valid['amount'].max())
    result['min_receipt'] = float(df_valid['amount'].min())
    result['median_receipt'] = float(df_valid['amount'].median())

    # Top stores
    store_totals = df_valid.groupby('store')['amount'].agg(['sum', 'count']).sort_values('sum', ascending=False)
    result['top_stores'] = [
        {"store": store, "total": float(row['sum']), "count": int(row['count'])}
        for store, row in store_totals.head(5).iterrows()
    ]

    # Top categories
    cat_totals = df_valid.groupby('category')['amount'].agg(['sum', 'count']).sort_values('sum', ascending=False)
    result['top_categories'] = [
        {"category": cat, "total": float(row['sum']), "count": int(row['count'])}
        for cat, row in cat_totals.iterrows()
    ]

    # Daily pattern
    daily = df_valid.groupby('date')['amount'].sum().reset_index()
    daily = daily.sort_values('date')
    result['daily_avg'] = float(daily['amount'].mean())
    result['daily_max'] = float(daily['amount'].max())
    result['daily_max_date'] = daily.loc[daily['amount'].idxmax(), 'date']

    # Weekday pattern
    df_valid['weekday'] = df_valid['date_parsed'].dt.dayofweek
    weekday_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    weekday_avg = df_valid.groupby('weekday')['amount'].mean()
    result['weekday_pattern'] = {
        weekday_names[int(day)]: round(float(avg), 2)
        for day, avg in weekday_avg.items()
    }

    # Peak spending day of week
    if not weekday_avg.empty:
        peak_day = int(weekday_avg.idxmax())
        result['peak_spending_day'] = weekday_names[peak_day]

    return result


def compare_months(df, month1: str, month2: str):
    """
    Compare spending between two months.
    month1 and month2 are in 'YYYY-MM' format.
    """
    df1 = df[df['date'].str.startswith(month1)]
    df2 = df[df['date'].str.startswith(month2)]

    total1 = float(df1['amount'].sum()) if not df1.empty else 0
    total2 = float(df2['amount'].sum()) if not df2.empty else 0
    count1 = len(df1)
    count2 = len(df2)

    change = total2 - total1
    change_pct = (change / total1 * 100) if total1 > 0 else 0

    return {
        "month1": month1, "month2": month2,
        "total1": total1, "total2": total2,
        "count1": count1, "count2": count2,
        "change": change, "change_pct": round(change_pct, 1),
        "direction": "up" if change > 0 else ("down" if change < 0 else "flat"),
    }


# ==============================
# 🔮 PREDICTIVE BUDGET ENGINE
# ==============================

def predict_monthly_spending(df, month: str, budget: float):
    """
    Predict end-of-month spending based on current trajectory.
    Returns prediction info dict.
    """
    month_df = df[df['date'].str.startswith(month)]

    if month_df.empty:
        return {"has_data": False}

    today = datetime.now()
    day_of_month = today.day

    # Determine total days in this month
    if today.month == 12:
        days_in_month = 31
    else:
        next_month = today.replace(month=today.month + 1, day=1)
        days_in_month = (next_month - today.replace(day=1)).days

    current_spent = float(month_df['amount'].sum())
    days_elapsed = max(day_of_month, 1)
    days_remaining = max(days_in_month - day_of_month, 0)

    # Calculate daily rate
    daily_rate = current_spent / days_elapsed

    # Predict end-of-month total
    predicted_total = current_spent + (daily_rate * days_remaining)

    # Safe daily limit (how much can be spent per remaining day to stay in budget)
    safe_daily_limit = 0
    if days_remaining > 0 and budget > 0:
        safe_daily_limit = max((budget - current_spent) / days_remaining, 0)

    result = {
        "has_data": True,
        "current_spent": round(current_spent, 2),
        "daily_rate": round(daily_rate, 2),
        "predicted_total": round(predicted_total, 2),
        "days_elapsed": days_elapsed,
        "days_remaining": days_remaining,
        "days_in_month": days_in_month,
        "budget": budget,
        "safe_daily_limit": round(safe_daily_limit, 2),
    }

    if budget > 0:
        result["on_track"] = predicted_total <= budget
        result["over_by"] = round(max(predicted_total - budget, 0), 2)
        result["under_by"] = round(max(budget - predicted_total, 0), 2)

        # Days until budget is exceeded (at current rate)
        if daily_rate > 0 and current_spent < budget:
            days_until_exceed = (budget - current_spent) / daily_rate
            result["days_until_exceed"] = round(days_until_exceed, 1)
        elif current_spent >= budget:
            result["days_until_exceed"] = 0
    else:
        result["on_track"] = True

    return result


# ==============================
# 🔁 RECURRING DETECTION ENGINE
# ==============================

def detect_recurring_expenses(df, min_occurrences: int = 2):
    """
    Detect recurring expenses based on store+amount pattern across months.
    """
    if df.empty:
        return []

    # Group by store+category and find entries with similar amounts
    recurring = []
    grouped = df.groupby(['store', 'category'])

    for (store, category), group in grouped:
        if len(group) < min_occurrences:
            continue

        # Check if amounts are relatively consistent (within 10% variance)
        amounts = group['amount'].tolist()
        avg_amount = sum(amounts) / len(amounts)
        if avg_amount == 0:
            continue

        variance = max(abs(a - avg_amount) / avg_amount for a in amounts) if avg_amount > 0 else 0

        # Get dates to check frequency
        dates = sorted(group['date'].tolist())

        if variance <= 0.15:  # Within 15%
            frequency = _estimate_frequency(dates)
            recurring.append({
                "store": store,
                "category": category,
                "avg_amount": round(avg_amount, 2),
                "occurrences": len(group),
                "frequency": frequency,
                "last_date": dates[-1] if dates else "",
                "dates": dates,
            })

    # Sort by occurrence count
    recurring.sort(key=lambda x: x['occurrences'], reverse=True)
    return recurring


def _estimate_frequency(dates: list) -> str:
    """Estimate how frequent the expenses occur."""
    if len(dates) < 2:
        return "one-time"

    parsed = [_safe_parse_date(d) for d in dates]
    parsed = [d for d in parsed if d is not None]
    if len(parsed) < 2:
        return "unknown"

    parsed.sort()
    gaps = [(parsed[i+1] - parsed[i]).days for i in range(len(parsed)-1)]
    avg_gap = sum(gaps) / len(gaps)

    if avg_gap <= 1.5:
        return "daily"
    elif avg_gap <= 8:
        return "weekly"
    elif avg_gap <= 17:
        return "bi-weekly"
    elif avg_gap <= 35:
        return "monthly"
    elif avg_gap <= 100:
        return "quarterly"
    else:
        return "occasional"


# ==============================
# 💡 SMART INSIGHTS ENGINE
# ==============================

def generate_insights(df, budget: float, current_month: str) -> list:
    """
    Generate smart actionable insights based on spending data.
    Returns a list of insight dicts with type, message, severity.
    """
    insights = []

    if df.empty:
        insights.append({
            "type": "info",
            "icon": "📝",
            "message": "No receipts recorded yet. Start by adding your first receipt!",
            "severity": "low"
        })
        return insights

    month_df = df[df['date'].str.startswith(current_month)]
    month_spent = float(month_df['amount'].sum()) if not month_df.empty else 0

    # Insight 1: Budget health
    if budget > 0:
        usage_pct = (month_spent / budget) * 100
        if usage_pct > 100:
            over = month_spent - budget
            insights.append({
                "type": "danger",
                "icon": "🚨",
                "message": f"Budget exceeded by {over:,.2f} ฿ ({usage_pct:.0f}% used)!",
                "severity": "critical"
            })
        elif usage_pct > 80:
            insights.append({
                "type": "warning",
                "icon": "⚠️",
                "message": f"Approaching budget limit ({usage_pct:.0f}% used). {budget - month_spent:,.2f} ฿ remaining.",
                "severity": "high"
            })
        elif usage_pct > 50:
            insights.append({
                "type": "info",
                "icon": "📊",
                "message": f"Budget at {usage_pct:.0f}%. On track for this month.",
                "severity": "medium"
            })

    # Insight 2: Spending acceleration
    if not month_df.empty:
        prediction = predict_monthly_spending(df, current_month, budget)
        if prediction.get("has_data") and budget > 0:
            if not prediction.get("on_track", True):
                insights.append({
                    "type": "warning",
                    "icon": "🔮",
                    "message": f"At current rate ({prediction['daily_rate']:,.0f} ฿/day), projected total: {prediction['predicted_total']:,.0f} ฿ — exceeds budget by {prediction['over_by']:,.0f} ฿!",
                    "severity": "high"
                })
            elif prediction.get("safe_daily_limit", 0) > 0:
                insights.append({
                    "type": "tip",
                    "icon": "💡",
                    "message": f"Safe to spend up to {prediction['safe_daily_limit']:,.0f} ฿/day for the remaining {prediction['days_remaining']} days.",
                    "severity": "low"
                })

    # Insight 3: Top category alert
    if not month_df.empty:
        cat_totals = month_df.groupby('category')['amount'].sum()
        if len(cat_totals) > 0:
            top_cat = cat_totals.idxmax()
            top_amount = float(cat_totals.max())
            pct_of_total = (top_amount / month_spent * 100) if month_spent > 0 else 0
            if pct_of_total > 50:
                insights.append({
                    "type": "info",
                    "icon": "📌",
                    "message": f"'{top_cat}' dominates your spending ({pct_of_total:.0f}% of total). Consider diversifying.",
                    "severity": "medium"
                })

    # Insight 4: Recurring expenses detected
    recurring = detect_recurring_expenses(df, min_occurrences=2)
    if recurring:
        total_recurring = sum(r['avg_amount'] for r in recurring)
        insights.append({
            "type": "info",
            "icon": "🔁",
            "message": f"Detected {len(recurring)} recurring expense(s) totaling ~{total_recurring:,.0f} ฿/cycle. Top: {recurring[0]['store']} ({recurring[0]['avg_amount']:,.0f} ฿/{recurring[0]['frequency']}).",
            "severity": "medium"
        })

    # Insight 5: Month-over-month comparison
    prev_month = _get_previous_month(current_month)
    prev_df = df[df['date'].str.startswith(prev_month)]
    prev_spent = float(prev_df['amount'].sum()) if not prev_df.empty else 0
    if prev_spent > 0:
        change_pct = ((month_spent - prev_spent) / prev_spent) * 100
        if change_pct > 20:
            insights.append({
                "type": "warning",
                "icon": "📈",
                "message": f"Spending is up {change_pct:.0f}% compared to {prev_month} ({prev_spent:,.0f} ฿ → {month_spent:,.0f} ฿).",
                "severity": "medium"
            })
        elif change_pct < -20:
            insights.append({
                "type": "success",
                "icon": "📉",
                "message": f"Great job! Spending is down {abs(change_pct):.0f}% compared to {prev_month}.",
                "severity": "low"
            })

    # Insight 6: Highest single receipt warning
    if not month_df.empty:
        max_receipt = month_df.loc[month_df['amount'].idxmax()]
        if month_spent > 0 and float(max_receipt['amount']) / month_spent > 0.3:
            insights.append({
                "type": "info",
                "icon": "💰",
                "message": f"Single large expense: {max_receipt['store']} at {float(max_receipt['amount']):,.0f} ฿ ({float(max_receipt['amount'])/month_spent*100:.0f}% of monthly total).",
                "severity": "low"
            })

    return insights


# ==============================
# 🔍 SEARCH ENGINE
# ==============================

def search_receipts(df, query: str):
    """
    Full-text search across store, category, date, and amount.
    Supports multiple search terms with AND logic.
    """
    if df.empty:
        return df

    terms = query.lower().split()
    mask = None

    for term in terms:
        term_mask = (
            df['store'].str.lower().str.contains(term, na=False) |
            df['category'].str.lower().str.contains(term, na=False) |
            df['date'].str.contains(term, na=False) |
            df['amount'].astype(str).str.contains(term, na=False)
        )
        if mask is None:
            mask = term_mask
        else:
            mask = mask & term_mask

    return df[mask] if mask is not None else df


# ==============================
# 🛠️ UTILITY HELPERS
# ==============================

def _safe_parse_date(date_str: str):
    """Safely parse a date string."""
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_str, fmt)
        except (ValueError, TypeError):
            continue
    return None


def _get_previous_month(month_str: str) -> str:
    """Get previous month string from YYYY-MM."""
    try:
        dt = datetime.strptime(month_str + "-01", "%Y-%m-%d")
        prev = dt - timedelta(days=1)
        return prev.strftime("%Y-%m")
    except ValueError:
        return month_str


def format_sparkline(values: list, width: int = 20) -> str:
    """Generate a simple text-based sparkline for trend visualization."""
    if not values:
        return ""
    blocks = "▁▂▃▄▅▆▇█"
    mn = min(values)
    mx = max(values)
    rng = mx - mn if mx != mn else 1
    
    # Sample values to fit width
    if len(values) > width:
        step = len(values) / width
        sampled = [values[int(i * step)] for i in range(width)]
    else:
        sampled = values
    
    return "".join(blocks[min(int((v - mn) / rng * (len(blocks) - 1)), len(blocks) - 1)] for v in sampled)
