import os
import sys
import subprocess
import time
import pandas as pd

def run_script(script_name):
    print(f"\n>>> RUNNING: {script_name} <<<")
    try:
        # Use sys.executable to ensure we use the same virtual environment's python
        result = subprocess.run([sys.executable, script_name], check=False)
        if result.returncode == 0:
            print(f">>> SUCCESS: {script_name} <<<")
        else:
            print(f">>> WARNING: {script_name} exited with code {result.returncode} <<<")
    except Exception as e:
        print(f">>> ERROR running {script_name}: {e} <<<")

def main():
    # Change directory to where the scripts are
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

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
        if os.path.exists(scraper):
            run_script(scraper)
        else:
            print(f">>> SKIP: {scraper} (File not found) <<<")

    # 2. DATA SUMMARY
    print("\n" + "="*50)
    print("           SCRAPING SUMMARY")
    print("="*50)
    # Correct path calculation for CSV FILES
    project_root = os.path.dirname(os.path.dirname(script_dir))
    csv_dir = os.path.join(project_root, "SPORTYBET AUTO TRADING BOT", "CSV FILES", f"{time.strftime('%Y-%m-%d')} Files")
    if os.path.exists(csv_dir):
        for f in os.listdir(csv_dir):
            if f.endswith('.csv'):
                try:
                    count = len(pd.read_csv(os.path.join(csv_dir, f)))
                    print(f"✅ {f:20} : {count} matches found")
                except:
                    print(f"❌ {f:20} : Could not read file")
    else:
        print(f"⚠️ No CSV directory found for today at {csv_dir}")
    print("="*50 + "\n")

    # 3. RUN THE BOT
    bot_script = "SportyBet Bot.py"
    if os.path.exists(bot_script):
        print("\n>>> STARTING SPORTYBET BOT <<<")
        run_script(bot_script)
    else:
        print(f"\n>>> ERROR: {bot_script} not found! <<<")

if __name__ == "__main__":
    main()
