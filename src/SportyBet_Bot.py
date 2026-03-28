from func import main_date,save_daily_csv2,saving_files,place_bet,sort_by_name_and_time_exact,click_center
from datetime import datetime
from pyppeteer import launch
from main_calc import cal
from login import Login_to
import asyncio
import pandas as pd
import warnings
import os
from dotenv import load_dotenv

import google.generativeai as genai

load_dotenv()
warnings.simplefilter(action='ignore',category=pd.errors.PerformanceWarning)

# ==========================================================
# CONFIGURATION
# ==========================================================
# All dynamic options are pulled from environment variables (see main.py)
STAKE_AMOUNT = int(os.getenv("STAKE_AMOUNT", "100")) 
MAX_GAMES_PER_SLIP = 10     # Max matches in one accumulator
PERCENT_THRESHOLD = int(os.getenv("PERCENT_THRESHOLD", "50")) # Min prediction percentage
MAX_TOTAL_SLIPS = int(os.getenv("MAX_TOTAL_SLIPS", "5")) # Stop after placing this many slips
# Check environment variable for AI mode (default: ON)
AI_MODE = os.getenv("NO_AI", "false").lower() != "true"
IGNORE_HISTORY = False       # Set to False to prevent re-betting same matches
# ==========================================================

# Initialize Gemini if AI_MODE is on
if AI_MODE:
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')
            print("🤖 Gemini AI initialized successfully.")
        except Exception as e:
            print(f"⚠️ Gemini init error: {e}")
            AI_MODE = False
    else:
        print("⚠️ AI_MODE is ON but GEMINI_API_KEY is missing in .env!")
        AI_MODE = False

async def verify_with_ai(home, away, h_per, d_per, a_per, ov_per, un_per, selection):
    if not AI_MODE: return True
    
    print(f"🤔 AI is analyzing: {home} vs {away} ({selection})...")
    prompt = f"""
    Analyze this football match: {home} vs {away}.
    Predictions: Home {h_per:.0f}%, Draw {d_per:.0f}%, Away {a_per:.0f}%, Over2.5 {ov_per:.0f}%.
    Bot selection: {selection}.
    Is this a safe bet? Start with 'BET: YES' or 'BET: NO', then 1 short sentence explanation.
    """
    try:
        response = await asyncio.to_thread(model.generate_content, prompt)
        text = response.text.strip()
        print(f"🤖 AI Result: {text}")
        return "BET: YES" in text.upper()
    except Exception as e:
        if "429" in str(e):
            print(f"⚠️ AI Quota Exceeded (429). Proceeding with fallback...")
        else:
            print(f"⚠️ AI API Error: {e}")
        return True # Fallback

# Project structure: root/src/SportyBet_Bot.py -> data/
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_files_path = os.path.join(project_root, 'data', f'{str(main_date())} Files')
save_dir = save_daily_csv2(main_dir=os.path.join(project_root, 'data'), second_dir_path_name=str(main_date()) + ' Main_Files')
save_path = f'{save_dir}/Data.csv'
placed_bets_path = f'{save_dir}/Placed_Bets.csv'

def load_csv_safe(path, name):
    try:
        if os.path.exists(path): 
            df = pd.read_csv(path)
            # print(f"✅ Loaded {name}: {len(df)} rows")
            return df
        else: return pd.DataFrame()
    except: return pd.DataFrame()

acc_df_f = load_csv_safe(f'{csv_files_path}/accumulator.csv', "Accumulator")
bcl_df_f = load_csv_safe(f'{csv_files_path}/betclan.csv', "BetClan")
fst_df_f = load_csv_safe(f'{csv_files_path}/footballsupertips.csv', "FootballSuperTips")
frb_df_f = load_csv_safe(f'{csv_files_path}/forebet.csv', "Forebet")
pre_df_f = load_csv_safe(f'{csv_files_path}/prematips.csv', "Prematips")
sta_df_f = load_csv_safe(f'{csv_files_path}/statarea.csv', "Statarea")

async def main():
    chrome_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    browser = await launch(executablePath=chrome_path if os.path.exists(chrome_path) else None, headless=False, args=['--no-sandbox'])
    page = await browser.newPage()
    await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
    await page.goto('https://www.sportybet.com/ng/sport/football/today', timeout=60000, waitUntil='networkidle2')
    await Login_to(page)

    total_slips_placed = 0
    print(f"DEBUG: AI_MODE is {'ON' if AI_MODE else 'OFF'}")
    print(f"DEBUG: IGNORE_HISTORY is {'ON' if IGNORE_HISTORY else 'OFF'}")
    
    while total_slips_placed < MAX_TOTAL_SLIPS:
        try:
            await page.waitForSelector('.m-table-row, .m-table-cell-home', timeout=10000)
            await asyncio.sleep(2)
        except:
            print("🏁 No more matches found or timeout.")
            break

        match_data = await page.evaluate('''() => {
            const rows = Array.from(document.querySelectorAll('.m-table-row, div[id^="match_"]'));
            return rows.map((row, idx) => {
                const home = row.querySelector('.m-table-cell-home, .home-team, div[class*="home"]')?.innerText.trim();
                const away = row.querySelector('.m-table-cell-away, .away-team, div[class*="away"]')?.innerText.trim();
                const time = row.querySelector('.m-table-cell-time, .time, div[class*="time"]')?.innerText.trim();
                return { idx, home, away, time };
            }).filter(m => m.home && m.away);
        }''')

        print(f"\n🚀 Sourced {len(match_data)} matches. Scanning for batches...")
        
        batch_selections = [] 
        
        for m in match_data:
            if total_slips_placed >= MAX_TOTAL_SLIPS: break
            if len(batch_selections) >= MAX_GAMES_PER_SLIP:
                print(f"📦 Batch full ({MAX_GAMES_PER_SLIP} games).")
                break

            spt_home_team = m['home'].replace('SRL','SIMULATED REALITY LEAGUE')
            spt_away_team = m['away'].replace('SRL','SIMULATED REALITY LEAGUE')
            spt_time = m['time'] or "00:00"
            pp_target = f"{spt_home_team}-{spt_away_team}"

            # History Check
            if not IGNORE_HISTORY and os.path.exists(placed_bets_path):
                try:
                    history = pd.read_csv(placed_bets_path)
                    if not history.empty and pp_target in history['INFO'].values:
                        continue
                except: pass

            # Match across all CSVs
            matches = []
            for name, df in [("ACC", acc_df_f), ("BCL", bcl_df_f), ("FST", fst_df_f), ("FRB", frb_df_f), ("PRE", pre_df_f), ("STA", sta_df_f)]:
                res = sort_by_name_and_time_exact(df, spt_home_team, spt_away_team, spt_time, PERCENT_THRESHOLD)
                if not res.empty:
                    matches.append(res)

            if len(matches) >= 2:
                new_df = pd.concat(matches, ignore_index=True).drop_duplicates(subset=['NAME'],keep='first')
                h_per = new_df['HOME PER'].mean()
                a_per = new_df['AWAY PER'].mean()
                ov_per = new_df['OVER 2.5'].mean()
                d_per = new_df['DRAW PER'].mean()
                un_per = new_df['UNDER 2.5'].mean()
                
                selection = "Home Win" if h_per >= 50 else "Away Win" if a_per >= 50 else None
                
                if selection:
                    if await verify_with_ai(spt_home_team, spt_away_team, h_per, d_per, a_per, ov_per, un_per, selection):
                        col = 0 if selection == "Home Win" else 2
                        batch_selections.append({'idx': m['idx'], 'col': col, 'target': pp_target})
                        print(f"   ✅ AI Approved: {spt_home_team} vs {spt_away_team} -> {selection}")
                    else:
                        print(f"   ❌ AI Rejected: {spt_home_team} vs {spt_away_team}")

        # Place the slip
        if batch_selections:
            print(f"⚡ Selecting {len(batch_selections)} games...")
            await page.evaluate('''function(selections) {
                const rows = document.querySelectorAll('.m-table-row, div[id^="match_"]');
                selections.forEach(s => {
                    const row = rows[s.idx];
                    if (row) {
                        const odds = row.querySelectorAll('.m-outcome-odds, .m-outcome-item');
                        if(odds[s.col]) {
                            ['mousedown', 'click'].forEach(evt => odds[s.col].dispatchEvent(new MouseEvent(evt, {bubbles:true})));
                        }
                    }
                });
            }''', batch_selections)
            
            await asyncio.sleep(2)
            result = await place_bet(page, 0, main_amt=STAKE_AMOUNT)
            if result:
                total_slips_placed += 1
                for s in batch_selections:
                    saving_files(data={'INFO': [s['target']]}, path=placed_bets_path)
                
                booking_info = f" [Code: {result}]" if isinstance(result, str) else ""
                print(f"✅ Slip #{total_slips_placed} placed!{booking_info}")
            
            await page.evaluate('() => { const delBtn = document.querySelector(".m-betslip-delete-all"); if(delBtn) delBtn.click(); }')
            batch_selections = [] 
            if total_slips_placed >= MAX_TOTAL_SLIPS: break
            continue 

        # Next page
        is_Next = await page.Jx('//div[@class="pagination pagination"]/span[contains(@class,"icon-next") and not(contains(@class,"icon-disabled"))]')
        if is_Next:
            await is_Next[0].click()
            print("➡️ Next Page...")
            await asyncio.sleep(4)
        else:
            print("🏁 No more pages.")
            break

    print(f"DONE. Placed {total_slips_placed} slips total.")
    await asyncio.sleep(10)
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
