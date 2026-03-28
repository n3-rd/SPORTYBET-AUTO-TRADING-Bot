import os
import sys
import subprocess
import time
import pandas as pd
from datetime import datetime

def run_script(script_name):
    print(f"\n>>> RUNNING: {script_name} <<<")
    # Script is in the same directory as this runner (src/)
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script_name)
    try:
        # Use sys.executable to ensure we use the same virtual environment's python
        result = subprocess.run([sys.executable, script_path], check=False)
        if result.returncode == 0:
            print(f">>> SUCCESS: {script_name} <<<")
        else:
            print(f">>> WARNING: {script_name} exited with code {result.returncode} <<<")
    except Exception as e:
        print(f">>> ERROR running {script_name}: {e} <<<")

def main():
    # Correct path calculation for project root and data directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_dir = os.path.join(project_root, "data", f"{datetime.now().strftime('%Y-%m-%d')} Files")

    print("======================================================")
    print("      SPORTYBET AUTO-TRADING BOT - FULL AUTOMATION")
    print("======================================================")

    # 1. RUN SCRAPERS
    scrapers = [
        "accumulator.py",
        "betclan.py",
        "footballsupertips.py",
        "forbet.py",
        "prematips.py",
        "statarea.py"
    ]

    for scraper in scrapers:
        scraper_path = os.path.join(script_dir, scraper)
        if os.path.exists(scraper_path):
            run_script(scraper)
        else:
            print(f">>> SKIP: {scraper} (File not found) <<<")

    # 2. DATA SUMMARY
    print("\n" + "="*50)
    print("           SCRAPING SUMMARY")
    print("="*50)
    
    if os.path.exists(data_dir):
        for f in os.listdir(data_dir):
            if f.endswith('.csv'):
                try:
                    count = len(pd.read_csv(os.path.join(data_dir, f)))
                    print(f"✅ {f:20} : {count} matches found")
                except:
                    print(f"❌ {f:20} : Could not read file")
    else:
        print(f"⚠️ No data directory found for today at {data_dir}")
    print("="*50 + "\n")

    # 3. RUN THE BOT
    # By default, we run the Desktop Bot
    # Using python3 -m src.SportyBet_Bot would be cleaner but let's stick to script execution
    # since we want SportyBet_Bot.py to run with its own arg parsing if any.
    bot_script = "SportyBet_Bot.py"
    bot_path = os.path.join(script_dir, bot_script)
    if os.path.exists(bot_path):
        print("\n>>> STARTING SPORTYBET BOT <<<")
        run_script(bot_script)
    else:
        print(f"\n>>> ERROR: {bot_script} not found! <<<")

if __name__ == "__main__":
    main()
