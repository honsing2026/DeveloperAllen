import streamlit as st
import time
import uuid
import random
import json
import os

SAVE_FILE = "save_data.json"

def load_save():
    """Load persisted game data from disk, or return defaults."""
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}

def save_game():
    """Persist the current game state to disk."""
    data = {
        "xp": st.session_state.get("xp", 0),
        "garden": st.session_state.get("garden", []),
        "tasks": st.session_state.get("tasks", []),
        "clock_skin": st.session_state.get("clock_skin", "Classic"),
    }
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f)
    except OSError:
        pass

# Tree shop: rarity tiers with weighted drop chances
TREE_TYPES = [
    {"name": "Oak",       "emoji": "🌳", "rarity": "Common",    "weight": 50, "color": "#4caf50"},
    {"name": "Pine",      "emoji": "🌲", "rarity": "Common",    "weight": 30, "color": "#2e7d32"},
    {"name": "Palm",      "emoji": "🌴", "rarity": "Uncommon",  "weight": 12, "color": "#8bc34a"},
    {"name": "Cherry",    "emoji": "🌸", "rarity": "Rare",      "weight": 5,  "color": "#e91e63"},
    {"name": "Maple",     "emoji": "🍁", "rarity": "Epic",      "weight": 2,  "color": "#ff5722"},
    {"name": "Golden",    "emoji": "🌟", "rarity": "Legendary", "weight": 1,  "color": "#ffc107"},
    {"name": "Birch",     "emoji": "🌿", "rarity": "Common",    "weight": 20, "color": "#a5d6a7"},
    {"name": "Willow",    "emoji": "🎋", "rarity": "Uncommon",  "weight": 10, "color": "#66bb6a"},
    {"name": "Baobab",    "emoji": "🌵", "rarity": "Rare",      "weight": 4,  "color": "#26a69a"},
    {"name": "Sakura",    "emoji": "🌺", "rarity": "Epic",      "weight": 2,  "color": "#ec407a"},
    {"name": "Rainbow",   "emoji": "🌈", "rarity": "Legendary", "weight": 1,  "color": "#7e57c2"},
]

ROLL_COST = 10
WATER_COST = 5

# Five growth stages: 0 = seed, 4 = fully grown
GROWTH_LABELS = ["Seed", "Sprout", "Sapling", "Young Tree", "Fully Grown"]
MAX_STAGE = len(GROWTH_LABELS) - 1

# Per-tree growth emoji sequences (5 stages each) so every species grows differently.
# Every stage of every tree uses a unique emoji (no recycling between trees or stages).
GROWTH_STAGES_BY_TREE = {
    "Oak":     ["🌰", "🌱", "🌿", "🌳", "🌳"],
    "Pine":    ["🟤", "🌾", "☘️", "🌲", "🎄"],
    "Palm":    ["🥥", "🍀", "🪴", "🌴", "🏝️"],
    "Cherry":  ["🍒", "🌾", "🌿", "🌸", "💮"],
    "Maple":   ["🍂", "🌱", "☘️", "🍁", "🏵️"],
    "Golden":  ["🪙", "🌾", "🪴", "🌟", "👑"],
    "Birch":   ["🌰", "🌱", "🌿", "🌿", "🌳"],
    "Willow":  ["🟢", "🌱", "☘️", "🎋", "🍃"],
    "Baobab":  ["🟤", "🌵", "🪴", "🌵", "🏜️"],
    "Sakura":  ["🩷", "🌾", "🌿", "🌺", "🌷"],
    "Rainbow": ["🟣", "🌱", "🪴", "🌈", "🦄"],
}

# Per-tree animation style: (css animation name, duration)
TREE_ANIMATIONS = {
    "Oak":     ("sway",      3.0),
    "Pine":    ("sway",      4.0),
    "Palm":    ("palm-sway", 2.5),
    "Cherry":  ("bloom",     2.0),
    "Maple":   ("sway",      3.5),
    "Golden":  ("gold-glow", 1.8),
    "Birch":   ("sway",      2.8),
    "Willow":  ("willow",    3.2),
    "Baobab":  ("sway",      4.5),
    "Sakura":  ("bloom",     2.2),
    "Rainbow": ("rainbow-spin", 2.0),
}

def growth_emoji(tree_name, stage):
    """Return the emoji for a tree at a given growth stage."""
    stages = GROWTH_STAGES_BY_TREE.get(tree_name, ["🌰", "🌱", "🌿", "🌳", "🌲"])
    return stages[min(stage, len(stages) - 1)]

# Per-tree environment: (sky gradient, ground color, ground accent)
TREE_ENVIRONMENTS = {
    "Oak":     ("linear-gradient(#87ceeb, #c8e6c9)", "#6d4c41", "#4caf50"),
    "Pine":    ("linear-gradient(#b3e5fc, #e1f5fe)", "#5d4037", "#2e7d32"),
    "Palm":    ("linear-gradient(#ffe082, #fff9c4)", "#f9a825", "#8bc34a"),
    "Cherry":  ("linear-gradient(#f8bbd0, #fce4ec)", "#6d4c41", "#e91e63"),
    "Maple":   ("linear-gradient(#ffcc80, #ffe0b2)", "#5d4037", "#ff5722"),
    "Golden":  ("linear-gradient(#ffd54f, #fff8e1)", "#b8860b", "#ffb300"),
    "Birch":   ("linear-gradient(#e3f2fd, #f1f8e9)", "#8d6e63", "#a5d6a7"),
    "Willow":  ("linear-gradient(#b2dfdb, #e0f2f1)", "#4e342e", "#66bb6a"),
    "Baobab":  ("linear-gradient(#ffcc80, #ffe0b2)", "#d7a86e", "#26a69a"),
    "Sakura":  ("linear-gradient(#f48fb1, #fce4ec)", "#6d4c41", "#ec407a"),
    "Rainbow": ("linear-gradient(135deg, #ff9a9e, #fbc2eb, #a6c1ee, #a1ffce, #faffd1)", "#6a1b9a", "#ab47bc"),
}

def tree_environment(tree_name):
    """Return (sky, ground, accent) colors for a tree's plot."""
    return TREE_ENVIRONMENTS.get(
        tree_name, ("linear-gradient(#87ceeb, #e0f7fa)", "#6d4c41", "#4caf50")
    )

RARITY_COLORS = {
    "Common":    "#9e9e9e",
    "Uncommon":  "#4caf50",
    "Rare":      "#2196f3",
    "Epic":      "#9c27b0",
    "Legendary": "#ff9800",
}

def roll_tree():
    """Pick a random tree using weighted probabilities."""
    weights = [t["weight"] for t in TREE_TYPES]
    return random.choices(TREE_TYPES, weights=weights, k=1)[0]

# Function to create a task list with check boxes and editable task names
def create_task_list(tasks):
    for i, task in enumerate(tasks):
        new_task = st.text_input(f"Task {i+1}", value=task, key=f"task_{i}")
        st.checkbox(f"Completed {i+1}", key=f"completed_{i}")
        if new_task != task:
            tasks[i] = new_task

# Clock skins: (label, face fill, rim stroke, rim width, tick color, minute hand color, second hand color)
CLOCK_SKINS = {
    "Classic": {
        "face": "#fafafa", "rim": "#333", "rim_width": 4,
        "tick_major": "#333", "tick_minor": "#999",
        "minute": "#1976d2", "second": "#d32f2f",
        "center": "#333", "text": "#333",
    },
    "Tomato": {
        "face": "#e53935", "rim": "#b71c1c", "rim_width": 6,
        "tick_major": "#ffffff", "tick_minor": "#ffcdd2",
        "minute": "#ffffff", "second": "#ffeb3b",
        "center": "#4caf50", "text": "#b71c1c",
    },
    "Antique": {
        "face": "#f5e6c8", "rim": "#8d6e63", "rim_width": 8,
        "tick_major": "#5d4037", "tick_minor": "#a1887f",
        "minute": "#3e2723", "second": "#bf360c",
        "center": "#5d4037", "text": "#5d4037",
    },
}

# Function to render the Pomodoro timer as an analog clock
def render_timer(remaining, total):
    remaining = max(remaining, 0)
    minutes, seconds = divmod(remaining, 60)
    skin = CLOCK_SKINS.get(st.session_state.get("clock_skin", "Classic"), CLOCK_SKINS["Classic"])

    # Angles (degrees, 0 = 12 o'clock, clockwise)
    # Use elapsed time so both hands move clockwise as time passes.
    total = max(total, 1)
    elapsed = total - remaining
    # Second hand: one full revolution per minute
    second_angle = (elapsed % 60) * 6
    # Minute hand: sweeps the full face over the Pomodoro session.
    minute_angle = (elapsed / total) * 360

    # Build tick marks around the face
    ticks = ""
    for i in range(60):
        angle = i * 6
        if i % 5 == 0:
            inner, width, color = 78, 3, skin["tick_major"]
        else:
            inner, width, color = 84, 1, skin["tick_minor"]
        ticks += (
            f"<line x1='100' y1='20' x2='100' y2='{inner}' "
            f"stroke='{color}' stroke-width='{width}' "
            f"transform='rotate({angle} 100 100)' />"
        )

    if remaining > 0:
        st.markdown(
            f"""
            <style>
            @keyframes pulse {{
                0%   {{ transform: scale(1);    color: #d32f2f; }}
                50%  {{ transform: scale(1.15); color: #ff5252; }}
                100% {{ transform: scale(1);    color: #d32f2f; }}
            }}
            .clock-wrap {{
                display: flex;
                flex-direction: column;
                align-items: center;
            }}
            .clock-hand {{
                transition: transform 0.9s linear;
                transform-box: view-box;
                transform-origin: 100px 100px;
            }}
            .clock-time {{
                font-size: 28px;
                font-weight: bold;
                margin-top: 8px;
                font-family: monospace;
                color: {skin['text']};
            }}
            </style>
            <div class="clock-wrap">
              <svg width="220" height="220" viewBox="0 0 200 200">
                <circle cx="100" cy="100" r="95" fill="{skin['face']}" stroke="{skin['rim']}" stroke-width="{skin['rim_width']}" />
                {ticks}
                <!-- Minute hand -->
                <line class="clock-hand" x1="100" y1="100" x2="100" y2="40"
                      stroke="{skin['minute']}" stroke-width="5" stroke-linecap="round"
                      style="transform: rotate({minute_angle}deg);" />
                <!-- Second hand -->
                <line class="clock-hand" x1="100" y1="110" x2="100" y2="25"
                      stroke="{skin['second']}" stroke-width="2" stroke-linecap="round"
                      style="transform: rotate({second_angle}deg);" />
                <circle cx="100" cy="100" r="5" fill="{skin['center']}" />
              </svg>
              <div class="clock-time">{minutes:02d}:{seconds:02d}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <style>
            @keyframes pulse {
                0%   { transform: scale(1);    color: #d32f2f; }
                50%  { transform: scale(1.15); color: #ff5252; }
                100% { transform: scale(1);    color: #d32f2f; }
            }
            .times-up {
                font-size: 48px;
                font-weight: bold;
                text-align: center;
                animation: pulse 1s ease-in-out infinite;
            }
            </style>
            <h1 class="times-up">Time's up!</h1>
            """,
            unsafe_allow_html=True,
        )


# Home page: task list + Pomodoro timer
def home_page():
    st.title("Task List with Pomodoro Timer")

    # Inject custom CSS to change the background color to white
    st.markdown(
        """
        <style>
        .stApp {
            background-color: white;
        }

        /* Animate checkboxes when checked */
        @keyframes check-pop {
            0%   { transform: scale(1); }
            40%  { transform: scale(1.4); }
            70%  { transform: scale(0.9); }
            100% { transform: scale(1); }
        }
        @keyframes label-flash {
            0%   { background-color: rgba(76, 175, 80, 0.0); }
            50%  { background-color: rgba(76, 175, 80, 0.25); }
            100% { background-color: rgba(76, 175, 80, 0.0); }
        }
        div[data-testid="stCheckbox"] input[type="checkbox"]:checked {
            animation: check-pop 0.4s ease-in-out;
        }
        div[data-testid="stCheckbox"] label:has(input[type="checkbox"]:checked) {
            animation: label-flash 0.8s ease-in-out;
            border-radius: 6px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Task list (persisted across reruns)
    if "tasks" not in st.session_state:
        st.session_state.tasks = saved.get("tasks", ["Task 1", "Task 2", "Task 3", "Task 4"])
    create_task_list(st.session_state.tasks)

    # Add task button
    if st.button("Add Task"):
        st.session_state.tasks.append("New Task")
        save_game()
        st.rerun()

    # Pomodoro timer
    st.write("Pomodoro Timer (25 minutes)")
    if "duration" not in st.session_state:
        st.session_state.duration = 25 * 60
    if "remaining" not in st.session_state:
        st.session_state.remaining = st.session_state.duration
    if "running" not in st.session_state:
        st.session_state.running = False

    render_timer(st.session_state.remaining, st.session_state.duration)

    # Skins button: cycles through the available clock skins
    skin_names = list(CLOCK_SKINS.keys())
    current_skin = st.session_state.get("clock_skin", "Classic")
    if st.button(f"🎨 Skins (current: {current_skin})"):
        idx = skin_names.index(current_skin) if current_skin in skin_names else 0
        st.session_state.clock_skin = skin_names[(idx + 1) % len(skin_names)]
        save_game()
        st.rerun()

    if st.button("Start Pomodoro"):
        st.session_state.remaining = st.session_state.duration
        st.session_state.running = True

    if st.button("Stop Pomodoro"):
        st.session_state.running = False

    # Timer controls (only available when the timer is stopped)
    if not st.session_state.running:
        st.write("Timer Controls")
        if st.button("Add 1 minute"):
            st.session_state.duration += 60
        if st.button("Subtract 1 minute"):
            st.session_state.duration = max(0, st.session_state.duration - 60)
        st.write(f"Current Duration: {st.session_state.duration // 60} minutes")

    # Non-blocking countdown: tick once per rerun while running
    if st.session_state.running and st.session_state.remaining > 0:
        time.sleep(1)
        st.session_state.remaining -= 1
        if st.session_state.remaining <= 0:
            st.session_state.running = False
            st.session_state.xp += 10
            st.session_state.xp_gained = True
            save_game()
        st.rerun()

    if st.session_state.get("xp_gained"):
        st.success("🎉 Pomodoro complete! You earned 10 XP.")
        st.session_state.xp_gained = False
        st.session_state.xp_animate = True

    # Auto-save task edits so progress survives restarts and tab closes
    save_game()

# Garden page
def garden_page():
    st.title("Garden")
    st.write("Your garden is growing. Keep finishing Pomodoros to earn XP!")

    if "garden" not in st.session_state:
        st.session_state.garden = []

    st.subheader("🌱 Tree Shop")
    st.write(f"Each roll costs **{ROLL_COST} XP**. You have **{st.session_state.xp} XP**.")

    # Show drop rates
    with st.expander("Drop rates"):
        total_weight = sum(t["weight"] for t in TREE_TYPES)
        for t in TREE_TYPES:
            pct = t["weight"] / total_weight * 100
            st.write(f"{t['emoji']} **{t['name']}** ({t['rarity']}) — {pct:.1f}%")

    if st.button(f"🎲 Roll for a tree ({ROLL_COST} XP)"):
        if st.session_state.xp < ROLL_COST:
            st.error("Not enough XP! Finish a Pomodoro to earn more.")
        else:
            st.session_state.xp -= ROLL_COST
            tree = roll_tree()
            # If you already own this tree, discard the new duplicate and refund 5 XP
            existing = next(
                (p for p in st.session_state.garden if p["name"] == tree["name"]),
                None,
            )
            if existing:
                st.session_state.xp += 5
                st.session_state.last_roll = tree
                st.session_state.duplicate_removed = tree["name"]
            else:
                # Each tree is its own instance starting as a seed (stage 0)
                st.session_state.garden.append({"name": tree["name"], "stage": 0})
                st.session_state.last_roll = tree
                st.session_state.duplicate_removed = None
            save_game()
            st.rerun()

    # Notify if a duplicate was rolled
    if st.session_state.get("duplicate_removed"):
        st.warning(
            f"You already had a {st.session_state.duplicate_removed} — "
            "the duplicate was discarded and you got 5 XP back."
        )
        st.session_state.duplicate_removed = None

    # Show the result of the last roll with a pop animation
    last = st.session_state.get("last_roll")
    if last:
        color = RARITY_COLORS.get(last["rarity"], "#333")
        st.markdown(
            f"""
            <style>
            @keyframes roll-pop {{
                0%   {{ transform: scale(0.3); opacity: 0; }}
                60%  {{ transform: scale(1.2); opacity: 1; }}
                100% {{ transform: scale(1);   opacity: 1; }}
            }}
            .roll-result {{
                text-align: center;
                padding: 16px;
                border-radius: 12px;
                border: 3px solid {color};
                animation: roll-pop 0.6s ease-out;
                margin: 12px 0;
            }}
            .roll-emoji {{ font-size: 64px; }}
            .roll-name  {{ font-size: 24px; font-weight: bold; color: {color}; }}
            .roll-rarity {{ font-size: 16px; color: {color}; }}
            </style>
            <div class="roll-result">
                <div class="roll-emoji">{last['emoji']}</div>
                <div class="roll-name">{last['name']}</div>
                <div class="roll-rarity">{last['rarity']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Show the collection
    st.subheader("🌳 Your Trees")
    if not st.session_state.garden:
        st.info("You don't have any trees yet. Roll the shop to grow your garden! 🌱")
    else:
        st.write(f"Water a tree for **{WATER_COST} XP** to help it grow (5 stages).")

        # Bulk watering for every tree that can still grow
        growable = [i for i, p in enumerate(st.session_state.garden) if p["stage"] < MAX_STAGE]
        if growable:
            total_cost = len(growable) * WATER_COST
            if st.button(f"💧 Water all growable trees ({total_cost} XP)"):
                if st.session_state.xp < total_cost:
                    st.error("Not enough XP to water all trees!")
                else:
                    st.session_state.xp -= total_cost
                    for idx in growable:
                        st.session_state.garden[idx]["stage"] += 1
                    save_game()
                    st.rerun()

        cols = st.columns(3)
        for i, plant in enumerate(st.session_state.garden):
            tree = next((t for t in TREE_TYPES if t["name"] == plant["name"]), None)
            if not tree:
                continue
            color = RARITY_COLORS.get(tree["rarity"], "#333")
            stage = plant["stage"]
            stage_emoji = growth_emoji(tree["name"], stage)
            stage_label = GROWTH_LABELS[stage]
            anim_name, anim_dur = TREE_ANIMATIONS.get(tree["name"], ("sway", 3.0))
            sky, ground, accent = tree_environment(tree["name"])
            # Scale the tree up as it grows for a more realistic feel
            scale = 1.0 + stage * 0.35
            base_size = 72
            emoji_size = int(base_size * scale)
            # Shadow grows and softens as the tree matures
            shadow_blur = 4 + stage * 3
            shadow_spread = 2 + stage * 2
            with cols[i % 3]:
                st.markdown(
                    f"""
                    <style>
                    @keyframes sway {{
                        0%   {{ transform: rotate(-2deg) translateY(0); }}
                        25%  {{ transform: rotate(1deg)  translateY(-2px); }}
                        50%  {{ transform: rotate(3deg)  translateY(0); }}
                        75%  {{ transform: rotate(1deg)  translateY(-1px); }}
                        100% {{ transform: rotate(-2deg) translateY(0); }}
                    }}
                    @keyframes palm-sway {{
                        0%   {{ transform: rotate(-5deg) skewX(-2deg) translateY(0); }}
                        50%  {{ transform: rotate(5deg)  skewX(2deg)  translateY(-3px); }}
                        100% {{ transform: rotate(-5deg) skewX(-2deg) translateY(0); }}
                    }}
                    @keyframes willow {{
                        0%   {{ transform: rotate(-3deg) translateY(0); }}
                        50%  {{ transform: rotate(3deg)  translateY(3px); }}
                        100% {{ transform: rotate(-3deg) translateY(0); }}
                    }}
                    @keyframes oak-sway {{
                        0%   {{ transform: rotate(-1.5deg) translateY(0); }}
                        50%  {{ transform: rotate(1.5deg)  translateY(-1px); }}
                        100% {{ transform: rotate(-1.5deg) translateY(0); }}
                    }}
                    @keyframes birch-sway {{
                        0%   {{ transform: rotate(-4deg) skewX(-1deg) translateY(0); }}
                        50%  {{ transform: rotate(4deg)  skewX(1deg)  translateY(-2px); }}
                        100% {{ transform: rotate(-4deg) skewX(-1deg) translateY(0); }}
                    }}
                    @keyframes bloom {{
                        0%   {{ transform: scale(1)    rotate(-1deg); }}
                        50%  {{ transform: scale(1.08) rotate(1deg); }}
                        100% {{ transform: scale(1)    rotate(-1deg); }}
                    }}
                    @keyframes shimmer {{
                        0%   {{ filter: brightness(1)   drop-shadow(0 0 2px gold); transform: scale(1)    rotate(-1deg); }}
                        50%  {{ filter: brightness(1.6) drop-shadow(0 0 10px gold); transform: scale(1.1) rotate(1deg); }}
                        100% {{ filter: brightness(1)   drop-shadow(0 0 2px gold); transform: scale(1)    rotate(-1deg); }}
                    }}
                    @keyframes gold-glow {{
                        0%   {{ filter: brightness(1)   drop-shadow(0 0 4px #ffd700); transform: scale(1)    rotate(-2deg); }}
                        50%  {{ filter: brightness(1.8) drop-shadow(0 0 16px #ffb300); transform: scale(1.12) rotate(2deg); }}
                        100% {{ filter: brightness(1)   drop-shadow(0 0 4px #ffd700); transform: scale(1)    rotate(-2deg); }}
                    }}
                    @keyframes rainbow-spin {{
                        0%   {{ filter: hue-rotate(0deg)   drop-shadow(0 0 6px #ff9a9e); transform: scale(1)    rotate(-3deg); }}
                        50%  {{ filter: hue-rotate(180deg) drop-shadow(0 0 14px #a6c1ee); transform: scale(1.1) rotate(3deg); }}
                        100% {{ filter: hue-rotate(360deg) drop-shadow(0 0 6px #ff9a9e); transform: scale(1)    rotate(-3deg); }}
                    }}
                    .tree-emoji {{
                        display: inline-block;
                        font-size: {emoji_size}px;
                        line-height: 1;
                        transform-origin: bottom center;
                        animation: {anim_name} {anim_dur}s ease-in-out infinite;
                        filter: drop-shadow(0 {shadow_spread}px {shadow_blur}px rgba(0,0,0,0.25));
                    }}
                    </style>
                    <div style="
                        text-align: center;
                        border-radius: 10px;
                        border: 2px solid {color};
                        margin-bottom: 8px;
                        overflow: hidden;
                    ">
                        <!-- Each tree gets its own plot: sky + ground -->
                        <div style="
                            position: relative;
                            height: 220px;
                            background: {sky};
                            display: flex;
                            flex-direction: column;
                            justify-content: flex-end;
                        ">
                            <div style="
                                flex-grow: 1;
                                display: flex;
                                align-items: flex-end;
                                justify-content: center;
                                padding-bottom: 4px;
                            ">
                                <span class="tree-emoji">{stage_emoji}</span>
                            </div>
                            <!-- Ground strip -->
                            <div style="
                                height: 40px;
                                background: {ground};
                                border-top: 3px solid {accent};
                                box-shadow: inset 0 6px 8px rgba(0,0,0,0.15);
                            "></div>
                        </div>
                        <div style="padding: 8px; background: white;">
                            <div style="font-weight: bold; color: {color};">{tree['name']}</div>
                            <div style="font-size: 12px; color: {color};">{tree['rarity']}</div>
                            <div style="font-size: 14px;">{stage_label} ({stage + 1}/5)</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if stage < MAX_STAGE:
                    if st.button(f"💧 Water ({WATER_COST} XP)", key=f"water_{i}"):
                        if st.session_state.xp < WATER_COST:
                            st.error("Not enough XP!")
                        else:
                            st.session_state.xp -= WATER_COST
                            st.session_state.garden[i]["stage"] += 1
                            save_game()
                            st.rerun()
                else:
                    st.success("Fully grown! 🌟")

                # Delete button opens a confirmation warning
                if st.button("🗑️ Delete", key=f"delete_{i}"):
                    st.session_state.pending_delete = i
                    st.rerun()

    # Confirmation warning for deleting a tree
    pending = st.session_state.get("pending_delete")
    if pending is not None and 0 <= pending < len(st.session_state.garden):
        plant = st.session_state.garden[pending]
        st.warning(
            f"⚠️ Are you sure you want to delete your **{plant['name']}** "
            f"({GROWTH_LABELS[plant['stage']]})? This cannot be undone."
        )
        confirm_col, cancel_col, _ = st.columns([1, 1, 4])
        with confirm_col:
            if st.button("Yes, delete it", type="primary"):
                st.session_state.garden.pop(pending)
                st.session_state.pending_delete = None
                save_game()
                st.rerun()
        with cancel_col:
            if st.button("Cancel"):
                st.session_state.pending_delete = None
                st.rerun()

# Main app
def main():
    st.set_page_config(page_title="Pomodoro Garden", page_icon="🌳", layout="centered")

    saved = load_save()

    if "page" not in st.session_state:
        st.session_state.page = "Home"
    if "xp" not in st.session_state:
        st.session_state.xp = saved.get("xp", 0)
    if "xp_gained" not in st.session_state:
        st.session_state.xp_gained = False
    if "xp_animate" not in st.session_state:
        st.session_state.xp_animate = False
    if "garden" not in st.session_state:
        st.session_state.garden = saved.get("garden", [])
    if "last_roll" not in st.session_state:
        st.session_state.last_roll = None
    if "duplicate_removed" not in st.session_state:
        st.session_state.duplicate_removed = None
    if "clock_skin" not in st.session_state:
        st.session_state.clock_skin = saved.get("clock_skin", "Classic")
    if "pending_delete" not in st.session_state:
        st.session_state.pending_delete = None

    # XP display at the top of the screen
    animate_class = "xp-bump" if st.session_state.xp_animate else ""
    st.markdown(
        f"""
        <style>
        @keyframes xp-bump {{
            0%   {{ transform: scale(1);    background-color: #1976d2; }}
            30%  {{ transform: scale(1.25); background-color: #43a047; }}
            60%  {{ transform: scale(0.95); background-color: #43a047; }}
            100% {{ transform: scale(1);    background-color: #1976d2; }}
        }}
        @keyframes xp-float {{
            0%   {{ opacity: 1; transform: translateY(0); }}
            100% {{ opacity: 0; transform: translateY(-40px); }}
        }}
        .xp-badge {{
            position: sticky;
            top: 0;
            z-index: 1000;
            background-color: #1976d2;
            color: white;
            padding: 8px 16px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 18px;
            text-align: right;
            margin-bottom: 8px;
            display: inline-block;
            width: 100%;
            box-sizing: border-box;
        }}
        .xp-bump {{
            animation: xp-bump 0.8s ease-in-out;
        }}
        .xp-float {{
            position: fixed;
            top: 60px;
            right: 24px;
            z-index: 1001;
            color: #43a047;
            font-weight: bold;
            font-size: 22px;
            animation: xp-float 1.2s ease-out forwards;
            pointer-events: none;
        }}
        </style>
        <div class="xp-badge {animate_class}">⭐ XP: {st.session_state.xp}</div>
        {"<div class='xp-float'>+10 XP</div>" if st.session_state.xp_animate else ""}
        """,
        unsafe_allow_html=True,
    )
    st.session_state.xp_animate = False

    # Level progress bar (100 XP per level)
    level = st.session_state.xp // 100
    progress = (st.session_state.xp % 100) / 100
    st.progress(progress, text=f"Level {level} — {st.session_state.xp % 100}/100 XP to next level")

    # Sidebar: quick stats and save management
    with st.sidebar:
        st.header("📊 Stats")
        st.metric("Total XP", st.session_state.xp)
        st.metric("Trees owned", len(st.session_state.garden))
        grown = sum(1 for p in st.session_state.garden if p["stage"] >= MAX_STAGE)
        st.metric("Fully grown", grown)
        st.divider()
        if st.button("🗑️ Reset save", use_container_width=True):
            st.session_state.xp = 0
            st.session_state.garden = []
            st.session_state.last_roll = None
            save_game()
            st.rerun()

    # Top navigation bar
    nav_home, nav_garden, _ = st.columns([1, 1, 6])
    with nav_home:
        if st.button("Home", use_container_width=True):
            st.session_state.page = "Home"
    with nav_garden:
        if st.button("Garden", use_container_width=True):
            st.session_state.page = "Garden"

    st.divider()

    if st.session_state.page == "Garden":
        garden_page()
    else:
        home_page()

if __name__ == "__main__":
    main()
