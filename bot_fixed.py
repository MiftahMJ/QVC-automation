import random
import time
import requests
import json
import base64
import re
import undetected_chromedriver as uc
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()
# ======== Email Config ========
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")   
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")


def send_email(subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

        print(f"✅ Email sent: {subject}")

    except Exception as e:
        print(f"❌ Email failed: {e}")

# ======== Helper Functions ========

def decrypt_response(encrypted_data):
    key = b"cvq@4202temoib!&"
    iv  = b"cvq@4202temoib!&"
    encrypted_bytes = base64.b64decode(encrypted_data)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)
    decrypted_str = decrypted.decode("utf-8")
    try:
        parsed = json.loads(decrypted_str)
        return json.dumps(parsed, indent=2)
    except:
        return decrypted_str


def get_visa_expiry_date(driver):
    """Extract the last booking date from the modal content"""
    try:
        modal_text = driver.execute_script("""
            let modal = document.querySelector('modal-content');
            return modal ? modal.innerText : null;
        """)
        print(f"Modal text: {modal_text}")

        if modal_text:
            # Extract "please choose the date on or before DD-Mon-YYYY"
            match = re.search(r'on or before (\d{2}-\w{3}-\d{4})', modal_text)
            if match:
                date_str = match.group(1)
                expiry = datetime.strptime(date_str, "%d-%b-%Y")
                print(f" Booking deadline: {expiry.strftime('%d %B %Y')}")
                return expiry
    except Exception as e:
        print(f" Could not extract expiry date: {e}")
    return None


def get_calendar_month_year(driver):
    """Get current month and year shown in calendar"""
    return driver.execute_script("""
        let spans = document.querySelectorAll('.navigation__title span');
        if (spans.length >= 2) {
            return {month: spans[0].innerText.trim(), year: spans[1].innerText.trim()};
        }
        return null;
    """)


def get_available_dates_current_month(driver, deadline_date=None):
    """Read available (enabled) dates from current calendar view"""
    data = driver.execute_script("""
        let available = [];
        let month = null;
        let year = null;

        try {
            let spans = document.querySelectorAll('.navigation__title span');
            if (spans.length >= 2) {
                month = spans[0].innerText.trim();
                year = spans[1].innerText.trim();
            }
        } catch(e) {}

        let days = document.querySelectorAll(
            '.datepicker__day:not(.is-disabled):not(.is-hidden) button:not([disabled])'
        );
        days.forEach(btn => {
            let day = btn.innerText.trim();
            if (day && day !== '') {
                available.push({day: day, month: month, year: year});
            }
        });

        return {month: month, year: year, available: available};
    """)

    if not data:
        return []

    month = data['month']
    year = data['year']
    available = []

    for d in data['available']:
        try:
            date_str = f"{d['day']} {month} {year}"
            date_obj = datetime.strptime(date_str, "%d %B %Y")
            # Filter by deadline if provided
            if deadline_date is None or date_obj <= deadline_date:
                available.append({
                    'date': date_str,
                    'datetime': date_obj
                })
        except Exception as e:
            print(f"  Date parse error: {e}")

    return available


def get_all_available_dates(driver, deadline_date=None):
    """Navigate through all months up to deadline and collect available dates"""
    all_available = []

    print("\n Scanning all months for available dates...")

    # Wait for calendar to be visible
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "datepicker__calendar")))
    time.sleep(2)

    max_months = 12  # safety limit
    for month_num in range(max_months):
        current = get_calendar_month_year(driver)
        if not current:
            break

        print(f"\n  Checking: {current['month']} {current['year']}")

        # Check if this month is past the deadline
        if deadline_date:
            try:
                month_start = datetime.strptime(f"1 {current['month']} {current['year']}", "%d %B %Y")
                if month_start > deadline_date:
                    print(f"  ⏹ Past deadline, stopping")
                    break
            except:
                pass

        # Get available dates in this month
        month_dates = get_available_dates_current_month(driver, deadline_date)
        if month_dates:
            print(f"   Found {len(month_dates)} available date(s):")
            for d in month_dates:
                print(f"     → {d['date']}")
            all_available.extend(month_dates)
        else:
            print(f"   No available dates")

        # Check if next button is disabled (no more months)
        next_disabled = driver.execute_script("""
            let btn = document.querySelector('.navigation__button.is-next');
            return btn ? btn.disabled : true;
        """)

        if next_disabled:
            print("  ⏹ No more months available")
            break

        # Check if next month would exceed deadline
        if deadline_date:
            try:
                current_dt = datetime.strptime(f"1 {current['month']} {current['year']}", "%d %B %Y")
                next_month = current_dt.month % 12 + 1
                next_year = current_dt.year + (1 if current_dt.month == 12 else 0)
                next_month_start = datetime(next_year, next_month, 1)
                if next_month_start > deadline_date:
                    print(f"  ⏹ Next month exceeds deadline, stopping")
                    break
            except:
                pass

        # Click next month button
        next_btn = driver.find_element(By.CSS_SELECTOR, ".navigation__button.is-next")
        driver.execute_script("arguments[0].click();", next_btn)
        print(f"  ➡ Moving to next month...")
        time.sleep(2)

    return all_available


def solve_captcha(driver, wait):
    print("Solving captcha...")
    time.sleep(2)

    img = wait.until(EC.presence_of_element_located((By.ID, "captchaImage")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", img)
    time.sleep(random.uniform(0.5, 1.0))

    src = img.get_attribute("src")
    base64_data = src.split(",", 1)[1]

    captcha_id = None
    for slot_attempt in range(5):
        response = requests.post("https://2captcha.com/in.php", data={
            "key": API_KEY,
            "method": "base64",
            "body": base64_data,
            "json": 1,
            "case": 1
        })
        result = response.json()
        if result["status"] == 1:
            captcha_id = result["request"]
            print(f"Captcha submitted (ID: {captcha_id}), waiting for solution...")
            break
        elif result["request"] == "ERROR_NO_SLOT_AVAILABLE":
            print(f" No slot available, retrying in 5s... ({slot_attempt + 1}/5)")
            time.sleep(5)
        else:
            raise Exception(f"2captcha submission failed: {result['request']}")

    if not captcha_id:
        raise Exception("2captcha has no slots available after 5 retries.")

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
            print(f" Captcha solved: {captcha_text}")
            break
        elif res["request"] == "CAPCHA_NOT_READY":
            print(f"  Not ready yet... ({attempt + 1}/24)")
        else:
            raise Exception(f"2captcha error: {res['request']}")

    if not captcha_text:
        raise Exception("Timed out waiting for captcha solution")

    img_after = driver.find_element(By.ID, "captchaImage")
    if img_after.get_attribute("src") != src:
        print("⚠️ Captcha changed while solving! Re-solving...")
        return solve_captcha(driver, wait)

    captcha_input = wait.until(
        EC.presence_of_element_located((By.XPATH,
            "//input[@placeholder='Enter Captcha'] | //input[@id='captchaCode'] | //input[@name='captcha']"
        ))
    )
    ActionChains(driver).move_to_element(captcha_input).pause(random.uniform(0.3, 0.7)).click().perform()
    time.sleep(0.5)

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
            time.sleep(random.uniform(
                (total_time / total_chars) * 0.6,
                (total_time / total_chars) * 1.4
            ))

    print(" Captcha fully entered")
    time.sleep(random.uniform(1.5, 2.5))

    print("Waiting for submit button to enable...")
    enabled_btn = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH,
            "//button[contains(@class,'btn-brand-arrow') and not(@disabled)]"
        ))
    )
    ActionChains(driver).move_to_element(enabled_btn).pause(random.uniform(0.3, 0.6)).click().perform()
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
            print(" Modal OK clicked")
            time.sleep(1)
            return
        except TimeoutException:
            continue
    print("No modal OK button found, continuing...")


# ======== Driver Setup ========

options = uc.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")

driver = uc.Chrome(options=options, version_main=145)
driver.maximize_window()

wait = WebDriverWait(driver, 20)
API_KEY = os.getenv("API_KEY")

# ======== Main ========

driver.get("https://www.qatarvisacenter.com/")

# Select Language
language_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@data-bs-toggle='dropdown']")))
driver.execute_script("arguments[0].click();", language_dropdown)
english_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'English')] | //li[contains(text(),'English')]")))
driver.execute_script("arguments[0].click();", english_option)

# Country Dropdown
country_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='-- Select Country --']")))
driver.execute_script("arguments[0].click();", country_dropdown)

# Select Pakistan
pakistan = wait.until(EC.element_to_be_clickable((By.XPATH, "//ul[contains(@class,'dropdown-menu')]//a[text()='Pakistan']")))
driver.execute_script("arguments[0].click();", pakistan)
print("Pakistan selected successfully")

# Book Appointment
book_appointment = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@class,'card-box') and contains(text(),'Book Appointment')]")))
driver.execute_script("arguments[0].click();", book_appointment)
print("Book Appointment clicked")

# Close Modal
close_modal = wait.until(EC.element_to_be_clickable((By.XPATH, "//img[@class='mod-close']")))
driver.execute_script("arguments[0].click();", close_modal)
print("Modal closed successfully")

# Passport Number
passport_number = input("Enter Passport Number: ")
passport_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Passport Number']")))
passport_input.send_keys(passport_number)
print("Passport number entered")

# Visa Number
visa_number = input("Enter Visa Number: ")
visa_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Visa Number']")))
visa_input.send_keys(visa_number)
print("Visa number entered")

# Solve Captcha & Submit
solve_captcha(driver, wait)

# Handle modals — extract visa expiry from first modal before closing
print("Checking for visa expiry info in modal...")
time.sleep(2)
deadline_date = get_visa_expiry_date(driver)
click_modal_ok(driver)

wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
time.sleep(2)
click_modal_ok(driver)

print("Waiting for page 2 to fully load...")
time.sleep(5)
print(f"Current URL: {driver.current_url}")
wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
time.sleep(3)

# Phone
phone_number = input("Enter phone number: ")
try:
    phone_input = wait.until(EC.element_to_be_clickable((By.ID, "phone")))
except:
    phone_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='tel'] | //input[contains(@placeholder,'hone')]")))
driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", phone_input)
time.sleep(random.uniform(1.0, 2.0))
phone_input.click()
for char in phone_number:
    phone_input.send_keys(char)
    time.sleep(random.uniform(0.15, 0.35))
print("Phone entered")
time.sleep(random.uniform(1.0, 2.0))

# Email
email_address = input("Enter email address: ")
try:
    email_input = wait.until(EC.element_to_be_clickable((By.ID, "email")))
except:
    email_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='email'] | //input[contains(@placeholder,'mail')]")))
driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", email_input)
time.sleep(random.uniform(1.0, 2.0))
email_input.click()
for char in email_address:
    email_input.send_keys(char)
    time.sleep(random.uniform(0.15, 0.35))
print("Email entered")
time.sleep(random.uniform(1.0, 2.0))

# Checkbox
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

# Confirm Button
confirm_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@translate='schedule.confirm_applicant']")))
driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", confirm_btn)
time.sleep(random.uniform(0.5, 1.0))
driver.execute_script("arguments[0].click();", confirm_btn)
print(" Confirm button clicked!")

# Modal OK on new page
print("Waiting for modal OK button...")
modal_ok = WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.XPATH, "//button[@translate='manage.ok']"))
)
driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", modal_ok)
time.sleep(random.uniform(0.5, 1.0))
driver.execute_script("arguments[0].click();", modal_ok)
print(" Modal OK clicked!")

# Wait for slot details page
wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
time.sleep(3)

# City Selection
city = input("Enter city (Islamabad / Karachi): ").strip()
center_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@name='selectedVsc']")))
driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", center_dropdown)
time.sleep(random.uniform(0.5, 1.0))
driver.execute_script("arguments[0].click();", center_dropdown)
print("QVC Center dropdown opened")
time.sleep(random.uniform(0.5, 1.0))

city_option = wait.until(EC.element_to_be_clickable((By.XPATH,
    f"//ul[contains(@class,'dropdown-menu')]//a[text()='{city}']"
)))
driver.execute_script("arguments[0].click();", city_option)
print(f" City '{city}' selected!")
time.sleep(3)

# Print deadline info
if deadline_date:
    print(f"\n Booking deadline: {deadline_date.strftime('%d %B %Y')}")
else:
    print("\n No deadline found, scanning all available months")

# Scan all months and collect available dates up to deadline
all_available = get_all_available_dates(driver, deadline_date)

# Final summary
# Final summary + Email
print(f"\n{'='*50}")
print(f"📅 AVAILABLE APPOINTMENT DATES")
print(f"{'='*50}")

if all_available:
    for d in all_available:
        print(f"  ✅ {d['date']}")
    print(f"\nTotal: {len(all_available)} available slot(s)")

    # Build email body
    dates_html = "".join([f"<li>✅ {d['date']}</li>" for d in all_available])
    deadline_str = deadline_date.strftime('%d %B %Y') if deadline_date else "N/A"

    body = f"""
    <html><body>
    <h2> Appointment Slots Available!</h2>
    <p><b>Passport:</b> {passport_number}</p>
    <p><b>Visa:</b> {visa_number}</p>
    <p><b>City:</b> {city}</p>
    <p><b>Booking Deadline:</b> {deadline_str}</p>
    <h3>Available Dates:</h3>
    <ul>{dates_html}</ul>
    <p>Please book your appointment as soon as possible.</p>
    </body></html>
    """
    send_email(
        subject=f" Qatar Visa Appointment Available — {city}",
        body=body
    )

else:
    print("  No available dates found before visa expiry")

    deadline_str = deadline_date.strftime('%d %B %Y') if deadline_date else "N/A"
    body = f"""
    <html><body>
    <h2> No Appointment Slots Available</h2>
    <p><b>Passport:</b> {passport_number}</p>
    <p><b>Visa:</b> {visa_number}</p>
    <p><b>City:</b> {city}</p>
    <p><b>Booking Deadline:</b> {deadline_str}</p>
    <p>No available appointment slots were found before the visa expiry deadline.</p>
    <p>Please check again later.</p>
    </body></html>
    """
    send_email(
        subject=f" No Qatar Visa Appointment Available — {city}",
        body=body
    )

print(f"{'='*50}")