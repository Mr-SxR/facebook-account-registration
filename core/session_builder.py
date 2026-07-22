import random
from curl_cffi import requests
from core.user_agent import (
    get_android_browser_ua, get_iphone_app_ua, get_android_app_ua,
    get_kaios_ua, get_windows_phone_ua, get_blackberry_ua,
)


# Create HTTP session with TLS fingerprint matching the device type
def create_http_session(device_type, proxy_dict=None):
    base_type = device_type.split("_")[0] if "_" in device_type else device_type

    impersonate_ver = None
    if base_type in ("Android", "AndroidApp"):
        impersonate_ver = "chrome107"
    elif base_type == "IphoneApp":
        impersonate_ver = "safari15_3"

    if impersonate_ver:
        session = requests.Session(impersonate=impersonate_ver)
    else:
        session = requests.Session()

    if proxy_dict:
        session.proxies.update(proxy_dict)

    return session


# Build headers and user-agent context based on device type and locale
def build_request_context(device_type, browser_type, locale):
    base_type = device_type.split("_")[0] if "_" in device_type else device_type

    if base_type == "KaiOS":
        return _build_kaios_context(locale)
    elif base_type == "WindowsPhone":
        return _build_windows_phone_context(locale)
    elif base_type == "BlackBerry":
        return _build_blackberry_context(locale)
    elif base_type == "IphoneApp":
        return _build_iphone_app_context(locale)
    elif base_type == "AndroidApp":
        return _build_android_app_context(locale)
    else:
        return _build_android_context(locale)


# Build Android browser request context (Android 4-8, Chrome 30-70)
def _build_android_context(locale):
    ua, model, android_ver = get_android_browser_ua()

    base_headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language": f"{locale},en-US,en;q=0.9",
        "upgrade-insecure-requests": "1",
        "user-agent": ua,
    }

    return {"ua": ua, "base_headers": base_headers, "model": model, "android_ver": android_ver}


# Build KaiOS feature phone request context
def _build_kaios_context(locale):
    ua = get_kaios_ua()

    base_headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "accept-language": f"{locale},en;q=0.9",
        "upgrade-insecure-requests": "1",
        "user-agent": ua,
    }

    return {"ua": ua, "base_headers": base_headers, "model": None, "android_ver": None}


# Build Windows Phone IE Mobile request context
def _build_windows_phone_context(locale):
    ua = get_windows_phone_ua()

    base_headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "accept-language": f"{locale},en;q=0.9",
        "upgrade-insecure-requests": "1",
        "user-agent": ua,
    }

    return {"ua": ua, "base_headers": base_headers, "model": None, "android_ver": None}


# Build BlackBerry 10 WebKit request context
def _build_blackberry_context(locale):
    ua = get_blackberry_ua()

    base_headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "accept-language": f"{locale},en;q=0.9",
        "upgrade-insecure-requests": "1",
        "user-agent": ua,
    }

    return {"ua": ua, "base_headers": base_headers, "model": None, "android_ver": None}


# Build iPhone Facebook App request context (iOS 6-9)
def _build_iphone_app_context(locale):
    ua = get_iphone_app_ua()

    base_headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "accept-language": f"{locale},en;q=0.9",
        "user-agent": ua,
    }

    return {"ua": ua, "base_headers": base_headers, "model": None, "android_ver": None}


# Build Android Facebook App request context (Android 4-6, FB Lite/Messenger)
def _build_android_app_context(locale):
    ua, model, android_ver = get_android_app_ua()

    base_headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language": f"{locale},en;q=0.9",
        "upgrade-insecure-requests": "1",
        "user-agent": ua,
    }

    return {"ua": ua, "base_headers": base_headers, "model": model, "android_ver": android_ver}


# Set initial session cookies to mimic a real device visit
def setup_session_cookies(session, device_type):
    base_type = device_type.split("_")[0] if "_" in device_type else device_type
    if base_type in ("Android", "AndroidApp"):
        screen_res = random.choice(["320x480", "480x800", "540x960", "800x480", "854x480", "960x540", "720x1280", "1280x720", "1080x1920"])
        session.cookies.update({"m_pixel_ratio": "1", "wd": screen_res})
