import streamlit as st
import random
import datetime
import difflib
import database
import speech_recognition as sr

# --- CONFIGURATION & DATA ---
st.set_page_config(page_title="Star Barista ☕", page_icon="☕", layout="wide")

# Initialize DB on load
database.init_db()

MENU = {
    "Hot Drinks": {
        "Caffe Americano": 3.50,
        "Cappuccino": 4.50,
        "Pumpkin Spice Latte": 5.25,
        "White Chocolate Mocha": 5.00,
        "Caramel Macchiato": 4.75,
        "Flat White": 4.75
    },
    "Iced Drinks": {
        "Iced Coffee": 3.25,
        "Iced Matcha Lemonade": 4.50,
        "Nitro Cold Brew": 4.75,
        "Pink Drink": 5.00,
        "Iced Chai Latte": 4.50,
        "Dragon Drink": 5.25
    },
    "Food": {
        "Butter Croissant": 2.75,
        "Blueberry Muffin": 2.95,
        "Bacon & Gouda Sandwich": 5.25,
        "Cake Pop": 2.25,
        "Impossible Breakfast Sandwich": 5.75
    }
}

# Flatten menu for searching
ALL_ITEMS = {}
for cat, items in MENU.items():
    for name, price in items.items():
        ALL_ITEMS[name.lower()] = {"name": name, "price": price, "category": cat}

FAQS = {
    "hours": "We are open daily from 6:00 AM to 9:00 PM!",
    "location": "Find us at 123 Coffee Lane, Brewtown, or check the app for the nearest store.",
    "allergens": "We use shared equipment. Please let us know if you have severe allergies.",
    "rewards": "Join Star Rewards to earn stars for free drinks! You earn 2 stars for every $1 spent.",
    "wifi": "Yes! We have free high-speed WiFi for all customers.",
    "job": "We are always looking for great baristas! Apply at starbucks.com/careers."
}

TRIVIA = [
    "Did you know? Espresso actually has less caffeine than a cup of drip coffee!",
    "Starbucks was founded in 1971 at Pike Place Market in Seattle.",
    "There are over 87,000 drink combinations possible at Starbucks!",
    "A 'Venti' means 'twenty' in Italian, referring to the 20oz size.",
    "The Starbucks siren logo serves to call coffee lovers from everywhere."
]

# --- SESSION STATE INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "cart" not in st.session_state:
    st.session_state.cart = []
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "stars" not in st.session_state:
    st.session_state.stars = 0
if "current_stage" not in st.session_state:
    st.session_state.current_stage = "greeting" # greeting, get_name, menu, checkout

# --- HELPER FUNCTIONS ---
def get_time_greeting():
    hour = datetime.datetime.now().hour
    if hour < 12:
        return "Good morning! ☀️ Need a wake-up call?"
    elif hour < 17:
        return "Good afternoon! ☕ Ready for a pick-me-up?"
    else:
        return "Good evening! 🌙 Decaf or a sweet treat tonight?"

def calculate_total():
    return sum(item['price'] for item in st.session_state.cart)

def add_to_chat(role, content):
    st.session_state.messages.append({"role": role, "content": content})

def find_item_fuzzy(query):
    """Find a menu item using fuzzy matching."""
    matches = difflib.get_close_matches(query.lower(), ALL_ITEMS.keys(), n=1, cutoff=0.6)
    if matches:
        return ALL_ITEMS[matches[0]]
    return None

# --- UI LAYOUT ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/d/d3/Starbucks_Corporation_Logo_2011.svg/1200px-Starbucks_Corporation_Logo_2011.svg.png", width=100)
    st.title("Star Rewards ⭐")
    
    if st.session_state.user_name:
        st.write(f"Welcome back, **{st.session_state.user_name}**!")
        st.metric("Stars Balance", st.session_state.stars)
    else:
        st.write("Guest User")
    
    st.divider()
    st.subheader("Your Order 🛒")
    if st.session_state.cart:
        for idx, item in enumerate(st.session_state.cart):
            st.text(f"{item['item']} - ${item['price']:.2f}")
        st.write(f"**Total: ${calculate_total():.2f}**")
        if st.button("Checkout Now", type="primary"):
             st.session_state.current_stage = "checkout"
             add_to_chat("assistant", f"Ready to checkout? Your total is **${calculate_total():.2f}**. Type `Pay` to finish up!")
             st.rerun()
    else:
        st.write("Your cart is empty.")

    st.divider()
    if st.button("Reset Session"):
        st.session_state.clear()
        st.rerun()

# --- MAIN CHAT LOGIC ---
st.title("☕ Star Barista AI")
st.caption("Now with Memory & Smart Matching")

# 1. INITIAL GREETING (Runs once)
if not st.session_state.messages:
    greeting = get_time_greeting()
    add_to_chat("assistant", f"{greeting} I'm Star Barista! What's your name so I can check your Rewards?")
    st.session_state.current_stage = "get_name"

# 2. DISPLAY CHAT HISTORY
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 3. HANDLE USER INPUT
# Create a container for input method selection or just show both
input_container = st.container()

voice_prompt = None
audio_value = st.audio_input("🎤 Record your order")

if audio_value:
    r = sr.Recognizer()
    try:
        with sr.AudioFile(audio_value) as source:
            audio_data = r.record(source)
            voice_prompt = r.recognize_google(audio_data)
            st.toast(f"I heard: '{voice_prompt}'", icon="👂")
    except sr.UnknownValueError:
        st.toast("Could not understand audio", icon="❌")
    except sr.RequestError:
        st.toast("Speech service unavailable", icon="⚠️")

# Priority: Voice > Text
prompt = voice_prompt if voice_prompt else st.chat_input("Type here...")

if prompt:
    add_to_chat("user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    response = ""
    stage = st.session_state.current_stage
    prompt_lower = prompt.lower()

    # --- STAGE: GET NAME + DB CHECK ---
    if stage == "get_name":
        st.session_state.user_name = prompt
        # check DB
        user = database.get_user(prompt)
        last_order = database.get_last_order(prompt)
        
        if user:
            st.session_state.stars = user[1]
            response = f"Welcome back, **{prompt}**! 👋 You have **{user[1]} Stars**. ✨\n\n"
            if last_order:
                # Suggest re-order
                 last_item_name = last_order[0]['item']
                 response += f"Want to order your usual **{last_item_name}** again?"
            else:
                 response += "What are you in the mood for today?"
        else:
            database.create_user(prompt)
            st.session_state.stars = 0
            response = f"Nice to meet you, {prompt}! I've signed you up for Star Rewards. You have 0 stars.\n\nWhat can I get started for you? (Menu, Hot, Iced, Food)"
        
        st.session_state.current_stage = "menu"

    # --- STAGE: LOGIC ROUTER ---
    elif stage == "checkout" or "pay" in prompt_lower or "checkout" in prompt_lower:
        if not st.session_state.cart:
            response = "Your cart is empty! Add something first. ☕"
        else:
            total = calculate_total()
            stars_earned = int(total * 2)
            
            # Save to DB
            database.add_order(st.session_state.user_name, st.session_state.cart, total)
            database.update_stars(st.session_state.user_name, stars_earned)
            
            # Update session
            st.session_state.stars += stars_earned
            
            response = f"Processing payment... Success! 🎉\n\nYou've earned **{stars_earned} Stars**! Current Balance: **{st.session_state.stars}**.\n\nCheck your *Order History* next time you visit!"
            st.session_state.cart = []
            st.session_state.current_stage = "menu"

    elif "menu" in prompt_lower:
        response = "### 📜 The Menu\n\n"
        for cat, items in MENU.items():
            response += f"**{cat}**\n" + "\n".join([f"- {k} (${v})" for k, v in items.items()]) + "\n\n"
        response += "Just type the name of a drink (even nicely like 'I want a latte')!"

    elif "surprise" in prompt_lower or "recommend" in prompt_lower:
        rec = random.choice(list(ALL_ITEMS.values()))
        response = f"✨ My AI taste-buds suggest a **{rec['name']}** (${rec['price']}). Shall I add it?"

    elif "fact" in prompt_lower or "trivia" in prompt_lower:
        response = f"🤓 {random.choice(TRIVIA)}"

    # FAQ MATCHING
    elif any(x in prompt_lower for x in FAQS):
        for key in FAQS:
            if key in prompt_lower:
                response = f"ℹ️ {FAQS[key]}"
                break

    # SMART ORDERING (FUZZY MATCH)
    else:
        # Check against all item names using fuzzy match
        # Split prompt into words if it's a long sentence, or feed whole phrase
        # We try to match content.
        
        # Simple heuristic: try to match the whole prompt or chunks?
        # Let's try matching the whole prompt first against keys
        match = find_item_fuzzy(prompt)
        
        # If no strict match, check if any word in prompt hits a keyword
        if not match:
            words = prompt.split()
            for word in words:
                if len(word) > 3: # skip small words
                    match = find_item_fuzzy(word)
                    if match: break
        
        if match:
            st.session_state.cart.append({"item": match['name'], "price": match['price']})
            response = f"Got it! Added **{match['name']}** to your cart. 🛒\n\nAnything else?"
        else:
            response = "I didn't quite catch that. 🤔 Try checking the `Menu` or asking for `Hours`."

    with st.chat_message("assistant"):
        st.markdown(response)
    add_to_chat("assistant", response)
    st.rerun()
