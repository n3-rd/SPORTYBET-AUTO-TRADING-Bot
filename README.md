🏆 SportyBet Automated Value Betting Bot (with Kelly Criterion)

This project automates value betting and bankroll management on SportyBet using Python and Pyppeteer.
It automatically finds profitable bets, calculates the ideal stake using the Kelly Criterion, and places bets directly on the SportyBet website — all hands-free.

⚙️ Key Features

✅ Automatic Login to SportyBet using Pyppeteer

✅ Automatic Game Detection from SportyBet’s website or local data

✅ Value Betting System (identifies profitable opportunities)

✅ Kelly Criterion Bet Sizing (smart bankroll management)

✅ Automatic Bet Placement (enters stake and clicks “Place Bet”)

✅ Multi-Bet Capable — handles 100+ bets daily

✅ Human-like delays to reduce automation detection

✅ Bankroll Tracker (monitors growth over time)

🧠 How It Works (Step-by-Step)

Game Scraping
The bot fetches upcoming matches from SportyBet using Pyppeteer or preloaded data files.

Value Calculation
Each game’s expected value (EV) is calculated:

value = (probability * odds) - 1


Bets are only taken if the value > 0.

Kelly Criterion Calculation
The bot computes the stake to bet using the Kelly formula:

f* = (bp - q) / b


Where:

b = odds - 1

p = win probability

q = 1 - p

f* = fraction of bankroll to bet

Automatic Betting
Using Pyppeteer, the bot:

Logs into SportyBet

Finds the target match

Clicks the betting option

Inputs the stake (calculated using Kelly Criterion)

Clicks “Place Bet”

Bankroll Logging
After each bet, results are recorded in a CSV file or terminal output, showing bankroll performance.

🧮 Kelly Criterion Helper Function
def cal(odd, pba, amt):
    odd = float(odd)
    pba = float(pba)
    odd -= 1  # Subtract 1 to get net odds (b)
    proba = round(pba / 100, 4)  # Convert percentage to decimal
    loss = 1 - proba
    if odd == 0:
        return 0  # Avoid division by zero
    f = round((((odd * proba) - (loss)) / odd) * amt)
    return f

Example:

If the odds = 2.50, your estimated win probability = 55%, and bankroll = ₦1000
Then:

f = (((1.5 * 0.55) - 0.45) / 1.5) * 1000 = ₦100


So the bot automatically places a ₦100 bet.

🧠 Real-Life Explanation (Layman’s Terms)

Imagine you’re betting ₦1000.
The Kelly formula helps you avoid losing too much and maximize long-term growth.
If the bot finds a game that looks slightly profitable (say 60% chance to win at 2.00 odds), it’ll only risk a portion (say ₦200).
This protects your bankroll if you lose and compounds your profits if you win consistently.

📂 Project Structure

```
SPORTYBET-AUTO-TRADING-Bot/
├── main.py              # New entry point – use --mode desktop or phone
├── src/                 # Source code
│   ├── SportyBet_Bot.py # Desktop version of the bot
│   ├── SportyBet_Phone.py# Mobile/Phone version of the bot
│   ├── login.py         # Login automation
│   ├── main_calc.py     # Kelly Criterion and odds calculations
│   └── func.py          # Shared utility functions
├── data/                # CSV data files (Automatically ignored by git)
├── .env                 # API Keys and sensitive config
├── requirements.txt     # Python dependencies
└── README.md            # Documentation
```

🖥️ Run the Bot

You can now run the bot from the root directory using `main.py`:

**1. Full Automation (Scrapers -> Summary -> Bot)**
By default, the bot runs all scrapers before starting the placement module:
```bash
python main.py
```

**2. Placement Only (Skip Scraping)**
If you've already scraped data today and just want to place bets:
```bash
python main.py --place-bet
```

**3. No AI Mode**
To disable the Gemini AI analysis (always say YES to bot suggestions):
```bash
python main.py --no-ai
```

**4. Phone Mode**
To run the phone/mobile bot interface:
```bash
python main.py --mode phone --place-bet
```

🧩 File Explanations

- **main.py**: The main entry point for the project. Use the `--mode` flag to choose between desktop and phone.
- **src/SportyBet_Bot.py**: The primary bot logic for desktop users.
- **src/SportyBet_Phone.py**: Optimized bot logic for mobile/phone interfaces.
- **src/login.py**: Handles logging in to SportyBet.
- **src/main_calc.py**: Contains probability and stake calculation logic.
- **src/func.py**: Shared helper functions for file handling and name matching.

🧰 Requirements

Install dependencies using the included file:

```bash
pip install -r requirements.txt
```

🖥️ Continuous Running (Linux/VPS)

To run the bot in the background:

```bash
nohup python main.py --mode desktop &
```

🧠 Tips and Recommendations

Start testing with small bankrolls (₦1000).

Use await asyncio.sleep() to introduce random delays.

Review logs/results.csv weekly for performance.

Don’t exceed 10% of bankroll on a single bet.

Adjust the probability threshold (e.g., 60% → safer, 55% → more bets).

Can be modified to run on Android (Termux/Pydroid) or VPS.

🧩 Future Improvements

AI-powered match probability predictions

Telegram/Discord notifications for placed bets

Support for more bookmakers

Visual bankroll charts

Advanced error recovery and session handling

👨‍💻 Author

Ezee Kits (Peter)
🎓 Electrical & Electronics Engineer | Python Automation Developer
📺 YouTube: Ezee Kits

📧 Email: ezeekits@gmail.com

💬 Content: Python, Tech, DIY, Engineering, Automation

⚠️ Disclaimer

This bot is for educational and research purposes only.
Use responsibly and at your own risk.
The author is not responsible for financial losses or betting misuse.
