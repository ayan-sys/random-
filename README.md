# ☕ Star Barista Chatbot

An intelligent, personality-driven customer service chatbot for Starbucks, built with Python and Streamlit.

## Features
-   **Smart AI Barista**: Uses fuzzy matching to understand natural language orders (e.g., "I want a latte" or even "latte please").
-   **Persistent Memory**: Uses SQLite to remember your name, star balance, and order history across sessions.
-   **Star Rewards System**: Earn 2 stars for every $1 spent.
-   **Context-Aware**: Greets you based on the time of day (Morning/Afternoon/Evening).
-   **Recommendation Engine**: Suggests drinks based on your history or random "Barista's Choice".

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/YOUR_USERNAME/star-barista.git
    cd star-barista
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  Run the app:
    ```bash
    streamlit run app.py
    ```

## Usage
-   Type **"Menu"** to see options.
-   Type **"Surprise me"** for a recommendation.
-   Type **"My stats"** to see your rewards.
-   Just chat! "Any food?", "What time are you open?", "I need caffeine".

## Data
-   User data is stored locally in `starbucks.db`.
