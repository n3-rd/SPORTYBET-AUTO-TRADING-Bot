"""
SPORTYBET AUTO-TRADING BOT - Main Entry Point

Usage:
  python3 main.py               # Runs everything with defaults
  python3 main.py --interactive # Interactive configuration for all options
  python3 main.py --place-bet   # Skips scrapers, only runs the bot
  python3 main.py --amount 500  # Set stake amount (default: 100)
  python3 main.py --total-slips 3 # Stop after 3 successful bets
  python3 main.py --percentage-threshold 60 # Only bet on 60%+ confidence
"""

import sys
import os
import argparse

# Add src to path so we can import from it
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def run_all():
    print("🌟 Initializing Full Automation (Scrapers + Bot)...")
    import run_all
    run_all.main()

def run_desktop_bot():
    print("🚀 Starting SportyBet Desktop Bot...")
    import SportyBet_Bot
    import asyncio
    asyncio.run(SportyBet_Bot.main())

def run_phone_bot():
    print("📱 Starting SportyBet Phone/Mobile Bot...")
    import SportyBet_Phone
    import asyncio
    asyncio.run(SportyBet_Phone.main())

def get_interactive_args():
    print("\n🎮 SportyBet Bot Interactive Configuration")
    print("------------------------------------------")
    
    # 💰 Amount
    print("\n💰 STAKE AMOUNT")
    print("Explanation: The amount of money (in Naira) to bet on each slip.")
    try:
        amount = input("Enter amount [default 100]: ").strip()
        amount = int(amount) if amount else 100
    except: amount = 100

    # 🖥️ Mode
    print("\n🖥️ BROWSER MODE")
    print("Explanation: 'desktop' uses the standard web layout. 'phone' uses the mobile layout.")
    mode = input("Select mode (desktop/phone) [default desktop]: ").strip().lower()
    if mode not in ['desktop', 'phone']: mode = 'desktop'

    # 🤖 AI Analysis
    print("\n🤖 AI ANALYSIS")
    print("Explanation: Uses Gemini AI to triple-check match predictions before betting.")
    ai_choice = input("Enable AI analysis? (y/n) [default y]: ").strip().lower()
    no_ai = ai_choice == 'n'

    # 📦 Total Slips
    print("\n📦 MAX TOTAL SLIPS")
    print("Explanation: The bot will automatically stop execution after successfully placing this many slips.")
    try:
        total_slips = input("Enter max slips [default 5]: ").strip()
        total_slips = int(total_slips) if total_slips else 5
    except: total_slips = 5

    # 🎯 Percentage Threshold
    print("\n🎯 PERCENTAGE THRESHOLD")
    print("Explanation: Only consider matches where prediction confidence is above this % threshold.")
    try:
        threshold = input("Enter % threshold [default 50]: ").strip()
        threshold = int(threshold) if threshold else 50
    except: threshold = 50

    # 🕵️ Automation Depth
    print("\n🕵️ AUTOMATION DEPTH")
    print("Explanation: 'Full' (Yes) will run all scrapers to get fresh data before betting.")
    print("             'Bot Only' (No) will jump straight to SportyBet using existing data.")
    auto_choice = (input("Run full automation? (y/n) [default y]: ").strip().lower() or 'y')
    place_bet = auto_choice == 'n'

    return amount, mode, no_ai, total_slips, threshold, place_bet

def main():
    parser = argparse.ArgumentParser(description="SportyBet Auto-Trading Bot Entry Point")
    parser.add_argument('--place-bet', action='store_true', 
                        help="Only run the SportyBet bot (skips scrapers)")
    parser.add_argument('--no-ai', action='store_true',
                        help="Disable Gemini AI analysis during betting")
    parser.add_argument('--mode', type=str, choices=['desktop', 'phone'], default='desktop',
                        help="Target platform: 'desktop' (default) or 'phone'")
    parser.add_argument('--amount', type=int, default=100,
                        help="Stake amount per bet (default: 100)")
    parser.add_argument('--total-slips', type=int, default=5,
                        help="Maximum number of slips to place (default: 5)")
    parser.add_argument('--percentage-threshold', type=int, default=50,
                        help="Minimum prediction percentage (default: 50)")
    parser.add_argument('--interactive', action='store_true',
                        help="Interactive mode to configure all options")
    
    args = parser.parse_args()

    # Handle Interactive Mode
    if args.interactive:
        amount, mode, no_ai, total_slips, threshold, place_bet = get_interactive_args()
        args.amount = amount
        args.mode = mode
        args.no_ai = no_ai
        args.total_slips = total_slips
        args.percentage_threshold = threshold
        args.place_bet = place_bet

    # Pass configuration via environment variables
    if args.no_ai:
        os.environ["NO_AI"] = "true"
        print("🚫 AI analysis disabled.")
    
    os.environ["STAKE_AMOUNT"] = str(args.amount)
    os.environ["MAX_TOTAL_SLIPS"] = str(args.total_slips)
    os.environ["PERCENT_THRESHOLD"] = str(args.percentage_threshold)
    
    print("\n📋 CONFIGURATION SUMMARY:")
    print(f"   💰 Stake Amount: {args.amount} Naira")
    print(f"   🖥️  Bot Mode:     {args.mode.upper()}")
    print(f"   📦 Max Slips:    {args.total_slips}")
    print(f"   🎯 % Threshold:  {args.percentage_threshold}%")
    print(f"   🤖 AI Analysis:  {'OFF 🚫' if args.no_ai else 'ON ✅'}")
    print("----------------------------\n")

    if not args.place_bet:
        # Default behavior: Run ALL (Scrapers + Bot)
        run_all()
    else:
        # User only wants to place bets based on existing data
        if args.mode == 'desktop':
            run_desktop_bot()
        elif args.mode == 'phone':
            run_phone_bot()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Operation stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
