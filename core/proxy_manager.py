import time
import itertools
from concurrent.futures import ThreadPoolExecutor
import requests
from urllib.parse import urlparse
from ui.colors import GREEN, RED, WHITE, EKL
from core.settings_manager import load_settings
from core.locale_data import get_locale, get_timezone, get_language

FALLBACK_IP_INFO = {"country": "United States", "countryCode": "US", "timezone": "America/New_York"}


# Parse proxy string into structured dict (supports ip:port, ip:port:user:pass, and URL formats)
def parse_proxy(proxy_str):
    proxy_str = proxy_str.strip()
    username = None
    password = None

    if "://" not in proxy_str:
        parts = proxy_str.split(":")
        if len(parts) == 2:
            ip, port = parts
            if not port.isdigit():
                return None
            proxy_url = f"http://{ip}:{port}"
        elif len(parts) >= 4:
            ip = parts[0]
            port = parts[1]
            if not port.isdigit():
                return None
            username = parts[2]
            password = ":".join(parts[3:])
            proxy_url = f"http://{ip}:{port}"
        else:
            return None
    else:
        try:
            parsed = urlparse(proxy_str)
            username = parsed.username
            password = parsed.password
            netloc = parsed.netloc
            if '@' in netloc:
                netloc = netloc.split('@')[-1]
            proxy_url = f"{parsed.scheme or 'http'}://{netloc}"
        except Exception:
            return None

    return {
        "http": proxy_url,
        "https": proxy_url,
        "username": username,
        "password": password
    }


# Fetch geolocation info for a proxy using ip-api.com
def get_ip_info(proxies=None, retries=1):
    for attempt in range(retries + 1):
        try:
            r = requests.get("http://ip-api.com/json/", proxies=proxies, timeout=10)
            if r.status_code == 200:
                data = r.json()
                return {
                    "country": data.get("country", "Unknown"),
                    "countryCode": data.get("countryCode", "US"),
                    "timezone": data.get("timezone", "Unknown")
                }
        except Exception:
            pass
        if attempt < retries:
            time.sleep(1)
    return None


# Build complete proxy data dict with locale, timezone, and language info
def build_proxy_data(proxy_dict):
    req_proxies = None
    if proxy_dict:
        username = proxy_dict.get("username")
        password = proxy_dict.get("password")
        raw_url = proxy_dict.get("http", "")
        if username and password:
            if "://" in raw_url:
                proto, host = raw_url.split("://", 1)
                auth_url = f"{proto}://{username}:{password}@{host}"
            else:
                auth_url = f"http://{username}:{password}@{raw_url}"
            req_proxies = {"http": auth_url, "https": auth_url}
        else:
            req_proxies = proxy_dict

    info = get_ip_info(req_proxies)
    if info is None:
        print(f"{RED} Warning: Could not determine location for proxy. Using default US settings.")
        info = FALLBACK_IP_INFO
    cc = info["countryCode"]
    return {
        "proxy": proxy_dict,
        "country": info["country"],
        "country_code": cc,
        "locale": get_locale(cc),
        "timezone": get_timezone(cc),
        "language": get_language(cc),
        "ip_timezone": info["timezone"]
    }


# Parse and validate a single proxy input string
def _input_single_proxy_internal(proxy_str, proxy_list):
    parsed = parse_proxy(proxy_str)
    if parsed:
        data = build_proxy_data(parsed)
        proxy_list.append(data)
    else:
        print(f"{RED} Invalid proxy format!")


# Prompt user for multiple proxy inputs (max 40)
def _input_multiple_proxies_internal(prompt_label, proxy_list):
    try:
        cnt_str = input(f" {GREEN}[{RED}●{GREEN}] How many proxies? (Max 40) {EKL} ").strip()
        if not cnt_str or not cnt_str.isdigit():
            print(f"{RED} Invalid number!")
            return
        cnt = int(cnt_str)
        if cnt > 40:
            print(f"{RED} Maximum 40 proxies allowed! You entered {cnt}.")
            return
        if cnt < 1:
            print(f"{RED} Invalid number!")
            return
        for i in range(cnt):
            while True:
                p_str = input(f" {WHITE}[{RED}●{WHITE}] Enter {prompt_label} [{i+1}/{cnt}] {EKL} ").strip()
                if not p_str:
                    continue
                parsed = parse_proxy(p_str)
                if parsed:
                    data = build_proxy_data(parsed)
                    proxy_list.append(data)
                    break
                else:
                    print(f"{RED} Invalid proxy format!")
    except KeyboardInterrupt:
        raise
    except Exception:
        print(f"{RED} Invalid input!")


# Format proxy config display label for the UI
def _format_proxy_config_label(proxy_list, source="User"):
    if not proxy_list:
        return "Direct"
    if len(proxy_list) == 1:
        p = proxy_list[0]
        if source == "Settings":
            return f"{p['country']} (Settings)"
        else:
            return f"{p['country']} (IP: {p['ip_timezone']})"
    countries = set(p['country'] for p in proxy_list)
    suffix = " (Settings)" if source == "Settings" else ""
    return f"{len(proxy_list)} Proxies ({len(countries)} Countries){suffix}"


# Main proxy input handler - loads from settings or prompts user
def get_proxy_list(config_state=None, render_callback=None):
    settings = load_settings()
    proxy_cfg = settings.get("proxy_settings", {})
    ask_proxy = proxy_cfg.get("ask_for_proxy", True)
    def_proxy = proxy_cfg.get("default_proxy", "")
    prompt_label = "Proxy"
    config_key = "proxy"

    proxy_list = []

    # Load proxies from settings if configured
    if def_proxy:
        parsed_proxies = []
        if isinstance(def_proxy, list):
            if len(def_proxy) > 40:
                print(f"{RED} Warning: Maximum 40 proxies allowed in settings. Using first 40.")
                def_proxy = def_proxy[:40]
            for p in def_proxy:
                parsed = parse_proxy(p)
                if parsed:
                    parsed_proxies.append(parsed)
                else:
                    print(f"{RED} Warning: Skipping invalid proxy in settings: {p}")
        elif def_proxy.strip():
            parsed = parse_proxy(def_proxy)
            if parsed:
                parsed_proxies.append(parsed)
            else:
                print(f"{RED} Warning: Skipping invalid proxy in settings: {def_proxy}")
        if parsed_proxies:
            with ThreadPoolExecutor(max_workers=min(len(parsed_proxies), 5)) as executor:
                proxy_list.extend(executor.map(build_proxy_data, parsed_proxies))

    if not ask_proxy:
        if config_state is not None:
            config_state[config_key] = _format_proxy_config_label(proxy_list, "Settings")
        return proxy_list

    if render_callback:
        render_callback()

    proxy_input = input(f" {GREEN}[{RED}●{GREEN}] Enter {prompt_label} (or 'y' for multiple) [Enter to Skip] {EKL} ").strip()

    if proxy_input.lower() == 'y':
        _input_multiple_proxies_internal(prompt_label, proxy_list)
    elif proxy_input:
        _input_single_proxy_internal(proxy_input, proxy_list)

    if config_state is not None:
        if not proxy_list:
            no_proxy_data = get_no_proxy_data()
            config_state[config_key] = f"Direct (IP: {no_proxy_data['country']})"
        else:
            config_state[config_key] = _format_proxy_config_label(proxy_list, "User")

    return proxy_list


# Create infinite cycling iterator for round-robin proxy rotation
def create_proxy_cycle(proxy_list):
    if proxy_list:
        return itertools.cycle(proxy_list)
    return None


# Get locale data for direct connection (no proxy)
def get_no_proxy_data():
    info = get_ip_info(None)
    if info is None:
        info = FALLBACK_IP_INFO
    cc = info["countryCode"]
    return {
        "proxy": None,
        "country": info["country"],
        "country_code": cc,
        "locale": get_locale(cc),
        "timezone": get_timezone(cc),
        "language": get_language(cc),
        "ip_timezone": info["timezone"]
    }


# Convert proxy_data dict into requests-compatible proxy format with auth
def format_proxy_for_requests(proxy_data):
    if not proxy_data:
        return None
    proxy_url = proxy_data.get("proxy")
    if not proxy_url:
        return None
    if isinstance(proxy_url, dict):
        username = proxy_url.get("username")
        password = proxy_url.get("password")
        raw_url = proxy_url.get("http", "")
        if username and password:
            from urllib.parse import quote
            safe_user = quote(username, safe="")
            safe_pass = quote(password, safe="")
            if "://" in raw_url:
                proto, host = raw_url.split("://", 1)
                auth_url = f"{proto}://{safe_user}:{safe_pass}@{host}"
            else:
                auth_url = f"http://{safe_user}:{safe_pass}@{raw_url}"
            return {"http": auth_url, "https": auth_url}
        return {"http": raw_url, "https": proxy_url.get("https", raw_url)}
    return {"http": proxy_url, "https": proxy_url}
