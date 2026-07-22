[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=22&pause=1000&color=76e033&center=true&vCenter=true&width=700&lines=NV+Create+%7C+Mr-SxR;Facebook+Automated+Registration)](https://github.com/Mr-SxR/Nov-Create)

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Open Source](https://img.shields.io/badge/Open%20Source-✓-76e033?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-0078D6?style=for-the-badge&logo=windows&logoColor=white)

</div>

---

## 📌 About

**Facebook Account Registration** is a multi-threaded Python tool for automating the **No Verify (NV)** registration workflow using legacy mobile device profiles.

The tool completes the Facebook registration process up to the **verification step**, but **does not submit the SMS/email verification code**. As a result, it creates **NV (unverified) accounts**, not fully verified Facebook accounts.

> 🔧 Built with **curl_cffi** for TLS fingerprinting and **Faker** for realistic identity generation.

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| 🔄 **Legacy UA Engine** | Generates verified working user-agents from Android 4-8, KaiOS, WP, BB, iOS App |
| 🌐 **Proxy Support** | HTTP/HTTPS/SOCKS5 with auto-geolocation and locale detection |
| 🔒 **TLS Fingerprint** | curl_cffi impersonation (Chrome 107 / Safari 15.3) per device type |
| 📱 **6 Device Profiles** | Android Browser, KaiOS, Windows Phone, BlackBerry, iPhone App, Android App |
| 🖥️ **10 Server Endpoints** | m.facebook, mbasic, touch, free, alpha, beta, x, limited, iphone, d |
| 📂 **Excel + TXT Input** | Reads phone numbers from Number_List.txt or .xlsx files |
| ⚙️ **JSON Config** | Pre-configure device, browser, server, proxy, and worker defaults |
| 💾 **Auto Save** | Successful accounts saved to `output/success.txt` with cookies |

---

## ⚙️ Installation

```bash
git clone https://github.com/Mr-SxR/facebook-account-registration.git
cd facebook-account-registration
```

### ▶️ Run

```bash
git pull
pip install -r requirements.txt
python main.py
```

---

## 📋 Requirements

- Python
- Windows or Linux (Termux supported)
- Internet connection
- Phone numbers (one per line in `Number_List.txt` or `.xlsx` file)
- Proxy list (optional but recommended)

---

## ▶️ How It Works

```
Start (python main.py)
       ↓
Select Device Type → Select Server → Load Proxies → Set Threads
       ↓
Load Phone Numbers (TXT / Excel)
       ↓
For each number (multi-threaded):
       ↓
Generate Legacy User-Agent → Build Session with TLS Fingerprint
       ↓
GET /reg → Extract Hidden Tokens (lsd, jazoest, ccp, fb_dtsg...)
       ↓
Generate Identity (Name, DOB, Password)
       ↓
POST /reg/submit/ → Check Response Cookies
       ↓
Success (c_user cookie found) → Save to output/success.txt
```

---

## 🗂️ Project Structure

```
facebook-account-registration/
├── main.py                    # Entry point, orchestrates the full workflow
├── setting.json               # Default configuration file
├── Number_List.txt            # Phone number input (one per line)
├── requirements.txt           # Python dependencies
│
├── core/
│   ├── user_agent.py          # Legacy UA generation engine (6 device types)
│   ├── session_builder.py     # HTTP session with TLS fingerprint + headers
│   ├── device_manager.py      # Device selection menu and server picker
│   ├── proxy_manager.py       # Proxy parsing, geolocation, rotation
│   ├── number_manager.py      # Phone number loading (TXT/Excel)
│   ├── worker_manager.py      # Thread count configuration
│   ├── settings_manager.py    # JSON settings loader
│   ├── locale_data.py         # Country-to-locale/timezone mappings
│   └── counter.py             # Thread-safe result counter
│
├── automation/
│   └── create_task.py         # Core registration worker logic
│
├── ui/
│   ├── logo.py                # Terminal ASCII banner
│   ├── colors.py              # ANSI color codes
│   └── display.py             # Thread-safe terminal output
│
└── output/
    └── success.txt            # Auto-generated on successful registration
```

---

## 🔧 Configuration

All defaults can be set in `setting.json` to skip interactive prompts:

```json
{
    "device_settings": {
        "ask_for_device": true,
        "default_device": "none"
    },
    "server_settings": {
        "tools_server_id": "none"
    },
    "proxy_settings": {
        "ask_for_proxy": true,
        "default_proxy": ""
    },
    "worker_settings": {
        "ask_for_workers": true,
        "default_workers": 30,
        "max_safe_workers": 200
    },
    "file_input_settings": {
        "always_use_txt": false,
        "use_multiple_excel_files": false
    }
}
```

> 💡 Set `"ask_for_device": false` with `"default_device": "1"` to auto-select Android Browser on every run.

---

## 🕵️ Device Profiles

All device profiles generate user-agents verified to receive the classic HTML registration page with extractable form tokens.

| # | Profile | User-Agent Type | Why It Works |
|---|---------|----------------|--------------|
| 1 | **Android Browser** | Android 4.4-8.1, Chrome 30-70 | Old OS + browser, legacy HTML served |
| 2 | **KaiOS** | Nokia/Alcatel/JioPhone, Firefox 48 | Feature phone, no modern JS support |
| 3 | **Windows Phone** | Lumia/HTC, IE Mobile 11 | IE can never run React/modern frameworks |
| 4 | **BlackBerry** | BB10 WebKit 537.35 | Ancient WebKit, legacy page forced |
| 5 | **iPhone App** | iOS 6-9, FBAN/FBIOS format | Old Facebook app format with carrier info |
| 6 | **Android App** | Android 4-6, Dalvik + FBAN/EMA | Facebook Lite/Messenger old format |

> 💡 Android Browser is the recommended default. It has the largest model pool and most realistic fingerprints.

---

## 🌐 Server Options

| # | Domain | Notes |
|---|--------|-------|
| 1 | m.facebook.com | Standard mobile (recommended) |
| 2 | mbasic.facebook.com | Basic HTML version |
| 3 | touch.facebook.com | Touch-optimized mobile |
| 4 | free.facebook.com | Free basics / zero-rated |
| 5 | m.alpha.facebook.com | Alpha testing endpoint |
| 6 | m.beta.facebook.com | Beta testing endpoint |
| 7 | x.facebook.com | Lightweight variant |
| 8 | limited.facebook.com | Limited connectivity version |
| 9 | iphone.facebook.com | iOS-specific endpoint |
| 10 | d.facebook.com | Feature phone / basic |

---

## 🌐 Proxy Format

| Format | Example |
|--------|---------|
| `ip:port` | `192.168.1.1:8080` |
| `ip:port:user:pass` | `192.168.1.1:8080:admin:secret` |
| `protocol://ip:port` | `socks5://192.168.1.1:1080` |
| `protocol://user:pass@ip:port` | `http://admin:secret@192.168.1.1:8080` |

> 🔐 Proxies are auto-detected for geolocation. The locale and timezone are set based on the proxy's country.

---

## 📄 Output

Successful registrations are saved to `output/success.txt`:

```
uid|password|cookie_string
```

Each line contains the Facebook user ID, generated password, and full session cookies.

---

## ⚠️ Disclaimer

This tool is provided for **educational and research purposes only**. The author is not responsible for any misuse. Users are solely responsible for ensuring compliance with all applicable laws and platform terms of service in their jurisdiction.

---

## 📬 Contact

[![Facebook](https://img.shields.io/badge/Facebook-1877F2?style=for-the-badge&logo=facebook&logoColor=white)](https://www.facebook.com/sifathub)
[![WhatsApp](https://img.shields.io/badge/WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)](https://wa.me/+8801858094178)
[![Telegram](https://img.shields.io/badge/Telegram-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/sifathub)


> Feel free to reach out for any questions, issues, or custom requests.

---

<div align="center">

*Developed & Open-Sourced by **[Mr-SxR](https://github.com/Mr-SxR)** — Speciality & Reliability*

</div>

