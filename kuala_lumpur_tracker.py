import streamlit as st
import json
import os
import random
from datetime import date, datetime

SAVE_FILE = "kl_tracker_data.json"

# Supported currencies. Amounts are stored internally in RM (base currency).
# Rates are approximate fixed values: 1 RM ≈ rate units of the target currency.
CURRENCIES = {
    "RM":  {"symbol": "RM", "rate": 1.0},       # Malaysian Ringgit (base)
    "USD": {"symbol": "$",  "rate": 0.21},      # US Dollar
    "EUR": {"symbol": "€",  "rate": 0.20},      # Euro
    "GBP": {"symbol": "£",  "rate": 0.17},      # British Pound
    "JPY": {"symbol": "¥",  "rate": 32.0},      # Japanese Yen
    "CNY": {"symbol": "¥",  "rate": 1.53},      # Chinese Yuan
    "SGD": {"symbol": "S$", "rate": 0.28},      # Singapore Dollar
    "AUD": {"symbol": "A$", "rate": 0.32},      # Australian Dollar
    "INR": {"symbol": "₹",  "rate": 17.5},      # Indian Rupee
}

CATEGORIES = [
    "Allowance",
    "Food",
    "Transport",
    "School",
    "Entertainment",
    "Shopping",
    "Savings",
    "Other",
]

def load_data():
    """Load persisted tracker data from disk, or return defaults."""
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}

def save_data():
    """Persist the current tracker state to disk."""
    data = {
        "balance": st.session_state.get("balance", 0.0),
        "transactions": st.session_state.get("transactions", []),
        "savings_goal": st.session_state.get("savings_goal", 0.0),
        "currency": st.session_state.get("currency", "RM"),
        "goal_celebrated": st.session_state.get("goal_celebrated", False),
        "coins": st.session_state.get("coins", 0),
        "spent_since_coin": st.session_state.get("spent_since_coin", 0.0),
    }
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f)
    except OSError:
        pass

def format_money(amount_rm):
    """Format an RM amount in the currently selected currency."""
    code = st.session_state.get("currency", "RM")
    cur = CURRENCIES.get(code, CURRENCIES["RM"])
    converted = amount_rm * cur["rate"]
    return f"{cur['symbol']} {converted:,.2f}"

def to_display(amount_rm):
    """Convert an RM amount to the currently selected currency (number only)."""
    code = st.session_state.get("currency", "RM")
    return amount_rm * CURRENCIES.get(code, CURRENCIES["RM"])["rate"]

def from_display(amount_display):
    """Convert an amount in the selected currency back to RM."""
    code = st.session_state.get("currency", "RM")
    rate = CURRENCIES.get(code, CURRENCIES["RM"])["rate"]
    return amount_display / rate if rate else amount_display

def add_transaction(kind, amount, category, note):
    """Record a transaction and update the balance."""
    amount = abs(float(amount))
    if kind == "Income":
        st.session_state.balance += amount
        signed = amount
    else:
        st.session_state.balance -= amount
        signed = -amount
        # Every 100 (in the current currency) spent removes one coin
        rate = CURRENCIES.get(st.session_state.get("currency", "RM"), CURRENCIES["RM"])["rate"]
        spent_display = amount * rate
        st.session_state.spent_since_coin += spent_display
        while st.session_state.spent_since_coin >= 100 and st.session_state.coins > 0:
            st.session_state.spent_since_coin -= 100
            st.session_state.coins -= 1
    st.session_state.transactions.append(
        {
            "id": datetime.now().isoformat(),
            "date": str(date.today()),
            "kind": kind,
            "amount": signed,
            "category": category,
            "note": note.strip(),
        }
    )
    save_data()

def main():
    st.set_page_config(
        page_title="KL Pocket Money Tracker",
        page_icon="💰",
        layout="centered",
    )

    saved = load_data()

    if "balance" not in st.session_state:
        st.session_state.balance = saved.get("balance", 0.0)
    if "transactions" not in st.session_state:
        st.session_state.transactions = saved.get("transactions", [])
    if "savings_goal" not in st.session_state:
        st.session_state.savings_goal = saved.get("savings_goal", 0.0)
    if "currency" not in st.session_state:
        st.session_state.currency = saved.get("currency", "RM")
    if "goal_celebrated" not in st.session_state:
        st.session_state.goal_celebrated = saved.get("goal_celebrated", False)
    if "coins" not in st.session_state:
        st.session_state.coins = saved.get("coins", 0)
    if "spent_since_coin" not in st.session_state:
        st.session_state.spent_since_coin = saved.get("spent_since_coin", 0.0)
    if "coin_animate" not in st.session_state:
        st.session_state.coin_animate = False

    # Auto-save on every rerun so progress survives restarts and tab closes
    save_data()

    st.title("💰 Kuala Lumpur Pocket Money & Allowance Tracker")
    st.caption("Track your daily allowance and spending. Switch between RM and USD in the sidebar.")
    st.caption("🎯 Savings Goal: set a target in the sidebar and watch your balance grow toward it.")

    # Balance summary
    balance = st.session_state.balance

    # Coin row: one coin per savings goal reached
    coin_html = "".join(
        f"<span class='coin{' coin-flip' if st.session_state.coin_animate else ''}' "
        f"style='animation-delay:{i * 0.08:.2f}s;'>🪙</span>"
        for i in range(st.session_state.coins)
    )
    if not coin_html:
        coin_html = "<span class='coin-empty'>No coins yet — reach a savings goal to earn one!</span>"

    st.markdown(
        f"""
        <style>
        .balance-card {{
            background: linear-gradient(135deg, #1976d2, #42a5f5);
            color: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 16px;
        }}
        .balance-label {{ font-size: 14px; opacity: 0.9; }}
        .balance-value {{ font-size: 40px; font-weight: bold; }}
        .coin-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            justify-content: center;
            align-items: center;
            padding: 10px;
            margin-bottom: 12px;
            border-radius: 12px;
            background: #fff8e1;
            border: 2px dashed #ffb300;
            min-height: 48px;
        }}
        .coin {{
            display: inline-block;
            font-size: 28px;
            line-height: 1;
            filter: drop-shadow(0 2px 3px rgba(0,0,0,0.25));
        }}
        .coin-empty {{
            font-size: 13px;
            color: #8d6e63;
        }}
        @keyframes coin-flip {{
            0%   {{ transform: rotateY(0deg)   scale(1); }}
            50%  {{ transform: rotateY(180deg) scale(1.3); }}
            100% {{ transform: rotateY(360deg) scale(1); }}
        }}
        .coin-flip {{
            animation: coin-flip 0.9s ease-in-out;
        }}
        </style>
        <div class="coin-row">{coin_html}</div>
        <div class="balance-card">
            <div class="balance-label">Current Balance</div>
            <div class="balance-value">{format_money(balance)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.session_state.coin_animate = False

    # Sidebar stats
    with st.sidebar:
        st.header("💱 Currency")
        currency = st.selectbox(
            "Display currency",
            list(CURRENCIES.keys()),
            index=list(CURRENCIES.keys()).index(st.session_state.currency),
        )
        if currency != st.session_state.currency:
            st.session_state.currency = currency
            save_data()
            st.rerun()

        st.divider()
        st.header("📊 Summary")
        income = sum(t["amount"] for t in st.session_state.transactions if t["amount"] > 0)
        expenses = sum(-t["amount"] for t in st.session_state.transactions if t["amount"] < 0)
        st.metric("Total Income", format_money(income))
        st.metric("Total Spent", format_money(expenses))
        st.metric("Transactions", len(st.session_state.transactions))
        st.divider()
        st.subheader("🎯 Savings Goal")
        goal_display = st.number_input(
            f"Target ({st.session_state.currency})",
            min_value=0.0,
            step=10.0,
            format="%.2f",
            value=float(to_display(st.session_state.savings_goal)),
        )
        goal_rm = from_display(goal_display)
        if abs(goal_rm - st.session_state.savings_goal) > 0.005:
            st.session_state.savings_goal = goal_rm
            save_data()
        if st.session_state.savings_goal > 0:
            pct = min(max(st.session_state.balance / st.session_state.savings_goal, 0.0), 1.0)
            st.progress(
                pct,
                text=f"{format_money(st.session_state.balance)} / {format_money(st.session_state.savings_goal)}",
            )
            if st.session_state.balance >= st.session_state.savings_goal:
                st.success("🎉 Savings goal reached!")
                if not st.session_state.goal_celebrated:
                    st.session_state.goal_celebrated = True
                    st.session_state.coins += 1
                    st.session_state.coin_animate = True
                    save_data()
            else:
                # Reset the celebration flag if the balance drops below the goal
                if st.session_state.goal_celebrated:
                    st.session_state.goal_celebrated = False
                    save_data()
        else:
            st.caption("Set a target above to track your progress.")
        st.divider()
        if st.button("🗑️ Reset all data", use_container_width=True):
            st.session_state.balance = 0.0
            st.session_state.transactions = []
            st.session_state.savings_goal = 0.0
            st.session_state.goal_celebrated = False
            st.session_state.coins = 0
            st.session_state.spent_since_coin = 0.0
            save_data()
            st.rerun()

    # Celebration animation when the savings goal is reached
    if (
        st.session_state.savings_goal > 0
        and st.session_state.balance >= st.session_state.savings_goal
        and st.session_state.goal_celebrated
    ):
        confetti = "".join(
            f"<span class='confetti' style='left:{random.randint(0, 100)}%;"
            f"animation-delay:{random.uniform(0, 1.5):.2f}s;"
            f"animation-duration:{random.uniform(2.0, 3.5):.2f}s;"
            f"background:{random.choice(['#ff5252', '#ffd740', '#69f0ae', '#40c4ff', '#e040fb', '#ffab40'])};'>"
            f"</span>"
            for _ in range(40)
        )
        st.markdown(
            f"""
            <style>
            @keyframes goal-pop {{
                0%   {{ transform: scale(0.5); opacity: 0; }}
                60%  {{ transform: scale(1.15); opacity: 1; }}
                100% {{ transform: scale(1); opacity: 1; }}
            }}
            @keyframes goal-glow {{
                0%   {{ box-shadow: 0 0 10px #ffd740, 0 0 20px #ffab40; }}
                50%  {{ box-shadow: 0 0 25px #ffd740, 0 0 50px #ffab40; }}
                100% {{ box-shadow: 0 0 10px #ffd740, 0 0 20px #ffab40; }}
            }}
            @keyframes confetti-fall {{
                0%   {{ transform: translateY(-20px) rotate(0deg); opacity: 1; }}
                100% {{ transform: translateY(320px) rotate(720deg); opacity: 0; }}
            }}
            .goal-banner {{
                position: relative;
                overflow: hidden;
                text-align: center;
                padding: 24px;
                margin-bottom: 16px;
                border-radius: 16px;
                background: linear-gradient(135deg, #ffd740, #ffab40, #ff5252);
                color: white;
                font-size: 28px;
                font-weight: bold;
                animation: goal-pop 0.8s ease-out, goal-glow 2s ease-in-out infinite;
            }}
            .goal-banner .sub {{
                font-size: 16px;
                font-weight: normal;
                margin-top: 6px;
                opacity: 0.95;
            }}
            .confetti {{
                position: absolute;
                top: 0;
                width: 10px;
                height: 14px;
                border-radius: 2px;
                animation-name: confetti-fall;
                animation-timing-function: ease-in;
                animation-iteration-count: infinite;
            }}
            </style>
            <div class="goal-banner">
                {confetti}
                🎉 Savings Goal Reached! 🎉
                <div class="sub">You hit {format_money(st.session_state.savings_goal)} — amazing work!</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Add transaction form
    st.subheader("➕ Add Transaction")
    with st.form("add_transaction", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            kind = st.selectbox("Type", ["Income", "Expense"])
        with col2:
            amount_display = st.number_input(
                f"Amount ({st.session_state.currency})",
                min_value=0.0,
                step=0.50,
                format="%.2f",
            )
        category = st.selectbox("Category", CATEGORIES)
        note = st.text_input("Note (optional)", placeholder="e.g. Nasi lemak at mamak")
        submitted = st.form_submit_button("Add")

        if submitted:
            if amount_display <= 0:
                st.error("Please enter an amount greater than 0.")
            else:
                amount_rm = from_display(amount_display)
                add_transaction(kind, amount_rm, category, note)
                st.success(f"Added {kind.lower()}: {format_money(amount_rm)}")
                st.rerun()

    # Transaction history
    st.subheader("📜 Transaction History")
    if not st.session_state.transactions:
        st.info("No transactions yet. Add your first allowance or expense above!")
    else:
        # Filter by category
        filter_cat = st.selectbox("Filter by category", ["All"] + CATEGORIES)
        rows = st.session_state.transactions
        if filter_cat != "All":
            rows = [t for t in rows if t["category"] == filter_cat]

        # Show newest first
        for t in reversed(rows):
            is_income = t["amount"] > 0
            color = "#2e7d32" if is_income else "#c62828"
            sign = "+" if is_income else "-"
            note = f" — {t['note']}" if t.get("note") else ""
            st.markdown(
                f"""
                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 10px 14px;
                    margin-bottom: 6px;
                    border-radius: 8px;
                    border-left: 5px solid {color};
                    background: #fafafa;
                ">
                    <div>
                        <div style="font-weight: bold;">{t['category']}{note}</div>
                        <div style="font-size: 12px; color: #666;">{t['date']}</div>
                    </div>
                    <div style="font-weight: bold; color: {color};">
                        {sign}{format_money(abs(t['amount']))}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Delete a transaction
        with st.expander("Delete a transaction"):
            options = {
                f"{t['date']} · {t['category']} · {format_money(abs(t['amount']))}": i
                for i, t in enumerate(st.session_state.transactions)
            }
            choice = st.selectbox("Select transaction", list(options.keys()))
            if st.button("Delete selected"):
                idx = options[choice]
                removed = st.session_state.transactions.pop(idx)
                # Reverse the balance effect
                st.session_state.balance -= removed["amount"]
                save_data()
                st.rerun()

if __name__ == "__main__":
    main()
