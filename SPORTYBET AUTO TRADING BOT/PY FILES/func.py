
from difflib import SequenceMatcher as ss
from datetime import datetime, timedelta
from datetime import date, timedelta
# from tkinter import simpledialog
from bs4 import BeautifulSoup
from lxml import html
# import tkinter as tk
import requests
import asyncio
import os
import atexit

match_day_date = datetime.now().strftime("%Y-%m-%d")

def main_date(day = match_day_date):
    return day


def info_init():
    print(' \n ########################################################################################################')
    print('This project was developed by Ezee Kits (Peter) – Electrical & Electronics Engineer, Nigeria 🇳🇬.')
    print('Automation • Machine Learning • AI • Web Scraping/Automation • Data Engineering.')
    print('\nGitHub: https://github.com/Ezee-Kits/')
    print('YouTube: https://www.youtube.com/@Ezee_Kits')
    print('Email: ezeekits@gmail.com ')
    print('######################################################################################################## \n')


def save_daily_csv():
    # Folder name
    folder_name = f"{str(main_date())} Files"
    # Get the parent directory of this file's directory (SPORTYBET AUTO TRADING BOT)
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    main_dir = os.path.join(parent_dir, "CSV FILES")
    path = os.path.join(main_dir, folder_name)

    # Create folder if it doesn't exist
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        print(f"Folder '{folder_name}' created successfully in '{main_dir}'.")
    else:
        # print(f"Folder '{folder_name}' already exists in '{main_dir}'.")
        pass
    return path

def save_daily_csv2(main_dir,second_dir_path_name):
    # Folder name
    path = os.path.join(main_dir, second_dir_path_name)

    # Create folder if it doesn't exist
    if not os.path.exists(path):
        os.makedirs(path)
        print(f" \n PATH ALREADY EXIST BUT WAS CREATED SUCCESFULLY \n ")
    else:
        print(f" \n PATH ALREADY EXIST BUT WAS CREATED SUCCESFULLY \n ")
    return path

def requests_init(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup, response
        else:
            return None, None
    except:
        return None, None

def tree_init(optional):
    tree = html.fromstring(optional.content)
    return tree

def saving_files(data,path):
    df = pd.DataFrame(data)
    # Check if file exists to decide on header and append mode
    if not os.path.isfile(path):
        df.to_csv(path, index=False)
        print('============================= FIRST FILE SAVED ==========================')
    else:
        # Load existing data to avoid duplicates in the same run if needed
        # but here we just append as the bot handles its own tracking
        df.to_csv(path, mode='a', header=False, index=False)
        print(' ------------------------------------ ALL FILES SAVED  ------------------------------------- \n')
    return True

def drop_duplicate(path):
    df = pd.read_csv(path)
    # df = df.drop_duplicates(subset=['HOME TEAM','AWAY TEAM'],keep='first')
    df = df.drop_duplicates(keep='first')
    df.to_csv(path,index=False)
    return True

def sorting_values(path,value,ascending_mode):
    df = pd.read_csv(path)
    df = df.sort_values(by=value,ascending=ascending_mode)
    df.to_csv(path,index=False)
    return True

def sorting_values_path_to_save(path,value,path_to_save,ascending_mode):
    df = pd.read_csv(path)
    df = df.sort_values(by=value,ascending=ascending_mode)
    df.to_csv(path_to_save,index=False)
    return True

import pandas as pd

async def place_bet(page, edge_amt, browser_delay_time=2000, main_amt=100):
    try:
        print(f"💰 Initializing {main_amt} Naira Batch Bet...")
        
        # 1️⃣ TARGET SPECIFIC STAKE INPUT FROM HTML
        success = await page.evaluate('''(amt) => {
            const input = document.querySelector('#j_stake_0 input') || document.querySelector('.m-input.fs-exclude');
            if (input) {
                input.value = amt.toString();
                ['input', 'change', 'blur'].forEach(name => {
                    input.dispatchEvent(new Event(name, { bubbles: true }));
                });
                input.focus();
                return true;
            }
            return false;
        }''', main_amt)

        if not success:
            print("❌ Error: Could not find stake input.")
            return False

        await asyncio.sleep(2) 

        # 2️⃣ VERIFY TOTAL STAKE
        total_stake = await page.evaluate('''() => {
            const valueEl = document.querySelector('.m-betslip-total-stake-value');
            if (valueEl && valueEl.innerText.includes('100')) return valueEl.innerText;

            const labels = Array.from(document.querySelectorAll('.m-label'));
            const totalLabel = labels.find(l => l.innerText.includes('Total Stake'));
            if (totalLabel && totalLabel.nextElementSibling) {
                return totalLabel.nextElementSibling.innerText.trim();
            }
            return document.querySelector('.m-betslip')?.innerText || "NOT_FOUND";
        }''')
        
        print(f"DEBUG: Verified Total Stake context: {total_stake.replace('\\n', ' ')}")
        
        if "100" not in total_stake.replace(',', ''):
            print(f"❌ SAFETY ABORT: Stake is '{total_stake}', not verified.")
            return False

        # 3️⃣ HANDLE 'ACCEPT CHANGES' OR 'PLACE BET'
        await page.evaluate('''() => {
            const btns = Array.from(document.querySelectorAll('button.af-button--primary'));
            const acceptBtn = btns.find(b => b.innerText.includes('Accept'));
            if (acceptBtn) acceptBtn.click();
        }''')
        await asyncio.sleep(1)

        await page.evaluate('''() => {
            const btns = Array.from(document.querySelectorAll('button.af-button--primary'));
            const placeBtn = btns.find(b => b.innerText.includes('Place Bet') || b.getAttribute('data-op') === 'desktop-betslip-place-bet-button');
            if (placeBtn) placeBtn.click();
        }''')
        
        await asyncio.sleep(1.5)

        # 4️⃣ CLICK CONFIRM IN POPUP
        confirmed = await page.evaluate('''() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const confirmBtn = btns.find(b => 
                b.innerText.includes('Confirm') || 
                (b.querySelector('span') && b.querySelector('span').innerText.includes('Confirm')) ||
                b.getAttribute('data-op') === 'confirm-bet-button'
            );
            if (confirmBtn) {
                confirmBtn.click();
                return true;
            }
            return false;
        }''')

        if confirmed:
            print("✅ BATCH BET CONFIRMED SUCCESSFULLY!")
            return True
        else:
            print("⚠️ Confirmation popup not detected. Checking for OK button...")
            await page.evaluate('(() => { const okBtn = document.querySelector("button.af-button--primary"); if(okBtn) okBtn.click(); })()')
            return False

    except Exception as e:
        print(f"❌ Betting error: {e}")
        return False


async def click_center(page, xpath: str, delay: float = 0.5):
    try:
        # Wait for the element to be present in the DOM
        element = await page.waitForXPath(xpath, timeout=10000)

        # Get the bounding box of the element
        bounding_box = await element.boundingBox()

        if not bounding_box:
            print(f"[ERROR] Could not find bounding box for '{xpath}'")
            return False

        # Calculate the center point
        center_x = bounding_box['x'] + bounding_box['width'] / 2
        center_y = bounding_box['y'] + bounding_box['height'] / 2

        # Move the mouse to the center and click
        await page.mouse.move(center_x, center_y)
        await page.mouse.click(center_x, center_y)

        # print(f"[OK] Clicked center of '{xpath}' at ({center_x:.2f}, {center_y:.2f})")

        # Optional delay after click
        if delay > 0:
            await asyncio.sleep(delay)

        return True

    except Exception as e:
        # print(f"[ERROR] Could not click on '{xpath}': {e}")
        return False

def sort_by_name_and_time(df, spt_home_team, spt_away_team, spt_time, percent):
    try:
        # Step 1: Calculate similarity for home team
        df['HOME_SIMILARITY'] = df['HOME TEAM'].apply(
            lambda x: ss(None, str(x).lower(), str(spt_home_team).lower()).ratio() * 100
        )

        # Step 2: Calculate similarity for away team
        df['AWAY_SIMILARITY'] = df['AWAY TEAM'].apply(
            lambda x: ss(None, str(x).lower(), str(spt_away_team).lower()).ratio() * 100
        )

        # Step 3: Keep rows where both similarities >= threshold
        filtered_df = df[
            (df['HOME_SIMILARITY'] >= percent) &
            (df['AWAY_SIMILARITY'] >= percent)
        ].copy()

        if filtered_df.empty:
            return filtered_df  # nothing matches, return empty

        # Step 4: Sort by combined similarity
        filtered_df['TOTAL_SIMILARITY'] = (
            filtered_df['HOME_SIMILARITY'] + filtered_df['AWAY_SIMILARITY']
        ) / 2
        filtered_df = filtered_df.sort_values(by='TOTAL_SIMILARITY', ascending=False).reset_index(drop=True)

        # Step 5: Filter by time range
        def time_within_range(row_time_str):
            try:
                row_time = datetime.strptime(row_time_str, "%H:%M")
                target_time = datetime.strptime(spt_time, "%H:%M")
                
                # Check if row_time is within 1 hour of target_time
                diff = abs((row_time - target_time).total_seconds()) / 3600
                return diff <= 1.5 # 1.5 hours tolerance
            except:
                return False

        filtered_df = filtered_df[filtered_df['TIME'].apply(time_within_range)].reset_index(drop=True)

        # Step 6: Drop helper columns
        filtered_df = filtered_df.drop(columns=['HOME_SIMILARITY', 'AWAY_SIMILARITY', 'TOTAL_SIMILARITY'])

        return filtered_df

    except Exception as e:
        print(f"Error sorting by team similarity and time: {e}")
        return df

def sort_by_name_and_time_exact(df, spt_home_team, spt_away_team, spt_time, percent):
    try:
        if df.empty: return df
        # Step 1: Calculate similarity for home team
        df['HOME_SIMILARITY'] = df['HOME TEAM'].apply(
            lambda x: ss(None, str(x).lower(), str(spt_home_team).lower()).ratio() * 100
        )

        # Step 2: Calculate similarity for away team
        df['AWAY_SIMILARITY'] = df['AWAY TEAM'].apply(
            lambda x: ss(None, str(x).lower(), str(spt_away_team).lower()).ratio() * 100
        )

        # Step 3: Keep rows where both similarities >= threshold
        filtered_df = df[
            (df['HOME_SIMILARITY'] >= percent) &
            (df['AWAY_SIMILARITY'] >= percent)
        ].copy()

        if filtered_df.empty:
            return filtered_df  # nothing matches, return empty

        # Step 4: Sort by combined similarity
        filtered_df['TOTAL_SIMILARITY'] = (
            filtered_df['HOME_SIMILARITY'] + filtered_df['AWAY_SIMILARITY']
        ) / 2
        filtered_df = filtered_df.sort_values(by='TOTAL_SIMILARITY', ascending=False).reset_index(drop=True)

        # Step 5: Clean and parse time
        try:
            # Extract only HH:MM if there's extra data (e.g., ID: 12345)
            clean_spt_time = spt_time.split()[0] if " " in spt_time else spt_time
            if ":" not in clean_spt_time:
                return pd.DataFrame() # Skip if not a valid time format
                
            spt_time_dt = datetime.strptime(clean_spt_time, "%H:%M")

            valid_times = {
                (spt_time_dt - timedelta(hours=1)).strftime("%H:%M"),
                spt_time_dt.strftime("%H:%M"),
                (spt_time_dt + timedelta(hours=1)).strftime("%H:%M")
            }

            filtered_df = filtered_df[filtered_df['TIME'].isin(valid_times)].reset_index(drop=True)
        except Exception as e:
            return pd.DataFrame() 

        # Step 6: Drop helper columns
        filtered_df = filtered_df.drop(columns=['HOME_SIMILARITY', 'AWAY_SIMILARITY', 'TOTAL_SIMILARITY'])

        return filtered_df

    except Exception as e:
        return pd.DataFrame()





def sort_by_name(df, spt_home_team, spt_away_team, percent):
    try:
        # Step 1: Calculate similarity for home team
        df['HOME_SIMILARITY'] = df['HOME TEAM'].apply(
            lambda x: ss(None, str(x).lower(), str(spt_home_team).lower()).ratio() * 100
        )

        # Step 2: Calculate similarity for away team
        df['AWAY_SIMILARITY'] = df['AWAY TEAM'].apply(
            lambda x: ss(None, str(x).lower(), str(spt_away_team).lower()).ratio() * 100
        )

        # Step 3: Keep rows where both similarities >= threshold
        filtered_df = df[
            (df['HOME_SIMILARITY'] >= percent) &
            (df['AWAY_SIMILARITY'] >= percent)
        ].copy()

        if filtered_df.empty:
            return filtered_df  # nothing matches, return empty

        # Step 4: Sort by combined similarity
        filtered_df['TOTAL_SIMILARITY'] = (
            filtered_df['HOME_SIMILARITY'] + filtered_df['AWAY_SIMILARITY']
        ) / 2
        filtered_df = filtered_df.sort_values(by='TOTAL_SIMILARITY', ascending=False).reset_index(drop=True)

        # Step 5: Drop helper columns
        filtered_df = filtered_df.drop(columns=['HOME_SIMILARITY', 'AWAY_SIMILARITY', 'TOTAL_SIMILARITY'])

        return filtered_df

    except Exception as e:
        print(f"Error sorting by team similarity: {e}")
        return df

def sort_by_time(df, current_time):
    try:
        # Ensure current_time is a datetime object
        if isinstance(current_time, str):
            current_time = datetime.strptime(current_time, "%H:%M")

        # Step 1: Filter matches within +/- 1 hour of the current time
        def time_diff(row_time_str):
            try:
                row_time = datetime.strptime(row_time_str, "%H:%M")
                diff = abs((row_time - current_time).total_seconds()) / 3600
                return diff <= 1.0
            except:
                return False

        filtered_df = df[df['TIME'].apply(time_diff)].copy()

        return filtered_df

    except Exception as e:
        print(f"Error sorting by time: {e}")
        return df

async def xpath_scroll_center(page, xpath: str, delay: float = 0.5):
    try:
        # Wait for the element to be present in the DOM
        element = await page.waitForXPath(xpath, timeout=10000)

        # Scroll the element into the center of the viewport
        await page.evaluate('''
            (el) => {
                el.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' });
            }
        ''', element)

        # print(f"[OK] Scrolled To center of '{xpath}'")

        return True

    except Exception as e:
        # print(f"[ERROR] Could not scroll on '{xpath}': {e}")
        return False


atexit.register(info_init)
