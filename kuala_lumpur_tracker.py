import streamlit as st
import json
import os
from datetime import date, datetime

SAVE_FILE = "kl_tracker_data.json"

# Supported currencies. Amounts are stored internally in RM (base currency).
CURRENCIES = {
    "RM": {"symbol": "RM", "rate": 1.0},        # Malaysian Ringgit (base)
    "USD": {"symbol": "$", "rate": 0.21},       # 1 RM ≈ 0.21 USD (fixed rate)
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

    st.title("💰 Kuala Lumpur Pocket Money & Allowance Tracker")
    st.caption("Track your daily allowance and spending. Switch between RM and USD in the sidebar.")
    st.caption("🎯 Savings Goal: set a target in the sidebar and watch your balance grow toward it.")

    # Balance summary
    balance = st.session_state.balance
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
        </style>
        <div class="balance-card">
            <div class="balance-label">Current Balance</div>
            <div class="balance-value">{format_money(balance)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar stats
    with st.sidebar:
        st.header("💱 Currency")
        currency = st.radio(
            "Display currency",
            list(CURRENCIES.keys()),
            index=list(CURRENCIES.keys()).index(st.session_state.currency),
            horizontal=True,
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
        else:
            st.caption("Set a target above to track your progress.")
        st.divider()
        if st.button("🗑️ Reset all data", use_container_width=True):
            st.session_state.balance = 0.0
            st.session_state.transactions = []
            st.session_state.savings_goal = 0.0
            save_data()
            st.rerun()

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
