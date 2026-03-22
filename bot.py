# import random
# import time
# import requests
# import undetected_chromedriver as uc
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# # -------- Launch undetected browser --------
# options = uc.ChromeOptions()
# options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_argument("--no-sandbox")
# options.add_argument("--disable-dev-shm-usage")
# options.add_argument("--window-size=1920,1080")

# driver = uc.Chrome(options=options,version_main=145)
# driver.maximize_window()

# wait = WebDriverWait(driver, 20)
# API_KEY = "5573fd8190654adf4f131e6c35c2de62"

# def solve_captcha(driver, wait):
#     print("Solving captcha...")

#     # -------- Wait for captcha image to fully load --------
#     time.sleep(2)
#     img = wait.until(EC.presence_of_element_located((By.ID, "captchaImage")))
    
#     # Scroll to captcha naturally
#     driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", img)
#     time.sleep(random.uniform(0.5, 1.0))

#     src = img.get_attribute("src")
#     base64_data = src.split(",", 1)[1]

#     # -------- Submit to 2captcha --------
#     response = requests.post("https://2captcha.com/in.php", data={
#         "key": API_KEY,
#         "method": "base64",
#         "body": base64_data,
#         "json": 1,
#         "case": 1
#     })

#     result = response.json()
#     if result["status"] != 1:
#         raise Exception(f"2captcha submission failed: {result['request']}")

#     captcha_id = result["request"]
#     print(f"Captcha submitted (ID: {captcha_id}), waiting for solution...")

#     # -------- Poll for result --------
#     captcha_text = None
#     for attempt in range(24):
#         time.sleep(5)
#         res = requests.get("https://2captcha.com/res.php", params={
#             "key": API_KEY,
#             "action": "get",
#             "id": captcha_id,
#             "json": 1
#         }).json()

#         if res["status"] == 1:
#             captcha_text = res["request"]
#             print(f"✅ Captcha solved: {captcha_text}")
#             break
#         elif res["request"] == "CAPCHA_NOT_READY":
#             print(f"  Not ready yet... ({attempt + 1}/24)")
#             continue
#         else:
#             raise Exception(f"2captcha error: {res['request']}")

#     if not captcha_text:
#         raise Exception("Timed out waiting for captcha solution")

#     # -------- Verify captcha hasn't changed since we solved it --------
#     img_after = driver.find_element(By.ID, "captchaImage")
#     src_after = img_after.get_attribute("src")
    
#     if src_after != src:
#         print("⚠️ Captcha changed while solving! Re-solving...")
#         return solve_captcha(driver, wait)  # recurse once

#     # -------- Click on captcha input naturally --------
#     captcha_input = wait.until(
#         EC.presence_of_element_located((By.XPATH,
#             "//input[@placeholder='Enter Captcha'] | //input[@id='captchaCode'] | //input[@name='captcha']"
#         ))
#     )

#     # Move to element naturally with ActionChains
#     from selenium.webdriver.common.action_chains import ActionChains
#     actions = ActionChains(driver)
#     actions.move_to_element(captcha_input).pause(random.uniform(0.3, 0.7)).click().perform()
#     time.sleep(0.5)

#     # -------- Type each letter human-like over ~6 seconds --------
#     total_chars = len(captcha_text)
#     total_time = 6.0

#     print(f"Typing captcha '{captcha_text}' over ~6 seconds...")

#     for i, char in enumerate(captcha_text):
#         current_value = captcha_text[:i + 1]
#         driver.execute_script("""
#             var el = arguments[0];
#             var nativeInputValueSetter = Object.getOwnPropertyDescriptor(
#                 window.HTMLInputElement.prototype, 'value'
#             ).set;
#             nativeInputValueSetter.call(el, arguments[1]);
#             el.dispatchEvent(new Event('input', { bubbles: true }));
#             el.dispatchEvent(new Event('change', { bubbles: true }));
#         """, captcha_input, current_value)

#         print(f"  Typed: {current_value}")

#         if i < total_chars - 1:
#             min_delay = (total_time / total_chars) * 0.6
#             max_delay = (total_time / total_chars) * 1.4
#             delay = random.uniform(min_delay, max_delay)
#             time.sleep(delay)

#     print("✅ Captcha fully entered")

#     # -------- Small pause before submit (human-like) --------
#     time.sleep(random.uniform(1.5, 2.5))

#     # -------- Wait for submit to enable then click --------
#     print("Waiting for submit button to enable...")
#     enabled_btn = WebDriverWait(driver, 15).until(
#         EC.element_to_be_clickable((By.XPATH,
#             "//button[contains(@class,'btn-brand-arrow') and not(@disabled)]"
#         ))
#     )

#     actions = ActionChains(driver)
#     actions.move_to_element(enabled_btn).pause(random.uniform(0.3, 0.6)).click().perform()
#     print("✅ Form submitted!")

#     return captcha_text

# driver = webdriver.Chrome()
# driver.maximize_window()

# driver.get("https://www.qatarvisacenter.com/")

# wait = WebDriverWait(driver, 20)

# # -------- Select Language --------
# language_dropdown = wait.until(
#     EC.element_to_be_clickable((By.XPATH, "//div[@data-bs-toggle='dropdown']"))
# )
# driver.execute_script("arguments[0].click();", language_dropdown)

# english_option = wait.until(
#     EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'English')] | //li[contains(text(),'English')]"))
# )
# driver.execute_script("arguments[0].click();", english_option)


# # -------- Open Country Dropdown --------
# country_dropdown = wait.until(
#     EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='-- Select Country --']"))
# )
# driver.execute_script("arguments[0].click();", country_dropdown)


# # -------- Select Pakistan --------
# pakistan = wait.until(
#     EC.element_to_be_clickable((By.XPATH, "//ul[contains(@class,'dropdown-menu')]//a[text()='Pakistan']"))
# )
# driver.execute_script("arguments[0].click();", pakistan)

# print("Pakistan selected successfully")

# book_appointment = wait.until(
#     EC.element_to_be_clickable((By.XPATH, "//a[contains(@class,'card-box') and contains(text(),'Book Appointment')]"))
# )

# driver.execute_script("arguments[0].click();", book_appointment)

# print("Book Appointment clicked")

# # -------- Close Modal --------
# close_modal = wait.until(
#     EC.element_to_be_clickable((By.XPATH, "//img[@class='mod-close']"))
# )
# driver.execute_script("arguments[0].click();", close_modal)

# print("Modal closed successfully")

# # -------- Enter Passport Number --------
# passport_number = input("Enter Passport Number: ")
# passport_input = wait.until(
#     EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Passport Number']"))
# )
# passport_input.send_keys(passport_number)
# print("Passport number entered")

# # -------- Get Visa Number from CLI --------
# visa_number = input("Enter Visa Number: ")

# # -------- Enter Visa Number --------
# visa_input = wait.until(
#     EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Visa Number']"))
# )

# visa_input.send_keys(visa_number)

# print("Visa number entered")

# # -------- Solve Captcha --------
# captcha_text = solve_captcha(driver,wait)

# # -------- Enter Captcha --------
# captcha_input = wait.until(
#     EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Enter Captcha' or @id='captchaInput' or @name='captcha']"))
# )
# captcha_input.clear()
# captcha_input.send_keys(captcha_text)
# print("Captcha entered")

# # Option 2: Scroll + click
# submit_btn = wait.until(
#     EC.presence_of_element_located((By.XPATH, "//button[contains(@class,'btn-brand-arrow')]"))
# )
# driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
# time.sleep(1)
# driver.execute_script("arguments[0].click();", submit_btn)
# print("✅ Form submitted!")

# # -------- Wait for next page & Close Modal --------
# # print("Waiting for next page to load...")
# # time.sleep(3)  # wait for page transition

# ok_button = wait.until(
#     EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='OK']"))
# )

# driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", ok_button)
# ok_button.click()
# print("✅ Modal closed successfully")

# # Wait for new page
# wait.until(lambda d: d.execute_script("return document.readyState") == "complete")


# from selenium.common.exceptions import TimeoutException

# def click_modal_ok(driver, wait_time=10):
#     """
#     Waits for optional modals and clicks the OK button if present.
#     """
#     # List of possible OK button XPaths
#     ok_buttons_xpaths = [
#         "//div[contains(@class,'appt')]//button[normalize-space()='Ok']",          # Modal 1
#         "//div[contains(@class,'appt')]//button[normalize-space()='OK']"           # Modal 2
#     ]

#     for xpath in ok_buttons_xpaths:
#         try:
#             ok_button = WebDriverWait(driver, wait_time).until(
#                 EC.element_to_be_clickable((By.XPATH, xpath))
#             )
#             # Scroll and click
#             driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", ok_button)
#             driver.execute_script("arguments[0].click();", ok_button)
#             print(f"✅ Clicked OK button for modal: {xpath}")
#             # Wait briefly to allow modal to disappear
#             time.sleep(1)
#         except TimeoutException:
#             # Modal with this XPath did not appear, continue
#             continue

# # Example usage after submitting form:
# click_modal_ok(driver)

# # Phone
# phone_number = input("Enter phone number")
# phone_input = wait.until(EC.element_to_be_clickable((By.ID, "phone")))
# phone_input.clear()
# phone_input.send_keys(phone_number)

# # Email
# email_address = input("Enter email address")
# email_input = wait.until(EC.element_to_be_clickable((By.ID, "email")))
# email_input.clear()
# email_input.send_keys(email_address)

# # Checkbox
# checkbox = wait.until(EC.element_to_be_clickable((By.ID, "checkVal")))
# if not checkbox.is_selected():
#     checkbox.click()





import os
import random
import time
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from dotenv import load_dotenv

load_dotenv()

def decrypt_response(encrypted_data):
    """Decrypt AES CBC encrypted response using the key from captcha.html"""
    key = b"cvq@4202temoib!&"
    iv  = b"cvq@4202temoib!&"

    # Base64 decode
    encrypted_bytes = base64.b64decode(encrypted_data)

    # Decrypt
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)
    decrypted_str = decrypted.decode("utf-8")

    # Pretty print if JSON
    try:
        import json
        parsed = json.loads(decrypted_str)
        return json.dumps(parsed, indent=2)
    except:
        return decrypted_str


def call_appointment_dates_api(driver):
    import json

    print("Intercepting API call through browser network...")

    # Inject fetch interceptor BEFORE the page makes the call
    driver.execute_script("""
        window._apiResponse = null;
        window._originalFetch = window.fetch;
        window.fetch = function(...args) {
            return window._originalFetch(...args).then(response => {
                if (args[0] && args[0].toString().includes('getvscappointmentdates')) {
                    response.clone().text().then(body => {
                        window._apiResponse = body;
                        console.log('API intercepted:', body);
                    });
                }
                return response;
            });
        };
    """)

    print("Fetch interceptor injected, waiting for page to make API call...")

    # Also intercept XMLHttpRequest
    driver.execute_script("""
        window._originalXHROpen = XMLHttpRequest.prototype.open;
        window._originalXHRSend = XMLHttpRequest.prototype.send;
        XMLHttpRequest.prototype.open = function(method, url, ...rest) {
            this._url = url;
            return window._originalXHROpen.apply(this, [method, url, ...rest]);
        };
        XMLHttpRequest.prototype.send = function(...args) {
            this.addEventListener('load', function() {
                if (this._url && this._url.includes('getvscappointmentdates')) {
                    window._apiResponse = this.responseText;
                    console.log('XHR intercepted:', this.responseText);
                }
            });
            return window._originalXHRSend.apply(this, args);
        };
    """)

    # Wait for the response to be captured (up to 15 seconds)
    raw_response = None
    for _ in range(30):
        time.sleep(0.5)
        raw_response = driver.execute_script("return window._apiResponse;")
        if raw_response:
            break

    if not raw_response:
        print("⚠️ API call not intercepted, trying direct localStorage/sessionStorage check...")
        # Sometimes Angular/Vue stores data in window variables
        raw_response = driver.execute_script("""
            // Check common Angular/Vue state locations
            return window.__APPOINTMENT_DATA__ || 
                   window.appointmentDates || 
                   sessionStorage.getItem('appointmentDates') ||
                   null;
        """)

    if not raw_response:
        print("❌ Could not capture API response")
        return None

    print(f"✅ Captured Response: {raw_response}")

    try:
        json_response = json.loads(raw_response)

        if "encryptedData" in json_response:
            encrypted = json_response["encryptedData"]
            print("\n🔓 Decrypting...")
            decrypted = decrypt_response(encrypted)
            print(f"✅ Decrypted:\n{decrypted}")
            return json.loads(decrypted)
        else:
            decrypted = decrypt_response(raw_response.strip().strip('"'))
            print(f"✅ Decrypted:\n{decrypted}")
            return json.loads(decrypted)

    except Exception as e:
        print(f"Parse/Decrypt error: {e}")
        print(f"Raw was: {raw_response}")
        return None
# -------- Launch undetected browser --------
options = uc.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")

driver = uc.Chrome(options=options, version_main=145)
driver.maximize_window()

wait = WebDriverWait(driver, 20)
API_KEY = os.getenv("API_KEY")

def solve_captcha(driver, wait):
    print("Solving captcha...")

    time.sleep(2)
    img = wait.until(EC.presence_of_element_located((By.ID, "captchaImage")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", img)
    time.sleep(random.uniform(0.5, 1.0))

    src = img.get_attribute("src")
    base64_data = src.split(",", 1)[1]

    response = requests.post("https://2captcha.com/in.php", data={
        "key": API_KEY,
        "method": "base64",
        "body": base64_data,
        "json": 1,
        "case": 1
    })

    result = response.json()
    if result["status"] != 1:
        raise Exception(f"2captcha submission failed: {result['request']}")

    captcha_id = result["request"]
    print(f"Captcha submitted (ID: {captcha_id}), waiting for solution...")

    captcha_text = None
    for attempt in range(24):
        time.sleep(5)
        res = requests.get("https://2captcha.com/res.php", params={
            "key": API_KEY,
            "action": "get",
            "id": captcha_id,
            "json": 1
        }).json()

        if res["status"] == 1:
            captcha_text = res["request"]
            print(f"✅ Captcha solved: {captcha_text}")
            break
        elif res["request"] == "CAPCHA_NOT_READY":
            print(f"  Not ready yet... ({attempt + 1}/24)")
            continue
        else:
            raise Exception(f"2captcha error: {res['request']}")

    if not captcha_text:
        raise Exception("Timed out waiting for captcha solution")

    # Verify captcha hasn't changed
    img_after = driver.find_element(By.ID, "captchaImage")
    src_after = img_after.get_attribute("src")
    if src_after != src:
        print("⚠️ Captcha changed while solving! Re-solving...")
        return solve_captcha(driver, wait)

    # Click captcha input
    from selenium.webdriver.common.action_chains import ActionChains
    captcha_input = wait.until(
        EC.presence_of_element_located((By.XPATH,
            "//input[@placeholder='Enter Captcha'] | //input[@id='captchaCode'] | //input[@name='captcha']"
        ))
    )
    actions = ActionChains(driver)
    actions.move_to_element(captcha_input).pause(random.uniform(0.3, 0.7)).click().perform()
    time.sleep(0.5)

    # Type human-like over ~6 seconds
    total_chars = len(captcha_text)
    total_time = 6.0
    print(f"Typing captcha '{captcha_text}' over ~6 seconds...")

    for i, char in enumerate(captcha_text):
        current_value = captcha_text[:i + 1]
        driver.execute_script("""
            var el = arguments[0];
            var nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype, 'value'
            ).set;
            nativeInputValueSetter.call(el, arguments[1]);
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        """, captcha_input, current_value)
        print(f"  Typed: {current_value}")

        if i < total_chars - 1:
            min_delay = (total_time / total_chars) * 0.6
            max_delay = (total_time / total_chars) * 1.4
            time.sleep(random.uniform(min_delay, max_delay))

    print("✅ Captcha fully entered")
    time.sleep(random.uniform(1.5, 2.5))

    # Click submit
    print("Waiting for submit button to enable...")
    enabled_btn = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH,
            "//button[contains(@class,'btn-brand-arrow') and not(@disabled)]"
        ))
    )
    actions = ActionChains(driver)
    actions.move_to_element(enabled_btn).pause(random.uniform(0.3, 0.6)).click().perform()
    print("✅ Form submitted!")

    return captcha_text


def click_modal_ok(driver, wait_time=10):
    ok_xpaths = [
        "//button[normalize-space()='Ok']",
        "//button[normalize-space()='OK']",
        "//div[contains(@class,'appt')]//button[normalize-space()='Ok']",
        "//div[contains(@class,'appt')]//button[normalize-space()='OK']",
    ]
    for xpath in ok_xpaths:
        try:
            ok_button = WebDriverWait(driver, wait_time).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", ok_button)
            driver.execute_script("arguments[0].click();", ok_button)
            print(f"✅ Modal OK clicked")
            time.sleep(1)
            return
        except TimeoutException:
            continue
    print("No modal OK button found, continuing...")


# ======== Main ========

driver.get("https://www.qatarvisacenter.com/")

# Select Language
language_dropdown = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//div[@data-bs-toggle='dropdown']"))
)
driver.execute_script("arguments[0].click();", language_dropdown)

english_option = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'English')] | //li[contains(text(),'English')]"))
)
driver.execute_script("arguments[0].click();", english_option)

# Country Dropdown
country_dropdown = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='-- Select Country --']"))
)
driver.execute_script("arguments[0].click();", country_dropdown)

# Select Pakistan
pakistan = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//ul[contains(@class,'dropdown-menu')]//a[text()='Pakistan']"))
)
driver.execute_script("arguments[0].click();", pakistan)
print("Pakistan selected successfully")

# Book Appointment
book_appointment = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//a[contains(@class,'card-box') and contains(text(),'Book Appointment')]"))
)
driver.execute_script("arguments[0].click();", book_appointment)
print("Book Appointment clicked")

# Close Modal
close_modal = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//img[@class='mod-close']"))
)
driver.execute_script("arguments[0].click();", close_modal)
print("Modal closed successfully")

# Passport Number
passport_number = input("Enter Passport Number: ")
passport_input = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Passport Number']"))
)
passport_input.send_keys(passport_number)
print("Passport number entered")

# Visa Number
visa_number = input("Enter Visa Number: ")
visa_input = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Visa Number']"))
)
visa_input.send_keys(visa_number)
print("Visa number entered")

# -------- Solve Captcha & Submit (all handled inside function) --------
solve_captcha(driver, wait)

# -------- Handle post-submit modal --------
click_modal_ok(driver)

# -------- Wait for page to load --------
wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
time.sleep(2)

# -------- Handle post-submit modal --------
click_modal_ok(driver)
print("Waiting for page 2 to fully load...")
time.sleep(5)

# Save cookies after page 1 success
cookies = driver.get_cookies()
print(f"Session cookies saved: {len(cookies)}")

# Wait for page 2 URL to be different
try:
    WebDriverWait(driver, 15).until(lambda d: "qatarvisacenter.com" in d.current_url)
    print(f"Current URL: {driver.current_url}")
except:
    pass

wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
time.sleep(3)

# Take screenshot to confirm we're on page 2
driver.save_screenshot("page2.png")
print("Screenshot saved as page2.png — check what page we're on")

# -------- Fill Phone human-like --------
phone_number = input("Enter phone number: ")
try:
    phone_input = wait.until(EC.element_to_be_clickable((By.ID, "phone")))
except:
    phone_input = wait.until(EC.element_to_be_clickable((By.XPATH, 
        "//input[@type='tel'] | //input[contains(@placeholder,'phone') or contains(@placeholder,'Phone')]"
    )))

driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", phone_input)
time.sleep(random.uniform(1.0, 2.0))
phone_input.click()
time.sleep(0.5)

for char in phone_number:
    phone_input.send_keys(char)
    time.sleep(random.uniform(0.15, 0.35))

print("Phone entered")
time.sleep(random.uniform(1.0, 2.0))

# -------- Fill Email human-like --------
email_address = input("Enter email address: ")
try:
    email_input = wait.until(EC.element_to_be_clickable((By.ID, "email")))
except:
    email_input = wait.until(EC.element_to_be_clickable((By.XPATH,
        "//input[@type='email'] | //input[contains(@placeholder,'email') or contains(@placeholder,'Email')]"
    )))

driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", email_input)
time.sleep(random.uniform(1.0, 2.0))
email_input.click()
time.sleep(0.5)

for char in email_address:
    email_input.send_keys(char)
    time.sleep(random.uniform(0.15, 0.35))

print("Email entered")
time.sleep(random.uniform(1.0, 2.0))

# -------- Checkbox --------
try:
    checkbox = wait.until(EC.element_to_be_clickable((By.ID, "checkVal")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
    time.sleep(random.uniform(0.8, 1.5))
    if not checkbox.is_selected():
        driver.execute_script("arguments[0].click();", checkbox)
    print("Checkbox checked")
except Exception as e:
    print(f"Checkbox not found: {e}")

time.sleep(random.uniform(1.5, 2.5))


# -------- Click Confirm Button --------
confirm_btn = wait.until(
    EC.element_to_be_clickable((By.XPATH, 
        "//button[@translate='schedule.confirm_applicant']"
    ))
)
driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", confirm_btn)
time.sleep(random.uniform(0.5, 1.0))
driver.execute_script("arguments[0].click();", confirm_btn)
print("✅ Confirm button clicked!")


# -------- Close Modal on New Page --------
print("Waiting for modal OK button...")
modal_ok = WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.XPATH,
        "//button[@translate='manage.ok']"
    ))
)
driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", modal_ok)
time.sleep(random.uniform(0.5, 1.0))
driver.execute_script("arguments[0].click();", modal_ok)
print("✅ Modal OK clicked!")


# -------- Get City from User --------
city = input("Enter city (Islamabad / Karachi): ").strip()

# -------- Click the QVC Center Dropdown --------
center_dropdown = wait.until(
    EC.element_to_be_clickable((By.XPATH,
        "//button[@name='selectedVsc']"
    ))
)
driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", center_dropdown)
time.sleep(random.uniform(0.5, 1.0))
driver.execute_script("arguments[0].click();", center_dropdown)
print("QVC Center dropdown opened")
time.sleep(random.uniform(0.5, 1.0))

# -------- Select the City --------
city_option = wait.until(
    EC.element_to_be_clickable((By.XPATH,
        f"//ul[contains(@class,'dropdown-menu')]//a[text()='{city}']"
    ))
)
driver.execute_script("arguments[0].click();", city_option)
print(f"✅ City '{city}' selected!")


# Inject interceptor BEFORE clicking city (so we catch any immediate API calls)
driver.execute_script("""
    window._apiResponse = null;
    window._originalFetch = window.fetch;
    window.fetch = function(...args) {
        return window._originalFetch(...args).then(response => {
            if (args[0] && args[0].toString().includes('getvscappointmentdates')) {
                response.clone().text().then(body => { window._apiResponse = body; });
            }
            return response;
        });
    };
""")

driver.execute_script("arguments[0].click();", city_option)
print(f"✅ City '{city}' selected!")
time.sleep(3)  # give page time to make the API call

# -------- Call API --------
print("\nFetching appointment dates...")
appointment_data = call_appointment_dates_api(driver)
# -------- Submit Page 2 --------
try:
    submit_btn2 = wait.until(
        EC.element_to_be_clickable((By.XPATH,
            "//button[contains(@class,'btn-brand-arrow') and not(@disabled)]"
        ))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn2)
    time.sleep(random.uniform(0.5, 1.0))
    from selenium.webdriver.common.action_chains import ActionChains
    ActionChains(driver).move_to_element(submit_btn2).pause(random.uniform(0.3, 0.6)).click().perform()
    print("✅ Page 2 submitted!")
except Exception as e:
    print(f"Submit button error: {e}")

time.sleep(3)
driver.save_screenshot("page2_after_submit.png")
print("✅ All done! Check page2_after_submit.png")