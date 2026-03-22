import requests
import time
import base64
import re
from bs4 import BeautifulSoup

API_KEY = "5573fd8190654adf4f131e6c35c2de62"

# --- Step 1: Extract base64 from the img tag ---
html = '''<img id="captchaImage" src="data:image/jpeg;base64,R0lGODlh...">'''  # paste full HTML here

soup = BeautifulSoup(html, "html.parser")
img_tag = soup.find("img", {"id": "captchaImage"})
src = img_tag["src"]

# Strip the data:image/...;base64, prefix
base64_data = src.split(",", 1)[1]

# --- Step 2: Submit to 2captcha ---
submit_url = "https://2captcha.com/in.php"

response = requests.post(submit_url, data={
    "key": API_KEY,
    "method": "base64",
    "body": base64_data,
    "json": 1
})

result = response.json()
if result["status"] != 1:
    raise Exception(f"Submission failed: {result['request']}")

captcha_id = result["request"]
print(f"Submitted. Captcha ID: {captcha_id}")

# --- Step 3: Poll for result ---
result_url = "https://2captcha.com/res.php"

print("Waiting for solution", end="", flush=True)
for _ in range(24):  # try for ~2 minutes
    time.sleep(5)
    print(".", end="", flush=True)

    res = requests.get(result_url, params={
        "key": API_KEY,
        "action": "get",
        "id": captcha_id,
        "json": 1
    }).json()

    if res["status"] == 1:
        print(f"\n✅ Solved: {res['request']}")
        captcha_text = res["request"]
        break
    elif res["request"] == "CAPCHA_NOT_READY":
        continue
    else:
        raise Exception(f"Error: {res['request']}")
else:
    raise Exception("Timed out waiting for captcha solution")

# --- Step 4: Use the result ---
print(f"Captcha answer: {captcha_text}")
# Now submit captcha_text in your form field