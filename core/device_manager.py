from ui.colors import GREEN, RED, WHITE, CYAN, EKL, LINE
from core.settings_manager import load_settings

SERVER_MAP = {
    "1": "m.facebook.com",
    "2": "mbasic.facebook.com",
    "3": "touch.facebook.com",
    "4": "free.facebook.com",
    "5": "m.alpha.facebook.com",
    "6": "m.beta.facebook.com",
    "7": "x.facebook.com",
    "8": "limited.facebook.com",
    "9": "iphone.facebook.com",
    "10": "d.facebook.com",
}


# Prompt user to select device type or use default from settings
def select_device(config_state, render_callback):
    settings = load_settings()
    device_set = settings.get("device_settings", {})
    ask_device = device_set.get("ask_for_device", True)
    def_device = str(device_set.get("default_device", "none")).strip().lower()

    device_type = "Android"

    device_map = {
        "1": "Android",
        "2": "KaiOS",
        "3": "WindowsPhone",
        "4": "BlackBerry",
        "5": "IphoneApp",
        "6": "AndroidApp",
    }

    if def_device in device_map:
        device_type = device_map[def_device]
    elif ask_device:
        if render_callback:
            render_callback()
        print(f" {GREEN}[{RED}01{GREEN}] Android Browser {WHITE}(Android 4-8, Chrome 30-70)")
        print(f" {GREEN}[{RED}02{GREEN}] KaiOS {WHITE}(Feature Phone)")
        print(f" {GREEN}[{RED}03{GREEN}] Windows Phone {WHITE}(IE Mobile)")
        print(f" {GREEN}[{RED}04{GREEN}] BlackBerry {WHITE}(BB10)")
        print(f" {GREEN}[{RED}05{GREEN}] iPhone App {WHITE}(iOS 6-9, Facebook App)")
        print(f" {GREEN}[{RED}06{GREEN}] Android App {WHITE}(Android 4-6, FB Lite/Messenger)")
        print(f"{LINE}")
        dev_choice = input(f" {GREEN}[{RED}●{GREEN}] Select Device {EKL} ").strip()
        device_type = device_map.get(dev_choice, "Android")

    config_state["device"] = device_type
    if render_callback:
        render_callback()
    return device_type


# Select browser type (fixed for all legacy device types)
def select_browser(device_type, config_state, render_callback):
    browser_type = "Default"
    config_state["browser"] = browser_type
    if render_callback:
        render_callback()
    return browser_type


# Prompt user to select server domain or use default from settings
def select_server(config_state, render_callback):
    settings = load_settings()
    server_set = settings.get("server_settings", {})
    raw_id = server_set.get("tools_server_id", "none")
    str_id = str(raw_id).strip().lower()

    server_domain = "m.facebook.com"

    if str_id == "none" or str_id == "":
        if render_callback:
            render_callback()
        for idx, domain in SERVER_MAP.items():
            print(f" {GREEN}[{RED}{idx.zfill(2)}{GREEN}] {WHITE}{domain}")
        print(f"{LINE}")

        while True:
            choice = input(f" {GREEN}[{RED}●{GREEN}] Select Server (1-{len(SERVER_MAP)}) {EKL} ").strip()
            if choice in SERVER_MAP:
                server_domain = SERVER_MAP[choice]
                break
            if not choice:
                break
            print(f" {RED}Invalid! Enter 1-{len(SERVER_MAP)}")
    else:
        server_domain = SERVER_MAP.get(str_id, "m.facebook.com")

    config_state["server"] = server_domain
    if render_callback:
        render_callback()
    return server_domain
