import streamlit as st
import json
import os
from datetime import date, datetime

SAVE_FILE = "kl_tracker_data.json"

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
    }
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f)
    except OSError:
        pass

def format_rm(amount):
    """Format a number as Malaysian Ringgit."""
    return f"RM {amount:,.2f}"

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

    st.title("💰 Kuala Lumpur Pocket Money & Allowance Tracker")
    st.caption("Track your daily allowance and spending in Malaysian Ringgit (RM).")

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
            <div class="balance-value">{format_rm(balance)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar stats
    with st.sidebar:
        st.header("📊 Summary")
        income = sum(t["amount"] for t in st.session_state.transactions if t["amount"] > 0)
        expenses = sum(-t["amount"] for t in st.session_state.transactions if t["amount"] < 0)
        st.metric("Total Income", format_rm(income))
        st.metric("Total Spent", format_rm(expenses))
        st.metric("Transactions", len(st.session_state.transactions))
        st.divider()
        if st.button("🗑️ Reset all data", use_container_width=True):
            st.session_state.balance = 0.0
            st.session_state.transactions = []
            save_data()
            st.rerun()

    # Add transaction form
    st.subheader("➕ Add Transaction")
    with st.form("add_transaction", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            kind = st.selectbox("Type", ["Income", "Expense"])
        with col2:
            amount = st.number_input("Amount (RM)", min_value=0.0, step=0.50, format="%.2f")
        category = st.selectbox("Category", CATEGORIES)
        note = st.text_input("Note (optional)", placeholder="e.g. Nasi lemak at mamak")
        submitted = st.form_submit_button("Add")

        if submitted:
            if amount <= 0:
                st.error("Please enter an amount greater than 0.")
            else:
                add_transaction(kind, amount, category, note)
                st.success(f"Added {kind.lower()}: {format_rm(amount)}")
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
                        {sign}{format_rm(abs(t['amount']))}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Delete a transaction
        with st.expander("Delete a transaction"):
            options = {
                f"{t['date']} · {t['category']} · {format_rm(abs(t['amount']))}": i
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
