import streamlit as st
import random
import datetime
import difflib
import database

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

# --- ADVANCED LOGIC ---
KEYWORDS = {
    "coffee": ["caffe americano", "iced coffee", "nitro cold brew"],
    "latte": ["pumpkin spice latte", "iced chai latte"],
    "tea": ["iced matcha lemonade", "iced chai latte"],
    "food": ["butter croissant", "blueberry muffin", "cake pop"],
    "sandwich": ["bacon & gouda sandwich", "impossible breakfast sandwich"]
}

SMALL_TALK = {
    "how are you": "I'm just a few lines of code, but I'm feeling brew-tiful! ☕ How are you?",
    "thank you": "You're welcome! It's my pleasure to serve. ✨",
    "thanks": "No problem! Let me know if you need anything else.",
    "hello": "Hi there! 👋 Ready for some coffee?",
    "hi": "Hello! What can I get for you today?"
}

def analyze_intent(text):
    text = text.lower()
    
    # 1. Direct Commands
    if "menu" in text: return "menu"
    if "cart" in text or "order" in text and "show" in text: return "show_cart"
    if "checkout" in text or "pay" in text: return "checkout"
    if "points" in text or "stars" in text: return "points"
    if "surprise" in text or "recommend" in text: return "recommend"
    
    # 2. Small Talk
    for key in SMALL_TALK:
        if key in text:
            return f"small_talk:{SMALL_TALK[key]}"
            
    # 3. FAQ
    for key in FAQS:
        if key in text:
            return f"faq:{FAQS[key]}"
            
    # 4. Item Search (Keyword + Fuzzy)
    # Check manual keywords first
    for keyword, items in KEYWORDS.items():
        if keyword in text:
            return f"suggest:{items[0]}" # Suggest the first match
            
    # Fuzzy match strict items
    match = find_item_fuzzy(text)
    if match:
        return f"add:{match['name']}"
        
    # Deep search (word by word)
    words = text.split()
    for word in words:
        if len(word) > 3:
            match = find_item_fuzzy(word)
            if match:
                return f"add:{match['name']}"
                
    return "unknown"

# --- MAIN CHAT LOGIC ---
st.title("☕ Star Barista AI")
st.caption("Now with specific Cart & Point commands!")

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
if prompt := st.chat_input("Type here..."):
    add_to_chat("user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    response = ""
    stage = st.session_state.current_stage
    
    # --- STAGE: GET NAME ---
    if stage == "get_name":
        st.session_state.user_name = prompt
        user = database.get_user(prompt)
        last_order = database.get_last_order(prompt)
        
        if user:
            st.session_state.stars = user[1]
            response = f"Welcome back, **{prompt}**! 👋 You have **{user[1]} Stars**. ✨\n\n"
            if last_order:
                last_item_name = last_order[0]['item']
                response += f"Want to order your usual **{last_item_name}** again?"
            else:
                 response += "What are you in the mood for today?"
        else:
            database.create_user(prompt)
            st.session_state.stars = 0
            response = f"Nice to meet you, {prompt}! I've signed you up for Star Rewards. You have 0 stars.\n\nWhat can I get started for you? (Menu, Hot, Iced, Food)"
        
        st.session_state.current_stage = "menu"
        
    # --- STAGE: ACTIVE CHAT ---
    else:
        intent = analyze_intent(prompt)
        
        if intent == "menu":
            response = "### 📜 The Menu\n\n"
            for cat, items in MENU.items():
                response += f"**{cat}**\n" + "\n".join([f"- {k} (${v})" for k, v in items.items()]) + "\n\n"
            response += "Just type the name of a drink (e.g., 'Latte') to add it!"
            
        elif intent == "show_cart":
            if st.session_state.cart:
                cart_text = "\n".join([f"- {item['item']} (${item['price']:.2f})" for item in st.session_state.cart])
                response = f"### 🛒 Your Cart\n{cart_text}\n\n**Total: ${calculate_total():.2f}**\nType `Checkout` to pay."
            else:
                response = "Your cart is empty! 🛒"
                
        elif intent == "points":
            response = f"🌟 You have **{st.session_state.stars} Stars**.\nEarn 2 stars per $1 spent!"
            
        elif intent == "checkout":
            if not st.session_state.cart:
                response = "Your cart is empty! Add something first. ☕"
            else:
                total = calculate_total()
                stars_earned = int(total * 2)
                database.add_order(st.session_state.user_name, st.session_state.cart, total)
                database.update_stars(st.session_state.user_name, stars_earned)
                st.session_state.stars += stars_earned
                response = f"Processing payment... Success! 🎉\n\nYou've earned **{stars_earned} Stars**! Current Balance: **{st.session_state.stars}**.\n\nCheck your *Order History* next time you visit!"
                st.session_state.cart = []
        
        elif intent == "recommend":
            rec = random.choice(list(ALL_ITEMS.values()))
            response = f"✨ User-Choice-O-Matic recommends: **{rec['name']}** (${rec['price']}). Shall I add it?"
            
        elif intent.startswith("small_talk:"):
            response = intent.split(":", 1)[1]
            
        elif intent.startswith("faq:"):
            response = f"ℹ️ {intent.split(':', 1)[1]}"
            
        elif intent.startswith("suggest:"):
            suggestion = intent.split(":", 1)[1]
            response = f"Did you mean **{suggestion}**? I can add that for you!"
            
        elif intent.startswith("add:"):
            item_name = intent.split(":", 1)[1]
            price = ALL_ITEMS[item_name.lower()]['price']
            st.session_state.cart.append({"item": item_name, "price": price})
            response = f"Got it! Added **{item_name}** to your cart. 🛒\n\nTotal: ${calculate_total():.2f}. Anything else?"
            
        else:
            response = "I'm not sure what you mean. 🤔 Try checking the `Menu`, asking for `Points`, or tell me to `Show Cart`."

    with st.chat_message("assistant"):
        st.markdown(response)
    add_to_chat("assistant", response)
    st.rerun()

