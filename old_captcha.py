# def solve_captcha(driver, wait):
#     """Extract base64 captcha from page, solve via 2captcha, and type it human-like over ~6 seconds"""
#     print("Solving captcha...")

#     # -------- Grab captcha image base64 --------
#     img = driver.find_element(By.ID, "captchaImage")
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
#     for attempt in range(24):  # ~2 min timeout
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

#     # -------- Find captcha input --------
#     captcha_input = wait.until(
#         EC.presence_of_element_located((By.XPATH,
#             "//input[@placeholder='Enter Captcha'] | //input[@id='captchaCode'] | //input[@name='captcha']"
#         ))
#     )
#     captcha_input.click()
#     time.sleep(0.5)

#     # -------- Type each letter with human-like delay over ~6 seconds --------
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
#     time.sleep(1)

#     return captcha_text