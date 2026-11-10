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

# Popular items you could buy, priced in RM (base currency).
# Prices are approximate typical prices. Each item is tagged with the
# currency "zone" it belongs to, so the shop only shows items relevant
# to the currently selected currency.
SHOP_ITEMS = [
    # ---- Malaysia (RM) ----
    {"name": "Nasi Lemak",            "emoji": "🍚", "price": 3.50,  "category": "Food",          "currency": "RM"},
    {"name": "Roti Canai",            "emoji": "🫓", "price": 2.00,  "category": "Food",          "currency": "RM"},
    {"name": "Mee Goreng",            "emoji": "🍜", "price": 7.00,  "category": "Food",          "currency": "RM"},
    {"name": "Chicken Rice",          "emoji": "🍗", "price": 9.00,  "category": "Food",          "currency": "RM"},
    {"name": "Teh Tarik",             "emoji": "🧋", "price": 2.50,  "category": "Food",          "currency": "RM"},
    {"name": "Bubble Tea",            "emoji": "🥤", "price": 12.00, "category": "Food",          "currency": "RM"},
    {"name": "LRT/MRT Ride",          "emoji": "🚇", "price": 3.00,  "category": "Transport",     "currency": "RM"},
    {"name": "Grab Ride (short)",     "emoji": "🚗", "price": 12.00, "category": "Transport",     "currency": "RM"},
    {"name": "Petrol (1 litre)",      "emoji": "⛽", "price": 2.05,  "category": "Transport",     "currency": "RM"},
    {"name": "School Bag",            "emoji": "🎒", "price": 80.00, "category": "School",        "currency": "RM"},
    {"name": "Cinema Ticket",         "emoji": "🎬", "price": 20.00, "category": "Entertainment", "currency": "RM"},
    {"name": "Mobile Game Top-up",    "emoji": "🎮", "price": 15.00, "category": "Entertainment", "currency": "RM"},
    {"name": "Spotify (1 month)",     "emoji": "🎵", "price": 17.00, "category": "Entertainment", "currency": "RM"},
    {"name": "Netflix (1 month)",     "emoji": "📺", "price": 28.00, "category": "Entertainment", "currency": "RM"},
    {"name": "Roblox Robux (400)",    "emoji": "🟥", "price": 20.00, "category": "Games",         "currency": "RM"},
    {"name": "Roblox Robux (800)",    "emoji": "🟥", "price": 40.00, "category": "Games",         "currency": "RM"},
    {"name": "Minecraft Minecoins",   "emoji": "⛏️", "price": 15.00, "category": "Games",         "currency": "RM"},
    {"name": "Fortnite V-Bucks",      "emoji": "🪂", "price": 35.00, "category": "Games",         "currency": "RM"},
    {"name": "Roblox Gift Card",      "emoji": "🎁", "price": 50.00, "category": "Games",         "currency": "RM"},
    {"name": "Steam Gift Card",       "emoji": "🎮", "price": 50.00, "category": "Games",         "currency": "RM"},
    {"name": "Nintendo eShop Card",   "emoji": "🍄", "price": 60.00, "category": "Games",         "currency": "RM"},
    {"name": "Among Us",              "emoji": "👾", "price": 12.00, "category": "Games",         "currency": "RM"},
    {"name": "Minecraft (PC)",        "emoji": "🧱", "price": 120.00, "category": "Games",        "currency": "RM"},
    {"name": "Lego Set (small)",      "emoji": "🧩", "price": 45.00, "category": "Toys",          "currency": "RM"},
    {"name": "Lego Set (large)",      "emoji": "🧱", "price": 250.00, "category": "Toys",         "currency": "RM"},
    {"name": "Stuffed Bear",          "emoji": "🧸", "price": 40.00, "category": "Toys",          "currency": "RM"},
    {"name": "Stuffed Bunny",         "emoji": "🐰", "price": 35.00, "category": "Toys",          "currency": "RM"},
    {"name": "Stuffed Unicorn",       "emoji": "🦄", "price": 55.00, "category": "Toys",          "currency": "RM"},
    {"name": "Stuffed Dinosaur",      "emoji": "🦖", "price": 50.00, "category": "Toys",          "currency": "RM"},
    {"name": "Hot Wheels Car",        "emoji": "🏎️", "price": 15.00, "category": "Toys",         "currency": "RM"},
    {"name": "Rubik's Cube",          "emoji": "🧊", "price": 20.00, "category": "Toys",          "currency": "RM"},
    {"name": "Yo-Yo",                 "emoji": "🪀", "price": 10.00, "category": "Toys",          "currency": "RM"},
    {"name": "Fidget Spinner",        "emoji": "🌀", "price": 8.00,  "category": "Toys",          "currency": "RM"},
    {"name": "Squishmallow",          "emoji": "🫧", "price": 60.00, "category": "Toys",          "currency": "RM"},
    {"name": "Pokémon Cards (pack)",  "emoji": "🃏", "price": 12.00, "category": "Toys",          "currency": "RM"},
    {"name": "Nerf Blaster",          "emoji": "🔫", "price": 90.00, "category": "Toys",          "currency": "RM"},
    {"name": "Board Game",            "emoji": "🎲", "price": 70.00, "category": "Toys",          "currency": "RM"},
    {"name": "Scooter",               "emoji": "🛴", "price": 300.00, "category": "Toys",         "currency": "RM"},
    {"name": "Ice Cream",             "emoji": "🍦", "price": 5.00,  "category": "Food",          "currency": "RM"},
    {"name": "Chocolate Bar",         "emoji": "🍫", "price": 4.00,  "category": "Food",          "currency": "RM"},
    {"name": "Gummy Bears",           "emoji": "🐻", "price": 6.00,  "category": "Food",          "currency": "RM"},
    {"name": "Donut",                 "emoji": "🍩", "price": 4.50,  "category": "Food",          "currency": "RM"},
    {"name": "Cupcake",               "emoji": "🧁", "price": 7.00,  "category": "Food",          "currency": "RM"},

    # ---- United States (USD) ----
    {"name": "Hamburger",             "emoji": "🍔", "price": 30.00, "category": "Food",          "currency": "USD"},
    {"name": "Hot Dog",               "emoji": "🌭", "price": 12.00, "category": "Food",          "currency": "USD"},
    {"name": "Pizza Slice",           "emoji": "🍕", "price": 15.00, "category": "Food",          "currency": "USD"},
    {"name": "Donut (US)",            "emoji": "🍩", "price": 10.00, "category": "Food",          "currency": "USD"},
    {"name": "Starbucks Coffee",      "emoji": "☕", "price": 25.00, "category": "Food",          "currency": "USD"},
    {"name": "Yellow School Bus Ride", "emoji": "🚌", "price": 10.00, "category": "Transport",    "currency": "USD"},
    {"name": "Uber Ride",             "emoji": "🚕", "price": 60.00, "category": "Transport",     "currency": "USD"},
    {"name": "Baseball Cap",          "emoji": "🧢", "price": 90.00, "category": "Shopping",      "currency": "USD"},
    {"name": "Basketball",            "emoji": "🏀", "price": 120.00, "category": "Toys",         "currency": "USD"},
    {"name": "American Football",     "emoji": "🏈", "price": 150.00, "category": "Toys",         "currency": "USD"},
    {"name": "Nintendo Switch Game",  "emoji": "🎮", "price": 250.00, "category": "Games",        "currency": "USD"},
    {"name": "Amazon Gift Card",      "emoji": "📦", "price": 100.00, "category": "Shopping",     "currency": "USD"},

    # ---- Europe (EUR) ----
    {"name": "Croissant",             "emoji": "🥐", "price": 12.00, "category": "Food",          "currency": "EUR"},
    {"name": "Baguette",              "emoji": "🥖", "price": 8.00,  "category": "Food",          "currency": "EUR"},
    {"name": "Gelato",                "emoji": "🍨", "price": 15.00, "category": "Food",          "currency": "EUR"},
    {"name": "Pretzel",               "emoji": "🥨", "price": 10.00, "category": "Food",          "currency": "EUR"},
    {"name": "Euro Train Ticket",     "emoji": "🚆", "price": 80.00, "category": "Transport",     "currency": "EUR"},
    {"name": "Soccer Ball",           "emoji": "⚽", "price": 100.00, "category": "Toys",         "currency": "EUR"},
    {"name": "Museum Ticket",         "emoji": "🏛️", "price": 60.00, "category": "Entertainment", "currency": "EUR"},

    # ---- United Kingdom (GBP) ----
    {"name": "Fish and Chips",        "emoji": "🍟", "price": 45.00, "category": "Food",          "currency": "GBP"},
    {"name": "Tea and Scones",        "emoji": "🫖", "price": 25.00, "category": "Food",          "currency": "GBP"},
    {"name": "Double Decker Bus",     "emoji": "🚌", "price": 15.00, "category": "Transport",     "currency": "GBP"},
    {"name": "Premier League Jersey", "emoji": "👕", "price": 350.00, "category": "Shopping",     "currency": "GBP"},
    {"name": "Harry Potter Book",     "emoji": "📚", "price": 60.00, "category": "Entertainment", "currency": "GBP"},

    # ---- Japan (JPY) ----
    {"name": "Sushi Set",             "emoji": "🍣", "price": 120.00, "category": "Food",         "currency": "JPY"},
    {"name": "Ramen Bowl",            "emoji": "🍜", "price": 45.00, "category": "Food",          "currency": "JPY"},
    {"name": "Onigiri",               "emoji": "🍙", "price": 8.00,  "category": "Food",          "currency": "JPY"},
    {"name": "Matcha Ice Cream",      "emoji": "🍦", "price": 20.00, "category": "Food",          "currency": "JPY"},
    {"name": "Shinkansen Ticket",     "emoji": "🚄", "price": 700.00, "category": "Transport",    "currency": "JPY"},
    {"name": "Gachapon",              "emoji": "🎰", "price": 15.00, "category": "Toys",          "currency": "JPY"},
    {"name": "Anime Figure",          "emoji": "🗿", "price": 250.00, "category": "Toys",         "currency": "JPY"},
    {"name": "Nintendo Game (JP)",    "emoji": "🎮", "price": 300.00, "category": "Games",        "currency": "JPY"},

    # ---- China (CNY) ----
    {"name": "Dumplings",             "emoji": "🥟", "price": 20.00, "category": "Food",          "currency": "CNY"},
    {"name": "Bubble Tea (CN)",       "emoji": "🧋", "price": 15.00, "category": "Food",          "currency": "CNY"},
    {"name": "Peking Duck",           "emoji": "🦆", "price": 150.00, "category": "Food",         "currency": "CNY"},
    {"name": "High-Speed Rail Ticket", "emoji": "🚄", "price": 200.00, "category": "Transport",   "currency": "CNY"},
    {"name": "Mahjong Set",           "emoji": "🀄", "price": 120.00, "category": "Toys",         "currency": "CNY"},
    {"name": "Kite",                  "emoji": "🪁", "price": 30.00, "category": "Toys",          "currency": "CNY"},

    # ---- Singapore (SGD) ----
    {"name": "Chicken Rice (SG)",     "emoji": "🍗", "price": 5.00,  "category": "Food",          "currency": "SGD"},
    {"name": "Chili Crab",            "emoji": "🦀", "price": 60.00, "category": "Food",          "currency": "SGD"},
    {"name": "Kaya Toast",            "emoji": "🍞", "price": 4.00,  "category": "Food",          "currency": "SGD"},
    {"name": "MRT Ride (SG)",         "emoji": "🚇", "price": 2.00,  "category": "Transport",     "currency": "SGD"},
    {"name": "Merlion Souvenir",      "emoji": "🦁", "price": 15.00, "category": "Toys",          "currency": "SGD"},

    # ---- Australia (AUD) ----
    {"name": "Meat Pie",              "emoji": "🥧", "price": 8.00,  "category": "Food",          "currency": "AUD"},
    {"name": "Vegemite Toast",        "emoji": "🍞", "price": 5.00,  "category": "Food",          "currency": "AUD"},
    {"name": "Kangaroo Plush",        "emoji": "🦘", "price": 30.00, "category": "Toys",          "currency": "AUD"},
    {"name": "Surfboard",             "emoji": "🏄", "price": 400.00, "category": "Toys",         "currency": "AUD"},
    {"name": "Boomerang",             "emoji": "🪃", "price": 20.00, "category": "Toys",          "currency": "AUD"},

    # ---- India (INR) ----
    {"name": "Samosa",                "emoji": "🥟", "price": 20.00, "category": "Food",          "currency": "INR"},
    {"name": "Butter Chicken",        "emoji": "🍛", "price": 350.00, "category": "Food",         "currency": "INR"},
    {"name": "Masala Chai",           "emoji": "🫖", "price": 15.00, "category": "Food",          "currency": "INR"},
    {"name": "Auto Rickshaw Ride",    "emoji": "🛺", "price": 50.00, "category": "Transport",     "currency": "INR"},
    {"name": "Cricket Bat",           "emoji": "🏏", "price": 800.00, "category": "Toys",         "currency": "INR"},
    {"name": "Cricket Ball",          "emoji": "🔴", "price": 150.00, "category": "Toys",         "currency": "INR"},
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
        "earned_since_coin": st.session_state.get("earned_since_coin", 0.0),
        "trophies": st.session_state.get("trophies", []),
        "announcement_dismissed": st.session_state.get("announcement_dismissed", False),
        "elon_announced": st.session_state.get("elon_announced", False),
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
        # Every 100 (in the current currency) earned awards one gold coin
        rate = CURRENCIES.get(st.session_state.get("currency", "RM"), CURRENCIES["RM"])["rate"]
        earned_display = amount * rate
        st.session_state.earned_since_coin += earned_display
        while st.session_state.earned_since_coin >= 100:
            st.session_state.earned_since_coin -= 100
            st.session_state.coins += 1
            st.session_state.coin_animate = True
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

# Milestone badges: (id, label, emoji, description, condition)
def get_advancements():
    """Return a list of advancement dicts with unlocked status."""
    coins = st.session_state.get("coins", 0)
    trophies = st.session_state.get("trophies", [])
    txns = st.session_state.get("transactions", [])
    income = sum(t["amount"] for t in txns if t["amount"] > 0)
    expenses = sum(-t["amount"] for t in txns if t["amount"] < 0)
    balance = st.session_state.get("balance", 0.0)

    categories_used = {t["category"] for t in txns}
    balance_display = to_display(balance)

    defs = [
        # Getting started
        ("first_txn", "First Step", "👣", "Log your first transaction", len(txns) >= 1),
        ("first_income", "Allowance Day", "💵", "Record your first income", income > 0),
        ("first_expense", "Spender", "🛒", "Record your first expense", expenses > 0),
        ("first_note", "Note Taker", "📝", "Add a note to a transaction", any(t.get("note") for t in txns)),
        # Coins
        ("first_coin", "First Coin", "🪙", "Earn your first gold coin", coins >= 1),
        ("coins_5", "Coin Collector", "💰", "Earn 5 gold coins", coins >= 5),
        ("coins_10", "Coin Hoarder", "🏦", "Earn 10 gold coins", coins >= 10),
        ("coins_25", "Coin Tycoon", "🤑", "Earn 25 gold coins", coins >= 25),
        ("coins_50", "Coin Baron", "🏛️", "Earn 50 gold coins", coins >= 50),
        # Trophies
        ("first_trophy", "Goal Getter", "🏆", "Reach your first savings goal", len(trophies) >= 1),
        ("trophies_3", "Trophy Hunter", "🎖️", "Collect 3 trophies", len(trophies) >= 3),
        ("trophies_5", "Champion", "👑", "Collect 5 trophies", len(trophies) >= 5),
        ("trophies_10", "Legend", "🌟", "Collect 10 trophies", len(trophies) >= 10),
        # Balance milestones (in current display currency)
        ("balance_100", "Saver", "🌱", "Reach a balance of 100", balance_display >= 100),
        ("balance_500", "Big Saver", "🌳", "Reach a balance of 500", balance_display >= 500),
        ("balance_1000", "Money Master", "💎", "Reach a balance of 1000", balance_display >= 1000),
        ("balance_5000", "Wealthy", "🏰", "Reach a balance of 5000", balance_display >= 5000),
        ("balance_10000", "Elon Mode", "🚀", "Reach a balance of 10,000", balance_display >= 10000),
        # Transaction counts
        ("txns_10", "Consistent", "📈", "Log 10 transactions", len(txns) >= 10),
        ("txns_25", "Habit Builder", "🗓️", "Log 25 transactions", len(txns) >= 25),
        ("txns_50", "Dedicated", "🔥", "Log 50 transactions", len(txns) >= 50),
        ("txns_100", "Centurion", "💯", "Log 100 transactions", len(txns) >= 100),
        # Category variety
        ("cat_3", "Explorer", "🧭", "Use 3 different categories", len(categories_used) >= 3),
        ("cat_5", "Well Rounded", "🎯", "Use 5 different categories", len(categories_used) >= 5),
        ("cat_all", "Jack of All Trades", "🌈", "Use every category", len(categories_used) >= len(CATEGORIES)),
        # Spending / saving behaviour
        ("spent_100", "Big Spender", "💸", "Spend a total of 100", to_display(expenses) >= 100),
        ("spent_500", "Shopping Spree", "🛍️", "Spend a total of 500", to_display(expenses) >= 500),
        ("income_1000", "Earner", "💼", "Earn a total income of 1000", to_display(income) >= 1000),
    ]
    return [
        {"id": i, "label": l, "emoji": e, "desc": d, "unlocked": bool(c)}
        for (i, l, e, d, c) in defs
    ]


def shop_page():
    st.title("🛍️ What Can I Buy?")
    st.caption("Popular items and what your current balance can afford.")

    balance_display = to_display(st.session_state.balance)
    st.markdown(
        f"""
        <div style="
            text-align: center;
            padding: 16px;
            border-radius: 12px;
            background: linear-gradient(135deg, #1976d2, #42a5f5);
            color: white;
            margin-bottom: 16px;
        ">
            <div style="font-size: 14px; opacity: 0.9;">Your balance</div>
            <div style="font-size: 32px; font-weight: bold;">{format_money(st.session_state.balance)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Only show items relevant to the currently selected currency zone
    zone_items = [i for i in SHOP_ITEMS if i.get("currency") == st.session_state.currency]
    st.caption(f"Showing items for the **{st.session_state.currency}** zone.")

    # Filter by category
    shop_categories = sorted({item["category"] for item in zone_items})
    filter_cat = st.selectbox("Filter by category", ["All"] + shop_categories)
    items = zone_items if filter_cat == "All" else [i for i in zone_items if i["category"] == filter_cat]

    # Only show items you can currently afford, cheapest first
    affordable = sorted(
        (i for i in items if to_display(i["price"]) <= balance_display),
        key=lambda i: i["price"],
    )

    if not affordable:
        st.info("You can't afford anything in this category yet — keep saving! 💪")
        return

    st.write(f"You can afford **{len(affordable)}** item(s).")

    # Render item cards
    card_html = ""
    for item in affordable:
        card_html += (
            f"<div class='shop-card' style='background: linear-gradient(135deg, #e8f5e9, #c8e6c9);"
            f"border: 2px solid #43a047;'>"
            f"<div class='shop-emoji'>{item['emoji']}</div>"
            f"<div class='shop-name'>{item['name']}</div>"
            f"<div class='shop-price'>{format_money(item['price'])}</div>"
            f"<div class='shop-badge'><span style='color:#2e7d32;font-weight:bold;'>✔ Affordable</span></div>"
            f"</div>"
        )

    st.markdown(
        f"""
        <style>
        .shop-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 12px;
            margin-top: 8px;
        }}
        .shop-card {{
            text-align: center;
            padding: 14px 10px;
            border-radius: 12px;
        }}
        .shop-emoji {{ font-size: 36px; line-height: 1; }}
        .shop-name {{ font-weight: bold; margin-top: 6px; font-size: 14px; }}
        .shop-price {{ font-size: 13px; color: #555; margin-top: 2px; }}
        .shop-badge {{ font-size: 12px; margin-top: 6px; }}
        </style>
        <div class="shop-grid">{card_html}</div>
        """,
        unsafe_allow_html=True,
    )


def advancements_page():
    st.title("🏅 Advancements")
    st.caption("All your achievements in one place — coins, trophies, and milestone badges.")

    advancements = get_advancements()
    unlocked = [a for a in advancements if a["unlocked"]]
    total = len(advancements)
    pct = len(unlocked) / total if total else 0.0

    st.progress(pct, text=f"{len(unlocked)} / {total} advancements unlocked")

    # Summary metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("🪙 Coins", st.session_state.get("coins", 0))
    c2.metric("🏆 Trophies", len(st.session_state.get("trophies", [])))
    c3.metric("🏅 Badges", f"{len(unlocked)}/{total}")

    st.divider()

    # Badge grid
    st.subheader("Milestone Badges")
    badge_html = ""
    for a in advancements:
        if a["unlocked"]:
            style = (
                "background: linear-gradient(135deg, #fff8e1, #ffe0b2);"
                "border: 2px solid #ffb300;"
                "box-shadow: 0 3px 10px rgba(255,179,0,0.4);"
            )
            icon_style = "filter: none;"
            label_color = "#b8860b"
        else:
            style = (
                "background: #f5f5f5;"
                "border: 2px dashed #bdbdbd;"
                "opacity: 0.6;"
            )
            icon_style = "filter: grayscale(1);"
            label_color = "#9e9e9e"
        badge_html += (
            f"<div class='badge' style='{style}'>"
            f"<div class='badge-icon' style='{icon_style}'>{a['emoji']}</div>"
            f"<div class='badge-label' style='color:{label_color};'>{a['label']}</div>"
            f"<div class='badge-desc'>{a['desc']}</div>"
            f"</div>"
        )
    st.markdown(
        f"""
        <style>
        .badge-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
            gap: 12px;
            margin-top: 8px;
        }}
        .badge {{
            text-align: center;
            padding: 14px 10px;
            border-radius: 12px;
        }}
        .badge-icon {{ font-size: 36px; line-height: 1; }}
        .badge-label {{ font-weight: bold; margin-top: 6px; font-size: 14px; }}
        .badge-desc {{ font-size: 11px; color: #757575; margin-top: 2px; }}
        </style>
        <div class="badge-grid">{badge_html}</div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # Trophy room (reused view)
    st.subheader("🏆 Trophy Room")
    trophies = st.session_state.get("trophies", [])
    if not trophies:
        st.info("No trophies yet — reach a savings goal to earn one!")
    else:
        trophy_html = "".join(
            f"<div class='trophy'>"
            f"<div class='trophy-icon'>🏆</div>"
            f"<div class='trophy-goal'>{t['currency']} {t['goal']:,.2f}</div>"
            f"<div class='trophy-date'>{t['date']}</div>"
            f"</div>"
            for t in trophies
        )
        st.markdown(
            f"""
            <style>
            .trophy-shelf {{
                display: flex;
                flex-wrap: nowrap;
                gap: 12px;
                padding: 16px;
                border-radius: 12px;
                background: linear-gradient(180deg, #fff8e1, #ffe0b2);
                border: 2px solid #ffb300;
                overflow-x: auto;
                overflow-y: hidden;
                scroll-behavior: smooth;
                -webkit-overflow-scrolling: touch;
            }}
            .trophy {{
                flex: 0 0 auto;
                text-align: center;
                padding: 12px 16px;
                border-radius: 10px;
                background: white;
                border: 2px solid #ffd740;
                box-shadow: 0 3px 8px rgba(0,0,0,0.15);
                min-width: 100px;
            }}
            .trophy-icon {{ font-size: 40px; line-height: 1; }}
            .trophy-goal {{ font-weight: bold; color: #b8860b; margin-top: 4px; }}
            .trophy-date {{ font-size: 12px; color: #8d6e63; }}
            </style>
            <div class="trophy-shelf">{trophy_html}</div>
            """,
            unsafe_allow_html=True,
        )


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
    if "earned_since_coin" not in st.session_state:
        st.session_state.earned_since_coin = saved.get("earned_since_coin", 0.0)
    if "trophies" not in st.session_state:
        st.session_state.trophies = saved.get("trophies", [])
    if "coin_animate" not in st.session_state:
        st.session_state.coin_animate = False
    if "announcement_dismissed" not in st.session_state:
        st.session_state.announcement_dismissed = saved.get("announcement_dismissed", False)
    if "page" not in st.session_state:
        st.session_state.page = "Tracker"
    if "elon_announced" not in st.session_state:
        st.session_state.elon_announced = saved.get("elon_announced", False)

    # Auto-save on every rerun so progress survives restarts and tab closes
    save_data()

    st.title("💰 Kuala Lumpur Pocket Money & Allowance Tracker")
    st.caption("Track your daily allowance and spending. Switch between RM and USD in the sidebar.")
    st.caption("🎯 Savings Goal: set a target in the sidebar and watch your balance grow toward it.")

    # Announcement banner (dismissible, persisted)
    if not st.session_state.announcement_dismissed:
        st.markdown(
            """
            <style>
            @keyframes announce-slide {
                0%   { transform: translateY(-20px); opacity: 0; }
                100% { transform: translateY(0);     opacity: 1; }
            }
            .announcement {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 14px 18px;
                margin-bottom: 16px;
                border-radius: 12px;
                background: linear-gradient(135deg, #fff3cd, #ffe0b2);
                border-left: 6px solid #ffb300;
                color: #5d4037;
                font-size: 15px;
                animation: announce-slide 0.5s ease-out;
            }
            .announcement .icon { font-size: 24px; }
            .announcement .title { font-weight: bold; }
            </style>
            <div class="announcement">
                <span class="icon">📢</span>
                <div>
                    <div class="title">Welcome to your Pocket Money Tracker!</div>
                    <div>Log your allowance and spending, set a savings goal, and earn gold coins and trophies along the way. 🪙🏆</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Dismiss announcement"):
            st.session_state.announcement_dismissed = True
            save_data()
            st.rerun()

    # Sidebar stats
    with st.sidebar:
        st.header("🧭 Navigation")
        pages = ["Tracker", "Advancements", "Shop"]
        page = st.radio(
            "Go to",
            pages,
            index=pages.index(st.session_state.page) if st.session_state.page in pages else 0,
        )
        if page != st.session_state.page:
            st.session_state.page = page
            st.rerun()

        st.divider()
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
                    st.session_state.trophies.append(
                        {
                            "goal": st.session_state.savings_goal,
                            "currency": st.session_state.currency,
                            "date": str(date.today()),
                        }
                    )
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
            st.session_state.earned_since_coin = 0.0
            st.session_state.trophies = []
            st.session_state.announcement_dismissed = False
            st.session_state.elon_announced = False
            save_data()
            st.rerun()

    # Top navigation bar
    nav_tracker, nav_adv, nav_shop, _ = st.columns([1, 1, 1, 3])
    with nav_tracker:
        if st.button("💰 Tracker", use_container_width=True):
            st.session_state.page = "Tracker"
            st.rerun()
    with nav_adv:
        if st.button("🏅 Advancements", use_container_width=True):
            st.session_state.page = "Advancements"
            st.rerun()
    with nav_shop:
        if st.button("🛍️ Shop", use_container_width=True):
            st.session_state.page = "Shop"
            st.rerun()

    # Advancements page
    if st.session_state.page == "Advancements":
        advancements_page()
        return

    # Shop page
    if st.session_state.page == "Shop":
        shop_page()
        return

    # Balance summary (rendered after the sidebar so coin updates show immediately)
    balance = st.session_state.balance

    # Coin row: individual coins up to 10, then a single coin with a count
    coins = st.session_state.coins
    flip_class = " coin-flip" if st.session_state.coin_animate else ""
    if coins == 0:
        coin_html = "<span class='coin-empty'>No coins yet — earn 100 to get a gold coin!</span>"
    elif coins <= 10:
        coin_html = "".join(
            f"<span class='coin{flip_class}' "
            f"style='animation-delay:{i * 0.08:.2f}s;'>🪙</span>"
            for i in range(coins)
        )
    else:
        coin_html = (
            f"<span class='coin{flip_class}'>🪙</span>"
            f"<span class='coin-count'>× {coins}</span>"
        )

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
            filter: sepia(1) saturate(6) hue-rotate(-10deg) brightness(1.1)
                    drop-shadow(0 2px 3px rgba(0,0,0,0.25));
        }}
        .coin-empty {{
            font-size: 13px;
            color: #8d6e63;
        }}
        .coin-count {{
            font-size: 24px;
            font-weight: bold;
            color: #b8860b;
            margin-left: 4px;
        }}
        .coin-note {{
            text-align: center;
            font-size: 12px;
            color: #8d6e63;
            margin: -6px 0 12px 0;
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
        <div class="coin-note">Each coin = 100 earned</div>
        <div class="balance-card">
            <div class="balance-label">Current Balance</div>
            <div class="balance-value">{format_money(balance)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.session_state.coin_animate = False

    # Elon Musk announcement: fires once when the balance reaches 10,000 (in current currency)
    if not st.session_state.elon_announced and to_display(st.session_state.balance) >= 10000:
        st.session_state.elon_announced = True
        save_data()
        st.markdown(
            """
            <style>
            @keyframes elon-pop {
                0%   { transform: scale(0.6) rotate(-3deg); opacity: 0; }
                60%  { transform: scale(1.08) rotate(1deg); opacity: 1; }
                100% { transform: scale(1) rotate(0deg); opacity: 1; }
            }
            @keyframes elon-glow {
                0%   { box-shadow: 0 0 12px #00c2ff, 0 0 24px #7b2ff7; }
                50%  { box-shadow: 0 0 30px #00c2ff, 0 0 60px #7b2ff7; }
                100% { box-shadow: 0 0 12px #00c2ff, 0 0 24px #7b2ff7; }
            }
            .elon-banner {
                text-align: center;
                padding: 24px;
                margin-bottom: 16px;
                border-radius: 16px;
                background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
                color: white;
                animation: elon-pop 0.8s ease-out, elon-glow 2.5s ease-in-out infinite;
            }
            .elon-banner .rocket { font-size: 48px; }
            .elon-banner .title { font-size: 26px; font-weight: bold; margin-top: 6px; }
            .elon-banner .sub { font-size: 15px; opacity: 0.9; margin-top: 6px; }
            </style>
            <div class="elon-banner">
                <div class="rocket">🚀</div>
                <div class="title">Elon Musk</div>
                <div class="sub">You reached 10,000! To the moon! 🌕</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

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

    # Trophy room: one trophy per savings goal reached
    st.subheader("🏆 Trophy Room")
    if not st.session_state.trophies:
        st.info("No trophies yet — reach a savings goal to earn one!")
    else:
        trophy_html = "".join(
            f"<div class='trophy'>"
            f"<div class='trophy-icon'>🏆</div>"
            f"<div class='trophy-goal'>{t['currency']} {t['goal']:,.2f}</div>"
            f"<div class='trophy-date'>{t['date']}</div>"
            f"</div>"
            for t in st.session_state.trophies
        )
        st.markdown(
            f"""
            <style>
            .trophy-shelf {{
                display: flex;
                flex-wrap: nowrap;
                gap: 12px;
                padding: 16px;
                border-radius: 12px;
                background: linear-gradient(180deg, #fff8e1, #ffe0b2);
                border: 2px solid #ffb300;
                overflow-x: auto;
                overflow-y: hidden;
                scroll-behavior: smooth;
                -webkit-overflow-scrolling: touch;
            }}
            .trophy-shelf::-webkit-scrollbar {{
                height: 8px;
            }}
            .trophy-shelf::-webkit-scrollbar-thumb {{
                background: #ffb300;
                border-radius: 4px;
            }}
            .trophy-shelf::-webkit-scrollbar-track {{
                background: #fff3cd;
                border-radius: 4px;
            }}
            .trophy {{
                flex: 0 0 auto;
                text-align: center;
                padding: 12px 16px;
                border-radius: 10px;
                background: white;
                border: 2px solid #ffd740;
                box-shadow: 0 3px 8px rgba(0,0,0,0.15);
                min-width: 100px;
            }}
            .trophy-icon {{ font-size: 40px; line-height: 1; }}
            .trophy-goal {{ font-weight: bold; color: #b8860b; margin-top: 4px; }}
            .trophy-date {{ font-size: 12px; color: #8d6e63; }}
            </style>
            <div class="trophy-shelf">{trophy_html}</div>
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
