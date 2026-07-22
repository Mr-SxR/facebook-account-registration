import json
import time
import random
import string
import re
import os
from faker import Faker

from ui.colors import GREEN, RED, WHITE, YELLOW, ORANGE, CYAN
from core.number_manager import remove_number
from core.proxy_manager import format_proxy_for_requests
from core.session_builder import create_http_session, build_request_context, setup_session_cookies

fake = Faker()


# Generate a random identity with name, birthday, gender and password
def generate_identity():
    gender = random.choice(['male', 'female'])

    if gender == 'male':
        first_name = fake.first_name_male()
        last_name = fake.last_name_male()
        sex_value = '2'
    else:
        first_name = fake.first_name_female()
        last_name = fake.last_name_female()
        sex_value = '1'

    dob = fake.date_of_birth(minimum_age=18, maximum_age=40)
    password = ''.join(random.choices(
        string.ascii_letters + string.digits + '!@#$%^&*',
        k=random.randint(8, 14)
    ))

    return {
        "first_name": first_name,
        "last_name": last_name,
        "sex_value": sex_value,
        "b_day": str(dob.day),
        "b_month": str(dob.month),
        "b_year": str(dob.year),
        "password": password,
    }


# Extract first regex capture group from text, returns None if not found
def _search(pattern, text):
    m = re.search(pattern, text)
    return m.group(1) if m else None


# Core worker - handles the full registration flow for a single phone number
def create_worker(wid, phone_number, proxy_data, config, counter):
    device_type = config.get("device_type", "Android")
    browser_type = config.get("browser_type", "Default")
    server = config.get("server", "m.facebook.com")

    proxy_dict = format_proxy_for_requests(proxy_data)
    locale = proxy_data.get("locale", "en_US") if proxy_data else "en_US"

    try:
        session = create_http_session(device_type, proxy_dict)
        setup_session_cookies(session, device_type)

        ctx = build_request_context(device_type, browser_type, locale)

        base_headers = ctx["base_headers"]

        # Step 1: GET registration page and extract hidden tokens
        response_1 = session.get(f'https://{server}/reg', headers=base_headers).text

        ccp = _search(r'name="ccp" value="([^"]+)"', response_1)
        lsd = _search(r'name="lsd" value="([^"]+)"', response_1)
        jazoest = _search(r'name="jazoest" value="([^"]+)"', response_1)
        reg_instance = _search(r'name="reg_instance" value="([^"]+)"', response_1)
        reg_impression_id = _search(r'name="reg_impression_id" value="([^"]+)"', response_1)
        ns_value = _search(r'name="ns" value="([^"]+)"', response_1)
        logger_id = _search(r'name="logger_id" value="([^"]+)"', response_1)
        encrypted_token = _search(r'"encrypted"\s*:\s*"([^"]+)"', response_1)
        fb_dtsg = _search(r'"dtsg"\s*:\s*\{\s*"token"\s*:\s*"([^"]+)"', response_1)
        privacy_token = _search(r'privacy_mutation_token=([^&]+)', response_1)

        required = [ccp, lsd, jazoest, reg_instance, reg_impression_id,
                    ns_value, logger_id, encrypted_token, fb_dtsg, privacy_token]
        if not all(required):
            counter.update("error", number=phone_number, message="Failed to Parse Tokens", color=ORANGE)
            return

        privacy_token = privacy_token.replace('%3D', '=')

        identity = generate_identity()

        # Step 2: POST registration with extracted tokens and generated identity
        post_headers = dict(base_headers)
        post_headers.update({
            'accept': '*/*',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': f'https://{server}',
            'referer': f'https://{server}/reg?soft=hjk',
            'x-fb-lsd': lsd,
            'x-requested-with': 'XMLHttpRequest',
            'x-response-format': 'JSONStream',
        })
        post_headers.pop('upgrade-insecure-requests', None)
        post_headers.pop('sec-fetch-user', None)

        params = {
            'privacy_mutation_token': privacy_token,
            'multi_step_form': '1',
            'skip_suma': '0',
            'shouldForceMTouch': '1',
        }

        data = {
            'ccp': ccp,
            'reg_instance': reg_instance,
            'submission_request': 'true',
            'helper': '',
            'reg_impression_id': reg_impression_id,
            'ns': ns_value,
            'zero_header_af_client': '',
            'app_id': '',
            'logger_id': logger_id,
            'field_names[0]': 'firstname',
            'firstname': identity["first_name"],
            'lastname': identity["last_name"],
            'field_names[1]': 'birthday_wrapper',
            'birthday_day': identity["b_day"],
            'birthday_month': identity["b_month"],
            'birthday_year': identity["b_year"],
            'age_step_input': '',
            'did_use_age': 'false',
            'field_names[2]': 'reg_email__',
            'reg_email__': phone_number,
            'field_names[3]': 'sex',
            'sex': identity["sex_value"],
            'preferred_pronoun': '',
            'custom_gender': '',
            'field_names[4]': 'reg_passwd__',
            'name_suggest_elig': 'false',
            'was_shown_name_suggestions': 'false',
            'did_use_suggested_name': 'false',
            'use_custom_gender': 'false',
            'guid': '',
            'pre_form_step': '',
            'encpass': f'#PWD_BROWSER:0:{int(time.time())}:{identity["password"]}',
            'fb_dtsg': fb_dtsg,
            'jazoest': jazoest,
            'lsd': lsd,
            '__dyn': '1Z3pawlEnwm8_Bg9ppoW5UdE4a2i5U4e0C86u7E39x60zU3ex608ewk9E4W0pKq0FE6S0x81vohw73wGwcq1GwqU2YwbK0oi0zE1jU1soG0hi0Lo6-0Co1kU1UU3jwGwbu',
            '__csr': '',
            '__hsdp': '',
            '__hblp': '',
            '__sjsp': '',
            '__req': 'r',
            '__fmt': '1',
            '__a': encrypted_token,
            '__user': '0',
        }

        response_2 = session.post(f'https://{server}/reg/submit/', params=params, headers=post_headers, data=data)

        cookies = response_2.cookies.get_dict()
        response_text = response_2.text
        name = f"{identity['first_name']} {identity['last_name']}"

        # Check for auth cookies to confirm successful registration
        if cookies and any(k in cookies for k in ("c_user", "xs")):
            uid = cookies.get("c_user", "")
            cookie_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
            counter.update(
                "success", number=phone_number,
                message=f" Name : {name} | Birthday : {identity['b_day']}/{identity['b_month']}/{identity['b_year']} \n [SxR-NV] {uid} | {identity['password']} | {cookie_str}",
                color=GREEN,
            )
            remove_number(phone_number)

            # Save successful account credentials to output file
            os.makedirs("output", exist_ok=True)
            with open("output/success.txt", "a", encoding="utf-8") as f:
                f.write(f"{uid}|{identity['password']}|{cookie_str}\n")

        else:
            # Parse error response for debugging
            debug_msg = "Unknown Error"
            try:
                err_data = json.loads(response_text.split("for (;;);")[1]) if "for (;;);" in response_text else json.loads(response_text)
                debug_msg = str(err_data)[:150]
            except Exception:
                debug_msg = response_text.replace('\n', ' ')[:300]

            counter.update(
                "failed", number=phone_number,
                message=f"Failed | Debug: {debug_msg}...",
                color=YELLOW,
            )

    except Exception as e:
        err = str(e)
        if "proxy" in err.lower():
            counter.update("error", number=phone_number, message="Proxy Error", color=RED)
        elif "timeout" in err.lower() or "timed out" in err.lower():
            counter.update("error", number=phone_number, message="Timeout", color=RED)
        else:
            counter.update("error", number=phone_number, message=err[:50], color=RED)
