
import asyncio
import os







async def Login_to(page):
    try:
        acct_balance = await page.waitForSelector('span[id="j_balance"]', timeout=10000)
        spt_acct_balance = (await (await acct_balance.getProperty('textContent')).jsonValue()).strip().replace('NGN ','').replace(',','').split('.')[0]
        if spt_acct_balance:
            print(f"\n>>> ALREADY LOGGED IN! ACCOUNT BALANCE: {spt_acct_balance} <<<\n")
            return False
    except:
        pass
    
    print("\n>>> NOT LOGGED IN! PROCEEDING TO LOGIN... <<<\n")
    
    # Get credentials from environment variables for automation
    email_to_input = os.getenv("SPORTYBET_PHONE")
    password_to_input = os.getenv("SPORTYBET_PASSWORD")

    if not email_to_input or not password_to_input:
        print("Credentials not found in environment variables.")
        email_to_input = input("Enter phone number:::::::: ")
        password_to_input = input("Enter password:::::::: ")

    email_to = await page.waitForSelector('div.m-phone input[name="phone"]', timeout=7000)
    await page.evaluate('(el) => el.scrollIntoView({ behavior: "smooth", block: "center" })', email_to)
    await email_to.click()
    await asyncio.sleep(1)
    await email_to.click()
    await asyncio.sleep(1)
    await page.keyboard.down('Control')
    await page.keyboard.press('A')
    await page.keyboard.up('Control')
    await page.keyboard.press('Backspace')
    await asyncio.sleep(1)
 
    # 3️⃣ Type the phone number
    await email_to.type(str(email_to_input))
    await asyncio.sleep(1)


    password_to = await page.waitForSelector('div.m-psd input[name="psd"]', timeout=4000)
    await page.evaluate('(el) => el.scrollIntoView({ behavior: "smooth", block: "center" })', password_to)
    await password_to.click()
    await asyncio.sleep(1)
    await password_to.click()
    await asyncio.sleep(1)
    await page.keyboard.down('Control')
    await page.keyboard.press('A')
    await page.keyboard.up('Control')
    await page.keyboard.press('Backspace')
    await asyncio.sleep(1)

    # 3️⃣ Type the password
    await password_to.type(str(password_to_input))   
    await asyncio.sleep(1)

    login_button = await page.waitForSelector('button[name="logIn"]', timeout=4000)
    await page.evaluate('(el) => el.scrollIntoView({ behavior: "smooth", block: "center" })', login_button)
    await login_button.click()
    await asyncio.sleep(.5)
    await login_button.click()
    await asyncio.sleep(3)



    try:
        now_balance = await page.waitForSelector('span[id="j_balance"]', timeout=15000)
        balance_text = (await (await now_balance.getProperty('textContent')).jsonValue())
        spt_acct_balance = balance_text.strip().replace('NGN ','').replace(',','').split('.')[0]
        if not spt_acct_balance:
            spt_acct_balance = "0 (Detected empty)"
        print(f"\n>>> LOGIN SUCCESSFUL! ACCOUNT BALANCE: {spt_acct_balance} <<<\n")
    except:
        print("\n>>> LOGIN MIGHT HAVE FAILED OR PAGE IS SLOW. <<<\n")
        if not (os.getenv("SPORTYBET_PHONE") and os.getenv("SPORTYBET_PASSWORD")):
            input("PRESS ENTER AFTER LOGGING IN AND SETTING UP THE PAGE TO AUTOMATE...")