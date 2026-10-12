# REAL SERVICE FIX V3: SMS/number assignment based service resolver
import requests
import time
import json
import os
import firebase_admin
from firebase_admin import credentials, firestore
import uuid
import threading
import random
import re
import unicodedata
import html
import pyotp
from collections import Counter 
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from datetime import datetime 
from urllib.parse import urljoin

# ==========================================
# Configuration (Token & Owner ID)
# ==========================================
TOKEN = "8428540473:AAHfClv9xjmnu-ZALwHdOZMPsTKlTedMEeQ"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
FILE_URL = f"https://api.telegram.org/file/bot{TOKEN}/"

OWNER_ID = 8666796208
BOT_USERNAME = "@myoto879_bot"
DB_FILE = "bot_data.json"

# ==========================================
# Premium Emoji Database
# ==========================================
PEM = {
    "ok": '<tg-emoji emoji-id="5352694861990501856">✅</tg-emoji>',
    "no": '<tg-emoji emoji-id="5420130255174145507">❌</tg-emoji>',
    "warn": '<tg-emoji emoji-id="5336944168944047463">⚠️</tg-emoji>',
    "admin": '<tg-emoji emoji-id="5353032893096567467">📊</tg-emoji>',
    "user": '<tg-emoji emoji-id="5352861489541714456">👤</tg-emoji>',
    "file": '<tg-emoji emoji-id="5352721946054268944">📁</tg-emoji>',
    "rocket": '<tg-emoji emoji-id="5352597830089347330">🚀</tg-emoji>',
    "graph": '<tg-emoji emoji-id="5352877703043258544">📊</tg-emoji>',
    "money": '<tg-emoji emoji-id="5348469219761626211">💸</tg-emoji>',
    "gift": '<tg-emoji emoji-id="5420396762189831222">🎁</tg-emoji>',
    "msg": '<tg-emoji emoji-id="5337302974806922068">💬</tg-emoji>',
    "gear": '<tg-emoji emoji-id="5420155432272438703">⚙️</tg-emoji>',
    "link": '<tg-emoji emoji-id="5420517437885943844">🔗</tg-emoji>',
    "trash": '<tg-emoji emoji-id="5422557736330106570">🗑</tg-emoji>',
    "upload": '<tg-emoji emoji-id="5353001161878182134">📤</tg-emoji>',
    "world": '<tg-emoji emoji-id="5336972142066047577">🌐</tg-emoji>',
    "lock": '<tg-emoji emoji-id="5353022963132174959">🔐</tg-emoji>',
    "phone": '<tg-emoji emoji-id="5337132498965010628">📱</tg-emoji>',
    "num": '<tg-emoji emoji-id="5352862640592949843">🔢</tg-emoji>',
    "pin": '<tg-emoji emoji-id="5352922460897452503">📍</tg-emoji>',
    "star": '<tg-emoji emoji-id="5352552689983067014">✨</tg-emoji>',
    "hi": '<tg-emoji emoji-id="5353027129250453493">👋</tg-emoji>'
}

GLOBAL_BODY_EMOJIS = {
    "➖": "5870818207383686839", "🚫": "5334807341109908955", "😒": "5334763399299506604",
    "🖥": "5334880948259427772", "🌐": "5334590977837403844", "🌟": "5337102391244263212",
    "🕓": "5336983442125001376", "⌛": "5337172996211648018", "💬": "5337302974806922068",
    "🔐": "5337255927735163754", "🍏": "5337132498965010628", "❔": "5336850036145823599",
    "⚠️": "5336944168944047463", "🔥": "5337267511261960341", "💸": "5348469219761626211",
    "🥚": "5348390922507817684", "👨‍⚖": "5334763399299506604", "🐁": "5348494358205207761",
    "🧻": "5348486915026884464", "⚗": "5346311574221000149", "🛴": "5348075478634766440",
    "📊": "5353032893096567467", "🔢": "5352862640592949843", "👤": "5352861489541714456",
    "📁": "5352721946054268944", "🚀": "5352597830089347330", "💎": "5352838545826420397",
    "📍": "5352922460897452503", "👋": "5353027129250453493", "✅": "5352694861990501856",
    "1️⃣": "5352651766288652742", "2️⃣": "5355186458418257716", "3️⃣": "5352867219028091093",
    "4️⃣": "5352566657216714037", "5️⃣": "5353086880835474989", "6️⃣": "5354859211975071385",
    "7️⃣": "5352859127309707652", "8️⃣": "5352957533600389988", "9️⃣": "5353060913463204207",
    "🔤": "5352727417842606016", "📣": "5352980533150259581", "📤": "5353001161878182134",
    "✨": "5352552689983067014", "🔹": "5352638632278660622", "🎙": "5355102594886833928",
    "💴": "5352985330628730418", "📅": "5352585194295564660", "📴": "5352974971167611327",
    "✏️": "5395444784611480792", "📱": "5337132498965010628", "🔗": "5420517437885943844",
    "❌": "5420130255174145507", "⚙️": "5420155432272438703", "🫂": "5420145051336485498",
    "➕": "5420323438508155202", "🗑": "5422557736330106570", "🎁": "5420396762189831222",
    "➤": "5420618897898381296", "🏢": "5420156334215565595", "💳": "5190899075968441286",
    "📝": "5192739271886282680", "🛡": "5190447043545438788", "🤝": "5192805934073685937",
    "💰": "5190576863226933563", "👀": "5190645917711114179", "🕹": "5193100774988617665",
    "🟢": "5192812028632274956", "🧪": "5190781475468915802", "🎨": "5190751148704833975",
    "📂": "5257969839313526622", "🌍": "5780471598922337683", "📌": "5318986077455795572",
    "📢": "5789428375261023681", "🆔": "5352862640592949843", "📈": "5352877703043258544",
    "🔔": "5352980533150259581", "🏦": "5348469219761626211", "🧾": "5192739271886282680",
    "👨‍⚖️": "5334763399299506604", "🔍": "5463352748751753567",
    "🔑": "5197288647275071607"
}

DEFAULT_CUSTOM_MESSAGES = {
    "start": {"text": "╔═══════════╗\n       📊 NUMBER BOT\n╚═══════════╝\n🚀 Welcome to Number & OTP Service\n━━━━━━━━━━━━\n✅ Choose an option below\nto continue using the bot.\n━━━━━━━━━━━━\n💎 Premium OTP Service", "buttons": []},
    "get_number": {"text": f"{PEM['pin']} Select a service:", "buttons": []},
    "select_country": {"text": f"📌 Select a country for {{service}}:", "buttons": []}, 
    "search_number": {"text": "╔═══════════╗\n     🔍 <b>SEARCH NUMBER</b>\n╚═══════════╝\n✅ Enter 3 to 9 digits  \nto search for a number.\n━━━━━━━━━━━━━\n📝 Example:\n➥ 880\n➥ 9227373\n━━━━━━━━━━━━━\n🔍 Fast Number Lookup System", "buttons": []},
    "traffic": {"text": f"{PEM['graph']} <b>Traffic Overview</b>\n\n{PEM['ok']} Available Numbers: {{avail}}\n{PEM['rocket']} Assigned Numbers: {{assigned}}", "buttons": []},
    "refer": {"text": f"➖➖➖➖➖➖➖\n« {PEM['gift']} REFER & EARN »\n➖➖➖➖➖➖➖\n{PEM['link']} YOUR LINK:\n<code>{{ref_link}}</code>\n➖➖➖➖➖➖➖\n{PEM['user']} TOTAL REFERS: <b>{{total_ref}}</b>\n➖➖➖➖➖➖➖\n{PEM['money']} PER REFER: <b>{{ref_reward}} TK</b>\n➖➖➖➖➖➖➖", "buttons": []},
    "withdrawal": {"text": "➖➖➖➖➖➖➖\n《 😒 WITHDRAWAL 》\n➖➖➖➖➖➖➖\n👋 Total Otp: {total_otp}\n➖➖➖➖➖➖➖\n🫂 Total Reffer :{total_ref}\n➖➖➖➖➖➖➖\n📅 BALANCE: {bal}৳\n➖➖➖➖➖➖➖\n🔐 MINIMUM: {min_w} ৳\n➖➖➖➖➖➖➖\nSELECT METHOD:", "buttons": []},
    "support": {"text": f"{PEM['msg']} Contact us for any help:", "buttons": []}
}

# ==========================================
# Firebase Setup
# ==========================================
firebase_credentials_json = r"""
{
  "type": "service_account",
  "project_id": "dmc",
  "private_key_id": "2722f2e02a730af953f30c96de78e7149",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDSdgpy9TTC1Gs6\n7Lp4FLDDNRpF2Inv1J10erMYz6TUjcxg740dhE4hKs8qpJWEv5azgCEAFXWeR1/W\n5WyinlEKkO8/5F36cIyk+9JUWDG9rs7uojvZ5X/pFKtGsW7gEHwj0bYUXqifg2Fi\nGDCASo9nSdjOlSy1di6sQP/u01LkiSqJ6yhzJmK+E3Hzt2M8Nfwqz1qmMKdKucXL\nXyWTV2qr9qnusEd7Eq2VG3SHIWzf3c7vOo2E9/FPL/CydlYkRRA/RgGPOd1zZlqh\nddsIZvyN1aiyoRjn4vtmniNQX4dFkyAeZ7b9vCEbtF31M71gvw14Eh\nZppvIza/AgMBAAECggEASq+bC6qau50YJIQHtD9bbxq0JR8v7A0eh0xXrDFbxBZB\n9hBsmpHuC/UeKXrYmJBI0ZBhpZ7362BW0XL/N0JJbh9618iZ1RsFvjKjNE1L8Y1M\nYADwjmXUG4m7Mk4bE6al9ywfmmDxJBJCh8YfyBcthrD9IGptwEOdUoGKkV0q6HBj\n636jwz/sRjhSQvAMZpRCA1dl/SDXE3eOhmzNsG+YoY7x1Qr8zjrq2m45Ijw3B/29\n9OdO3XwMQYHR3EaK0EwH3LM8kc9gUMjkgDSdXhHTrS9f28nB8WIJ7DE+2xUvt3us\nlAWmFO2EKyp57p3b4nM1wFvxbzUhvPg+bVyo41YOIQKBgQDxN4kC2+Po9Zff9o0+\nIDvw/fXgN96d9ZIpY3SnI1lhQiC1XF5NqJfFm7m/WUGkjGeAVWgcv4bwccf6PQDr\nDDBFRQHGoowLjpsOxk9LIy8YS6caTKjaE5P2YGLciq+1Elffv3CyluXMLr0Mgpj0\n//5pg7YxeCqxwrwjcWKkZkvM8QKBgQDfW/nIUKaBa7SYMbuVIAUtOcG4dot+N51k\nAQad3G85u//9DCQ7CfMbQQRp2anVBr4nNYqWJM+SNkSw25TMsBLak/7NpGTLkAuq\nJ9w2J7vwjb9TWkbi4uCC6UMcVq9KbDjnjFvXioJJmIAuMy5iDIz+TgZI3HDb/V28\niDCJ16v+rwKBgQDRLkjZutjFEB2ZshTAWHHCxmlv/ONH9kq/K6lgu+3pws/clvKM\nw/SCAE6vWnbrfHrRNr9nlswtPW6fWkGuk85Uc8hbemCaMRvUTzM6RJO1rP2HeA1B\nuJKqqOFywa4oB3U+6qSPqv4y+CEndSWx6UG2POtFsSDNMMO4tL5HNRLs8QKBgBS3\n1FiHWpqAohTH8C1p9fD2/YgdvtyrTfcbvUBhVRPW42zWdnnfd2RcyIsE/KLc6EB8\nz+kTawmV7RM2mvvNjUInHih3Cj5zkxFqdxuy3dT3YPrbUd3zy315I5d6VvIhTbn0\npAQ/PcyTz7f5WWEQ5vcjx6N0hydwvgQh4da3YaXTAoGBALX1ox7CEs3VOCaVQjiI\nffZThUHFjMs7M6AwSqsWKfYCTEteMClKzq+wLhuoAvoY4cSp+SRTij51hUeCpvrR\nEdRw6QgaJaRGIIHv0BInF8SLqkIwOIrsIfRFYLgfNSg+Kxh3D7tU1h3ee/XqQ97eKw3asYNNg7va1Jl\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@dmemdnc.iam.gserviceaccount.com",
  "client_id": "11655245407",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40dmemdnc.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
"""

try:
    cred_dict = json.loads(firebase_credentials_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Firebase Connected! (Full Sync Enabled)")
except Exception as e:
    print(f"❌ Firebase Error: {e}")
    db = None

bot_settings = {
    "admins": [OWNER_ID],
    "panels": [], 
    "fw_groups": [], 
    "otp_link": "https://t.me/your_otp_group",
    "otp_channel_url": "",
    "otp_extra_buttons": [],
    "withdraw_on": True,
    "min_withdraw": 30.0,
    "otp_reward": 0.1,
    "refer_reward": 0.2,
    "cooldown": 10,
    "num_req": 3,
    "num_share": 1, 
    "support_link": "https://t.me/your_support",
    "w_methods": ["bKash", "Nagad"],
    "w_group": "", 
    
    "fj_on": False,
    "fj_channels": [], 
    "stex_keys": [], 
    "voltx_keys": [],
    "search_countries": [],
    "stex_services": {},
    "voltx_services": {},
    "premium_flags": {
        "1": {"char": "🇺🇸", "iso": "US", "name": "United States", "id": "5913463998522592692"},
        "880": {"char": "🇧🇩", "iso": "BD", "name": "Bangladesh", "id": "5911365056594973179"},
        "91": {"char": "🇮🇳", "iso": "IN", "name": "India", "id": "5913754823643107921"},
        "92": {"char": "🇵🇰", "iso": "PK", "name": "Pakistan", "id": "5913705895375672082"},
        "44": {"char": "🇬🇧", "iso": "GB", "name": "United Kingdom", "id": "5913443365499703513"}
    },
    "premium_apps": {
        "FACEBOOK": {"char": "🚫", "id": "5334807341109908955", "name": "Facebook"},
        "WHATSAPP": {"char": "🚫", "id": "5334759662677957452", "name": "WhatsApp"}
    },
    "custom_messages": DEFAULT_CUSTOM_MESSAGES.copy(),
    # CUSTOM OTP TEST CONFIGURATION: stores only synthetic/test-message schedules.
    "custom_otp_services": [],
    "custom_otp_service_digits": {},
    "custom_otp_configs": [],
    "custom_otp_running": False
}

FS_KEYS = [
    "admins", "panels", "fw_groups", "otp_link", "otp_channel_url", "otp_extra_buttons", "withdraw_on", 
    "min_withdraw", "otp_reward", "refer_reward", "cooldown", 
    "num_req", "num_share", "support_link", "w_methods", "w_group", "stex_keys", "voltx_keys", "search_countries", "stex_services", "voltx_services",
    "fj_on", "fj_channels"
]

number_batches = {}
used_numbers_list = []
stex_assigned_numbers = {} 
voltx_assigned_numbers = {}
STEX_BASE_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tness/@public/api"
VOLTX_BASE_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tnevs/@public/api"
total_uploaded_stats = 0
total_assigned_stats = 0
processed_otps = set() 
recent_traffic = []
user_banned_cache = {}

# Active HTTP sessions for Auto Captcha Panels
panel_sessions = {}

# 🌟 sAjaxSource (AJAX/DataTable) এবং Fallback HTML Parser Helper Function
def fetch_cpt_panel_cdrs(p, session, check_url):
    res = session.get(check_url, timeout=15)
    html_text = res.text
    
    # সেশন শেষ হয়েছে বা লগইন পেজে রিডাইরেক্ট করেছে কি না তা চেক করা
    if "login" in html_text.lower() or "signin" in html_text.lower() or any(x in html_text for x in ["Sign in to your account", "Please sign in", "Welcome back!"]):
        raise Exception("Session expired")
        
    soup = BeautifulSoup(html_text, 'html.parser')
    s_ajax_source = ""
    for script in soup.find_all("script"):
        script_text = script.string or ""
        match = re.search(r'sAjaxSource":\s*"([^"]+)"', script_text)
        if match:
            s_ajax_source = match.group(1)
            break
            
    results = []
    
    n_col_name = p.get("num_col_name", "number").lower()
    m_col_name = p.get("msg_col_name", "message").lower()
    n_idx = int(p.get("num_col_idx", 1)) - 1 if p.get("num_col_idx") else 1
    m_idx = int(p.get("msg_col_idx", 2)) - 1 if p.get("msg_col_idx") else 2

    # ৫.১ যদি sAjaxSource AJAX লিংক পাওয়া যায়
    if s_ajax_source:
        baseUrl = p.get("login_url", "").split("/client")[0].split("/login")[0].strip()
        if not baseUrl.startswith("http"):
            baseUrl = "http://" + baseUrl
            
        full_ajax_url = ""
        if s_ajax_source.startswith("http"):
            full_ajax_url = s_ajax_source
        elif s_ajax_source.startswith("/"):
            full_ajax_url = f"{baseUrl}{s_ajax_source}"
        else:
            last_slash_idx = check_url.rfind("/")
            current_dir = check_url[:last_slash_idx]
            full_ajax_url = f"{current_dir}/{s_ajax_source}"

        if "iDisplayLength" not in full_ajax_url:
            # 250 এর জায়গায় 10000 করে দেওয়া হলো যাতে সব মেসেজ ফেচ করতে পারে
            query_params = "sEcho=1&iColumns=7&iDisplayStart=0&iDisplayLength=10000&sSearch=&iSortingCols=1&iSortCol_0=0&sSortDir_0=desc"
            divider = "&" if "?" in full_ajax_url else "?"
            full_ajax_url += f"{divider}{query_params}"

        ajax_headers = {
            "Referer": check_url,
            "X-Requested-With": "XMLHttpRequest"
        }
        
        ajax_res = session.get(full_ajax_url, headers=ajax_headers, timeout=15)
        data_dict = ajax_res.json()
        rows = data_dict.get("aaData", [])
        for row_val in rows:
            if not isinstance(row_val, list):
                continue
                
            if len(row_val) < max(n_idx, m_idx) + 1:
                continue
                
            num_val = row_val[n_idx] if (0 <= n_idx < len(row_val)) else row_val[2]
            msg_val = row_val[m_idx] if (0 <= m_idx < len(row_val)) else row_val[4]
            
            clean_num = re.sub(r'\D', '', str(num_val))
            if clean_num and 5 <= len(clean_num) <= 18:
                otp = extract_otp_code(msg_val)
                if otp and len(msg_val) > 4:
                    results.append({"number": clean_num, "message": msg_val, "otp": otp})
                    
    else:
        # ৫.২ ডাইরেক্ট HTML টেবিল থেকে রিড করার ব্যাকআপ লজিক
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            if not rows: continue
            
            final_n_idx = n_idx
            final_m_idx = m_idx
            
            header_cells = rows[0].find_all(['th', 'td'])
            for i, cell in enumerate(header_cells):
                c_text = cell.get_text(strip=True).lower()
                if n_col_name in c_text: final_n_idx = i
                if m_col_name in c_text: final_m_idx = i

            for row in rows:
                cols = row.find_all(['td', 'th'])
                if all(c.name == 'th' for c in cols): continue
                
                if len(cols) > max(final_n_idx, final_m_idx):
                    num_text = cols[final_n_idx].get_text(separator=" ", strip=True)
                    msg_text = cols[final_m_idx].get_text(separator=" ", strip=True)
                    
                    clean_num = re.sub(r'\D', '', num_text)
                    if clean_num and 5 <= len(clean_num) <= 18:
                        otp = extract_otp_code(msg_text)
                        if otp and len(msg_text) > 4:
                            results.append({"number": clean_num, "message": msg_text, "otp": otp})
                            
    return results, html_text

# Track active number sessions to expire them automatically
user_active_sessions = {}

# Persistent ownership map for manually uploaded/local numbers.  A local number
# may be shared with more than one user (according to num_share), so each
# number keeps a list of owners.  This survives removal of the number from
# number_batches after its share limit is reached and lets the OTP listener
# resolve the correct user/service later.
local_assigned_numbers = {}

def load_db():
    global bot_settings, number_batches, used_numbers_list, total_uploaded_stats, total_assigned_stats, recent_traffic, stex_assigned_numbers, voltx_assigned_numbers, local_assigned_numbers
    if db:
        try:
            doc = db.collection('settings').document('bot_config').get()
            if doc.exists:
                fs_data = doc.to_dict()
                for k in FS_KEYS:
                    if k in fs_data:
                        bot_settings[k] = fs_data[k]
                print("✅ Config Loaded from Firestore!")
            else:
                fs_data = {k: bot_settings[k] for k in FS_KEYS}
                db.collection('settings').document('bot_config').set(fs_data)
                print("✅ Firestore Config Initialized!")
        except Exception as e:
            print(f"❌ Error loading from Firestore: {e}")

    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding='utf-8') as f:
                data = json.load(f)
                saved_settings = data.get("bot_settings", {})
                for key, val in saved_settings.items():
                    if key not in FS_KEYS:
                        if key == "custom_messages":
                            for m_key, m_val in val.items():
                                bot_settings["custom_messages"][m_key] = m_val
                        else:
                            bot_settings[key] = val
                        
                for m_key, m_val in DEFAULT_CUSTOM_MESSAGES.items():
                    if m_key not in bot_settings["custom_messages"]:
                        bot_settings["custom_messages"][m_key] = m_val
                        
                number_batches = data.get("number_batches", {})
                used_numbers_list = data.get("used_numbers_list", [])
                total_uploaded_stats = data.get("total_uploaded_stats", 0)
                total_assigned_stats = data.get("total_assigned_stats", 0)
                recent_traffic = data.get("recent_traffic", [])
                stex_assigned_numbers = data.get("stex_assigned_numbers", {})
                voltx_assigned_numbers = data.get("voltx_assigned_numbers", {})
                local_assigned_numbers = data.get("local_assigned_numbers", {})
            print("✅ Local Stock/UI DB Loaded Successfully!")
        except Exception as e:
            print(f"❌ Error loading local DB: {e}")

def save_local_db():
    local_data = {
        "bot_settings": {k: v for k, v in bot_settings.items() if k not in FS_KEYS},
        "number_batches": number_batches,
        "used_numbers_list": used_numbers_list,
        "total_uploaded_stats": total_uploaded_stats,
        "total_assigned_stats": total_assigned_stats,
        "recent_traffic": recent_traffic,
        "stex_assigned_numbers": stex_assigned_numbers,
        "voltx_assigned_numbers": voltx_assigned_numbers,
        "local_assigned_numbers": local_assigned_numbers
    }
    try:
        with open(DB_FILE, "w", encoding='utf-8') as f:
            json.dump(local_data, f, indent=4)
    except Exception as e:
        pass

def _sync_fs():
    if not db: return
    fs_data = {k: bot_settings[k] for k in FS_KEYS if k in bot_settings}
    try:
        db.collection('settings').document('bot_config').set(fs_data)
    except: pass

def save_db():
    save_local_db()
    # 🌟 Firestore Save Threading: মেইন বটকে স্লো না করার জন্য ব্যাকগ্রাউন্ডে সেভ হবে
    threading.Thread(target=_sync_fs, daemon=True).start()

load_db()

user_states = {}
# Per-user number prefix filter. A prefix is matched from the START of uploaded numbers.
user_prefixes = {}
# Keeps the last rendered Number page so Prefix/no-stock Back always returns there.
number_page_snapshots = {}
temp_data = {}
user_cooldowns = {}
pending_withdrawals = {}
WITHDRAWALS_LOCAL_FILE = "withdrawals_local.json"
LOCAL_BANNED_FILE = "banned_users.json"
local_banned_users = set()
custom_otp_stop_event = threading.Event()
custom_otp_worker_thread = None

# ==========================================
# Withdrawal / Ban Persistence Helpers
# ==========================================
def _load_local_withdrawals():
    global pending_withdrawals
    try:
        if os.path.exists(WITHDRAWALS_LOCAL_FILE):
            with open(WITHDRAWALS_LOCAL_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            pending_withdrawals = {str(k): v for k, v in data.items() if str(v.get("status", "pending")).lower() == "pending"}
    except Exception as e:
        print(f"[WITHDRAWAL] Local load error: {e}")

def _save_local_withdrawals():
    try:
        data = {}
        # Keep pending requests plus a small local history.
        if os.path.exists(WITHDRAWALS_LOCAL_FILE):
            try:
                with open(WITHDRAWALS_LOCAL_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}
        for rid, item in pending_withdrawals.items():
            row = dict(item)
            row.setdefault("status", "pending")
            data[str(rid)] = row
        with open(WITHDRAWALS_LOCAL_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[WITHDRAWAL] Local save error: {e}")

def _load_local_bans():
    global local_banned_users
    try:
        if os.path.exists(LOCAL_BANNED_FILE):
            with open(LOCAL_BANNED_FILE, "r", encoding="utf-8") as f:
                local_banned_users = {str(x) for x in json.load(f)}
    except Exception as e:
        print(f"[BAN] Local load error: {e}")

def _save_local_bans():
    try:
        with open(LOCAL_BANNED_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted(local_banned_users), f, indent=2)
    except Exception as e:
        print(f"[BAN] Local save error: {e}")

_load_local_withdrawals()
_load_local_bans()

# ==========================================
# Telegram API & Helpers
# ==========================================
tg_session = requests.Session() # 🌟 Keep-Alive Connection (Makes bot 10x faster)

# 🎨 Global Inline Button Color Table
# Only the visual style is changed; button text/callback/URL and layout stay untouched.
BUTTON_COLOR_TABLE = ("primary", "success", "danger")

def _apply_button_color_table(reply_markup):
    """Apply varied Telegram inline-button styles without changing button behavior."""
    if not isinstance(reply_markup, dict):
        return reply_markup
    inline_keyboard = reply_markup.get("inline_keyboard")
    if not isinstance(inline_keyboard, list):
        # Reply keyboards do not support Telegram's inline style field; leave them unchanged.
        return reply_markup

    # Preserve an explicitly requested style.  The previous global color pass
    # overwrote every button style, which made state buttons such as START/STOP
    # stay green even after their callback changed the state.
    markup = {k: v for k, v in reply_markup.items() if k != "inline_keyboard"}
    new_keyboard = []
    color_index = 0
    for row in inline_keyboard:
        new_row = []
        if isinstance(row, list):
            for button in row:
                if isinstance(button, dict):
                    b = button.copy()
                    if "style" not in b:
                        b["style"] = BUTTON_COLOR_TABLE[color_index % len(BUTTON_COLOR_TABLE)]
                    color_index += 1
                    new_row.append(b)
                else:
                    new_row.append(button)
        else:
            new_row = row
        new_keyboard.append(new_row)
    markup["inline_keyboard"] = new_keyboard
    return markup

def api_call(method, payload=None):
    url = f"{BASE_URL}/{method}"
    try:
        # Keep the Telegram API response intact so admin actions can show the real error.
        res = tg_session.post(url, json=payload, timeout=15)
        try:
            data = res.json()
        except Exception:
            data = {"ok": False, "error_code": res.status_code, "description": res.text[:500]}
        if not data.get("ok", False):
            print(f"[TELEGRAM API] {method} failed: {data}")
        return data
    except Exception as e:
        print(f"[TELEGRAM API] {method} exception: {e}")
        return {"ok": False, "description": str(e)}

def send_message(chat_id, text, reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode, "disable_web_page_preview": True}
    if reply_markup: payload["reply_markup"] = _apply_button_color_table(reply_markup)
    return api_call("sendMessage", payload)

def send_photo(chat_id, photo_url_or_file_id, caption="", reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "photo": photo_url_or_file_id, "caption": caption, "parse_mode": parse_mode}
    if reply_markup: payload["reply_markup"] = _apply_button_color_table(reply_markup)
    return api_call("sendPhoto", payload)

def edit_message(chat_id, message_id, text, reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": parse_mode, "disable_web_page_preview": True}
    if reply_markup: payload["reply_markup"] = _apply_button_color_table(reply_markup)
    return api_call("editMessageText", payload)

def delete_message(chat_id, message_id):
    return api_call("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

def answer_callback(callback_id, text="", show_alert=False):
    api_call("answerCallbackQuery", {"callback_query_id": callback_id, "text": text, "show_alert": show_alert})

def send_document(chat_id, filename, text_content):
    url = f"{BASE_URL}/sendDocument"
    files = {'document': (filename, text_content)}
    data = {'chat_id': chat_id}
    try: requests.post(url, data=data, files=files)
    except: pass

# 🌟 Local User List to completely remove Firebase Read Costs!
all_known_users = set()

def sync_users_list():
    global all_known_users
    try:
        if os.path.exists("users_list.json"):
            with open("users_list.json", "r") as f:
                all_known_users = set(json.load(f))
        if not all_known_users and db:
            for doc in db.collection('users').select([]).stream():
                all_known_users.add(doc.id)
            with open("users_list.json", "w") as f:
                json.dump(list(all_known_users), f)
    except: pass

threading.Thread(target=sync_users_list, daemon=True).start()

def _save_users_list():
    try:
        with open("users_list.json", "w") as f:
            json.dump(list(all_known_users), f)
    except: pass

def register_user_local(uid):
    uid_str = str(uid)
    if uid_str not in all_known_users:
        all_known_users.add(uid_str)
        # 🌟 Non-blocking background save (Prevents lag)
        threading.Thread(target=_save_users_list, daemon=True).start()

def broadcast_copymessage(from_chat_id, msg_id):
    success = 0
    failed = 0
    users = list(all_known_users)
    
    # 🌟 Dedicated Connection Pool for Broadcast (Fixes Port Exhaustion & Network Lag)
    b_session = requests.Session()
    url = f"{BASE_URL}/copyMessage"
    
    for user_id in users:
        payload = {"chat_id": user_id, "from_chat_id": from_chat_id, "message_id": msg_id}
        try:
            res = b_session.post(url, json=payload, timeout=5).json()
            if res.get("ok"): success += 1
            else: failed += 1
        except:
            failed += 1
        time.sleep(0.035) # Safe speed (28 msgs/sec) to prevent Telegram Ban
        
    send_message(from_chat_id, render_body_text(f"📢 <b>Broadcast Completed!</b>\n✅ Success: {success}\n❌ Failed: {failed}\n👥 Total Sent: {len(users)}"))

def render_body_text(text):
    if not text: return str(text)
    parts = re.split(r'(<tg-emoji.*?</tg-emoji>)', str(text))
    for i in range(len(parts)):
        if not parts[i].startswith('<tg-emoji'):
            for normal_emj, prem_id in GLOBAL_BODY_EMOJIS.items():
                if normal_emj in parts[i]:
                    parts[i] = parts[i].replace(normal_emj, f'<tg-emoji emoji-id="{prem_id}">{normal_emj}</tg-emoji>')
    return "".join(parts)

def extract_premium_html(msg):
    text = msg.get("text", msg.get("caption", ""))
    entities = msg.get("entities", msg.get("caption_entities", []))
    if not entities: return text
    try:
        b_text = text.encode('utf-16-le')
        c_entities = [e for e in entities if e.get("type") == "custom_emoji"]
        c_entities.sort(key=lambda x: x["offset"], reverse=True)
        for ent in c_entities:
            offset = ent["offset"] * 2
            length = ent["length"] * 2
            eid = ent["custom_emoji_id"]
            emoji_char = b_text[offset:offset+length].decode('utf-16-le')
            html_tag = f'<tg-emoji emoji-id="{eid}">{emoji_char}</tg-emoji>'
            replacement = html_tag.encode('utf-16-le')
            b_text = b_text[:offset] + replacement + b_text[offset+length:]
        return b_text.decode('utf-16-le')
    except Exception as e:
        return text 

def get_custom_emoji_id_from_message(msg):
    """Return the first Telegram custom emoji ID from a message, if present."""
    try:
        entities = msg.get("entities", msg.get("caption_entities", [])) or []
        for ent in entities:
            if ent.get("type") == "custom_emoji" and ent.get("custom_emoji_id"):
                return str(ent["custom_emoji_id"])
    except Exception:
        pass
    return None

def get_flag_info_from_num(num):
    clean = num.replace("+", "").replace(" ", "")
    sorted_codes = sorted(bot_settings.get("premium_flags", {}).keys(), key=len, reverse=True)
    for code in sorted_codes:
        if clean.startswith(code):
            data = bot_settings["premium_flags"][code]
            return data["char"], data.get("iso", "XX"), data.get("id")
    return "🌍", "XX", None

# Comprehensive fallback for ISO country detection from international phone numbers.
# Existing premium_flags always take priority; this only prevents XX/🌍 when the
# country is not yet present in the premium flag configuration.
PHONE_PREFIX_TO_ISO = {
    "880":"BD","213":"DZ","49":"DE","7":"RU","77":"KZ","76":"KZ",
    "1":"US","1242":"BS","1246":"BB","1264":"AI","1268":"AG","1284":"VG",
    "1340":"VI","1345":"KY","1441":"BM","1473":"GD","1649":"TC","1658":"SX",
    "1664":"MS","1670":"MP","1671":"GU","1684":"AS","1721":"SX","1758":"LC",
    "1767":"DM","1784":"VC","1787":"PR","1809":"DO","1829":"DO","1849":"DO",
    "1868":"TT","1869":"KN","1876":"JM","20":"EG","211":"SS","212":"MA",
    "216":"TN","218":"LY","220":"GM","221":"SN","222":"MR","223":"ML","224":"GN",
    "225":"CI","226":"BF","227":"NE","228":"TG","229":"BJ","230":"MU","231":"LR",
    "232":"SL","233":"GH","234":"NG","235":"TD","236":"CF","237":"CM","238":"CV",
    "239":"ST","240":"GQ","241":"GA","242":"CG","243":"CD","244":"AO","245":"GW",
    "246":"IO","248":"SC","249":"SD","250":"RW","251":"ET","252":"SO","253":"DJ",
    "254":"KE","255":"TZ","256":"UG","257":"BI","258":"MZ","260":"ZM","261":"MG",
    "262":"RE","263":"ZW","264":"NA","265":"MW","266":"LS","267":"BW","268":"SZ",
    "269":"KM","27":"ZA","290":"SH","291":"ER","297":"AW","298":"FO","299":"GL",
    "30":"GR","31":"NL","32":"BE","33":"FR","34":"ES","350":"GI","351":"PT",
    "352":"LU","353":"IE","354":"IS","355":"AL","356":"MT","357":"CY","358":"FI",
    "359":"BG","36":"HU","370":"LT","371":"LV","372":"EE","373":"MD","374":"AM",
    "375":"BY","376":"AD","377":"MC","378":"SM","379":"VA","380":"UA","381":"RS",
    "382":"ME","383":"XK","385":"HR","386":"SI","387":"BA","389":"MK","39":"IT",
    "40":"RO","41":"CH","420":"CZ","421":"SK","423":"LI","43":"AT","44":"GB",
    "45":"DK","46":"SE","47":"NO","48":"PL","500":"FK","501":"BZ","502":"GT",
    "503":"SV","504":"HN","505":"NI","506":"CR","507":"PA","508":"PM","509":"HT",
    "51":"PE","52":"MX","53":"CU","54":"AR","55":"BR","56":"CL","57":"CO","58":"VE",
    "590":"GP","591":"BO","592":"GY","593":"EC","594":"GF","595":"PY","596":"MQ",
    "597":"SR","598":"UY","599":"CW","60":"MY","61":"AU","62":"ID","63":"PH",
    "64":"NZ","65":"SG","66":"TH","670":"TL","672":"AQ","673":"BN","674":"NR",
    "675":"PG","676":"TO","677":"SB","678":"VU","679":"FJ","680":"PW","681":"WF",
    "682":"CK","683":"NU","685":"WS","686":"KI","687":"NC","688":"TV","689":"PF",
    "690":"TK","691":"FM","692":"MH","800":"ZZ","81":"JP","82":"KR","84":"VN",
    "850":"KP","852":"HK","853":"MO","855":"KH","856":"LA","86":"CN","880":"BD",
    "886":"TW","90":"TR","91":"IN","92":"PK","93":"AF","94":"LK","95":"MM",
    "960":"MV","961":"LB","962":"JO","963":"SY","964":"IQ","965":"KW","966":"SA",
    "967":"YE","968":"OM","970":"PS","971":"AE","972":"IL","973":"BH","974":"QA",
    "975":"BT","976":"MN","977":"NP","98":"IR","992":"TJ","993":"TM","994":"AZ",
    "995":"GE","996":"KG","998":"UZ"
}

ISO_TO_FLAG = {iso: chr(0x1F1E6 + ord(iso[0]) - 65) + chr(0x1F1E6 + ord(iso[1]) - 65)
               for iso in set(PHONE_PREFIX_TO_ISO.values()) if len(iso) == 2 and iso.isalpha()}

def get_flag_and_code(num):
    char, iso, _ = get_flag_info_from_num(num)
    if str(iso).upper() != "XX":
        return char, str(iso).upper()
    clean = re.sub(r"\D", "", str(num))
    # Prefer the longest prefix, except Kazakhstan/Russia where +7 is shared.
    for prefix in sorted(PHONE_PREFIX_TO_ISO, key=len, reverse=True):
        if clean.startswith(prefix):
            resolved_iso = PHONE_PREFIX_TO_ISO[prefix]
            return ISO_TO_FLAG.get(resolved_iso, "🌍"), resolved_iso
    return "🌍", "XX"

COUNTRY_NAME_BY_ISO = {'AD': 'Andorra', 'AE': 'United Arab Emirates', 'AF': 'Afghanistan', 'AG': 'Antigua and Barbuda', 'AI': 'Anguilla', 'AL': 'Albania', 'AM': 'Armenia', 'AO': 'Angola', 'AQ': 'Antarctica', 'AR': 'Argentina', 'AS': 'American Samoa', 'AT': 'Austria', 'AU': 'Australia', 'AW': 'Aruba', 'AX': 'Åland Islands', 'AZ': 'Azerbaijan', 'BA': 'Bosnia and Herzegovina', 'BB': 'Barbados', 'BD': 'Bangladesh', 'BE': 'Belgium', 'BF': 'Burkina Faso', 'BG': 'Bulgaria', 'BH': 'Bahrain', 'BI': 'Burundi', 'BJ': 'Benin', 'BL': 'Saint Barthélemy', 'BM': 'Bermuda', 'BN': 'Brunei', 'BO': 'Bolivia', 'BQ': 'Bonaire, Sint Eustatius and Saba', 'BR': 'Brazil', 'BS': 'Bahamas', 'BT': 'Bhutan', 'BV': 'Bouvet Island', 'BW': 'Botswana', 'BY': 'Belarus', 'BZ': 'Belize', 'CA': 'Canada', 'CC': 'Cocos (Keeling) Islands', 'CD': 'Democratic Republic of the Congo', 'CF': 'Central African Republic', 'CG': 'Republic of the Congo', 'CH': 'Switzerland', 'CI': 'Côte d’Ivoire', 'CK': 'Cook Islands', 'CL': 'Chile', 'CM': 'Cameroon', 'CN': 'China', 'CO': 'Colombia', 'CR': 'Costa Rica', 'CU': 'Cuba', 'CV': 'Cabo Verde', 'CW': 'Curaçao', 'CX': 'Christmas Island', 'CY': 'Cyprus', 'CZ': 'Czech Republic', 'DE': 'Germany', 'DJ': 'Djibouti', 'DK': 'Denmark', 'DM': 'Dominica', 'DO': 'Dominican Republic', 'DZ': 'Algeria', 'EC': 'Ecuador', 'EE': 'Estonia', 'EG': 'Egypt', 'EH': 'Western Sahara', 'ER': 'Eritrea', 'ES': 'Spain', 'ET': 'Ethiopia', 'FI': 'Finland', 'FJ': 'Fiji', 'FK': 'Falkland Islands (Malvinas)', 'FM': 'Micronesia, Federated States of', 'FO': 'Faroe Islands', 'FR': 'France', 'GA': 'Gabon', 'GB': 'United Kingdom', 'GD': 'Grenada', 'GE': 'Georgia', 'GF': 'French Guiana', 'GG': 'Guernsey', 'GH': 'Ghana', 'GI': 'Gibraltar', 'GL': 'Greenland', 'GM': 'Gambia', 'GN': 'Guinea', 'GP': 'Guadeloupe', 'GQ': 'Equatorial Guinea', 'GR': 'Greece', 'GS': 'South Georgia and the South Sandwich Islands', 'GT': 'Guatemala', 'GU': 'Guam', 'GW': 'Guinea-Bissau', 'GY': 'Guyana', 'HK': 'Hong Kong', 'HM': 'Heard Island and McDonald Islands', 'HN': 'Honduras', 'HR': 'Croatia', 'HT': 'Haiti', 'HU': 'Hungary', 'ID': 'Indonesia', 'IE': 'Ireland', 'IL': 'Israel', 'IM': 'Isle of Man', 'IN': 'India', 'IO': 'British Indian Ocean Territory', 'IQ': 'Iraq', 'IR': 'Iran', 'IS': 'Iceland', 'IT': 'Italy', 'JE': 'Jersey', 'JM': 'Jamaica', 'JO': 'Jordan', 'JP': 'Japan', 'KE': 'Kenya', 'KG': 'Kyrgyzstan', 'KH': 'Cambodia', 'KI': 'Kiribati', 'KM': 'Comoros', 'KN': 'Saint Kitts and Nevis', 'KP': 'North Korea', 'KR': 'South Korea', 'KW': 'Kuwait', 'KY': 'Cayman Islands', 'KZ': 'Kazakhstan', 'LA': 'Laos', 'LB': 'Lebanon', 'LC': 'Saint Lucia', 'LI': 'Liechtenstein', 'LK': 'Sri Lanka', 'LR': 'Liberia', 'LS': 'Lesotho', 'LT': 'Lithuania', 'LU': 'Luxembourg', 'LV': 'Latvia', 'LY': 'Libya', 'MA': 'Morocco', 'MC': 'Monaco', 'MD': 'Moldova', 'ME': 'Montenegro', 'MF': 'Saint Martin (French part)', 'MG': 'Madagascar', 'MH': 'Marshall Islands', 'MK': 'North Macedonia', 'ML': 'Mali', 'MM': 'Myanmar', 'MN': 'Mongolia', 'MO': 'Macao', 'MP': 'Northern Mariana Islands', 'MQ': 'Martinique', 'MR': 'Mauritania', 'MS': 'Montserrat', 'MT': 'Malta', 'MU': 'Mauritius', 'MV': 'Maldives', 'MW': 'Malawi', 'MX': 'Mexico', 'MY': 'Malaysia', 'MZ': 'Mozambique', 'NA': 'Namibia', 'NC': 'New Caledonia', 'NE': 'Niger', 'NF': 'Norfolk Island', 'NG': 'Nigeria', 'NI': 'Nicaragua', 'NL': 'Netherlands', 'NO': 'Norway', 'NP': 'Nepal', 'NR': 'Nauru', 'NU': 'Niue', 'NZ': 'New Zealand', 'OM': 'Oman', 'PA': 'Panama', 'PE': 'Peru', 'PF': 'French Polynesia', 'PG': 'Papua New Guinea', 'PH': 'Philippines', 'PK': 'Pakistan', 'PL': 'Poland', 'PM': 'Saint Pierre and Miquelon', 'PN': 'Pitcairn', 'PR': 'Puerto Rico', 'PS': 'Palestine', 'PT': 'Portugal', 'PW': 'Palau', 'PY': 'Paraguay', 'QA': 'Qatar', 'RE': 'Réunion', 'RO': 'Romania', 'RS': 'Serbia', 'RU': 'Russia', 'RW': 'Rwanda', 'SA': 'Saudi Arabia', 'SB': 'Solomon Islands', 'SC': 'Seychelles', 'SD': 'Sudan', 'SE': 'Sweden', 'SG': 'Singapore', 'SH': 'Saint Helena, Ascension and Tristan da Cunha', 'SI': 'Slovenia', 'SJ': 'Svalbard and Jan Mayen', 'SK': 'Slovakia', 'SL': 'Sierra Leone', 'SM': 'San Marino', 'SN': 'Senegal', 'SO': 'Somalia', 'SR': 'Suriname', 'SS': 'South Sudan', 'ST': 'Sao Tome and Principe', 'SV': 'El Salvador', 'SX': 'Sint Maarten (Dutch part)', 'SY': 'Syria', 'SZ': 'Eswatini', 'TC': 'Turks and Caicos Islands', 'TD': 'Chad', 'TF': 'French Southern Territories', 'TG': 'Togo', 'TH': 'Thailand', 'TJ': 'Tajikistan', 'TK': 'Tokelau', 'TL': 'Timor-Leste', 'TM': 'Turkmenistan', 'TN': 'Tunisia', 'TO': 'Tonga', 'TR': 'Türkiye', 'TT': 'Trinidad and Tobago', 'TV': 'Tuvalu', 'TW': 'Taiwan, Province of China', 'TZ': 'Tanzania', 'UA': 'Ukraine', 'UG': 'Uganda', 'UM': 'United States Minor Outlying Islands', 'US': 'United States', 'UY': 'Uruguay', 'UZ': 'Uzbekistan', 'VA': 'Holy See (Vatican City State)', 'VC': 'Saint Vincent and the Grenadines', 'VE': 'Venezuela', 'VG': 'Virgin Islands, British', 'VI': 'Virgin Islands, U.S.', 'VN': 'Vietnam', 'VU': 'Vanuatu', 'WF': 'Wallis and Futuna', 'WS': 'Samoa', 'XK': 'Kosovo', 'YE': 'Yemen', 'YT': 'Mayotte', 'ZA': 'South Africa', 'ZM': 'Zambia', 'ZW': 'Zimbabwe'}

def get_flag_info_html(num_or_iso, return_full_name=False):
    """Return a country flag/name from ISO or phone prefix, with a complete ISO fallback."""
    value = str(num_or_iso or '').strip()
    if len(value) == 2 and value.isalpha():
        iso = value.upper()
        for code, data in bot_settings.get("premium_flags", {}).items():
            if str(data.get("iso", "")).upper() == iso:
                if return_full_name:
                    return data.get("name") or COUNTRY_NAME_BY_ISO.get(iso, iso)
                eid = data.get("id")
                char = data.get("char") or ISO_TO_FLAG.get(iso, "🌍")
                if eid:
                    return f'<tg-emoji emoji-id="{html.escape(str(eid), quote=True)}">{html.escape(str(char))}</tg-emoji>'
                return char
        if return_full_name:
            return COUNTRY_NAME_BY_ISO.get(iso, iso)
        return ISO_TO_FLAG.get(iso, "🌍")

    clean = re.sub(r"\D", "", value)
    char, iso, eid = get_flag_info_from_num(value)
    iso = str(iso or "XX").upper()
    if iso == "XX" and clean:
        for prefix in sorted(PHONE_PREFIX_TO_ISO, key=len, reverse=True):
            if clean.startswith(prefix):
                iso = PHONE_PREFIX_TO_ISO[prefix]
                char = ISO_TO_FLAG.get(iso, char)
                break
    if return_full_name:
        if iso != "XX":
            for code, data in bot_settings.get("premium_flags", {}).items():
                if str(data.get("iso", "")).upper() == iso and data.get("name"):
                    return data["name"]
            return COUNTRY_NAME_BY_ISO.get(iso, iso)
        return value
    if iso != "XX":
        for code, data in bot_settings.get("premium_flags", {}).items():
            if str(data.get("iso", "")).upper() == iso:
                eid = data.get("id")
                char = data.get("char") or ISO_TO_FLAG.get(iso, char)
                if eid:
                    return f'<tg-emoji emoji-id="{html.escape(str(eid), quote=True)}">{html.escape(str(char))}</tg-emoji>'
                return char
        return ISO_TO_FLAG.get(iso, char or "🌍")
    return char or "🌍"

def mask_number(num):
    clean = num.replace("+", "").replace(" ", "")
    if len(clean) > 6: return f"{clean[:3]}DXA{clean[-3:]}"
    elif len(clean) > 2: return f"{clean[:1]}DXA{clean[-1:]}"
    return clean

LANG_MAP = {
    "#EN": "English", "#BN": "Bengali", "#AR": "Arabic", "#HI": "Hindi", 
    "#PA": "Punjabi", "#GU": "Gujarati", "#OR": "Odia", "#TA": "Tamil", 
    "#TE": "Telugu", "#KN": "Kannada", "#ML": "Malayalam", "#SI": "Sinhala", 
    "#TH": "Thai", "#LO": "Lao", "#BO": "Tibetan", "#MY": "Burmese", 
    "#AM": "Amharic", "#KM": "Khmer", "#KA": "Georgian", "#HY": "Armenian", 
    "#HE": "Hebrew", "#EL": "Greek", "#RU": "Russian", "#ZH": "Chinese", 
    "#JA": "Japanese", "#KO": "Korean", "#ID": "Indonesian", "#MS": "Malay", 
    "#VN": "Vietnamese", "#TL": "Filipino", "#ES": "Spanish", "#PT": "Portuguese", 
    "#FR": "French", "#DE": "German", "#IT": "Italian", "#PL": "Polish", 
    "#TR": "Turkish", "#NL": "Dutch", "#SV": "Swedish", "#DA": "Danish", 
    "#NO": "Norwegian", "#FI": "Finnish", "#CS": "Czech", "#SK": "Slovak", 
    "#HU": "Hungarian", "#RO": "Romanian", "#HR": "Croatian", "#BG": "Bulgarian", 
    "#UK": "Ukrainian", "#SW": "Swahili", "#AF": "Afrikaans"
}

# ==========================================
# 🌟 ADVANCED SERVICE & LANGUAGE DETECTION
# ==========================================

SERVICE_SMS_KEYWORDS = {
    # 🟢 Social Media & Chat (Added Arabic Keywords)
    "whatsapp": ["whatsapp", "whatsa", "whatsap", "whats", "whatsapp business", "whatsapp me", "whatsapp code", "whatsap", "واتساب", "واتساپ", "واٹس ایپ", "व्हाट्सएप", "वाट्सएप", "वॉट्सऐप", "व्हाट्सप्प", "হোয়াটসঅ্যাপ", "হোটসঅ্যাপ", "ватсап", "уотсап", "вотсап", "ватс апп", "వాట్సాప్", "വാട്‌സ്ആപ്പ്", "வாட்ஸ்அப்", "ವಾಟ್ಸಾಪ್", "વોટ્સએપ", "ਵਟਸਐਪ", "ହ୍ଵାଟସ୍ ଆପ୍", "වට්ස්ඇප්", "วอตส์แอปป์", "วอทส์แอพ", "ဝက်စ်အက်ပ်", "វ៉តសាប់", "ວອດແອັບ", "ワッツアップ", "왓츠앱", "whatsapp的", "whatsapp验证码", "וואטסאפ", "γουάτσαπ", "ዋትስአፕ", "ვოთსאფი", "վոթսափ"],
    "facebook": ["facebook", "fb", "meta", "fbook", "fb code", "facebook code", "فيسبوك", "فيس بوك"],
    "instagram": ["instagram", "insta", "ig", "ig code", "instagram code", "انستغرام", "انستقرام"],
    "telegram": ["telegram", "tg", "tele", "telegram code", "tg code", "t.me", "تيليجرام", "تليجرام"],
    "tiktok": ["tiktok", "tik tok", "tikvideo", "tiktok code", "tik code", "تيك توك"],
    "snapchat": ["snapchat", "snap", "snap code", "سناب شات"],
    "twitter": ["twitter", "x.com", "x code", "twitter code", "تويتر"],
    "discord": ["discord", "discord code", "ديسكورد"],
    "viber": ["viber", "viber code", "فايبر"],
    "line": ["line", "line code", "line verification", "لاين"],
    "wechat": ["wechat", "we chat", "wechat code", "وي تشات"],
    "signal": ["signal", "signal code", "سيجنال"],
    "linkedin": ["linkedin", "linked in", "لينكد إن"],
    "imo": ["imo", "imo code", "imo verification", "ايمو"],
    "kakaotalk": ["kakao", "kakaotalk", "كاكاو"],
    "qq": ["qq", "tencent qq"],
    "vk": ["vk", "vkontakte"],

    # 🔵 Tech & Mail
    "google": ["google", "gmail", "youtube", "g-", "google voice", "جوجل", "غوغل"],
    "microsoft": ["microsoft", "ms", "outlook", "live.com", "hotmail"],
    "apple": ["apple", "icloud", "itunes", "apple id"],
    "yahoo": ["yahoo", "yahoo code", "ymail"],
    "protonmail": ["proton", "protonmail"],
    
    # 💰 Crypto & Trading
    "binance": ["binance", "bnb", "binances"],
    "coinbase": ["coinbase"],
    "okx": ["okx", "okex"],
    "kucoin": ["kucoin"],
    "bybit": ["bybit"],
    "huobi": ["huobi", "htx"],
    "mexc": ["mexc"],
    "trustwallet": ["trust wallet", "trustwallet"],

    # 💳 Finance & Wallets
    "bkash": ["bkash", "b-kash", "bkash code"],
    "nagad": ["nagad", "nagad code"],
    "rocket": ["rocket", "dutch bangla"],
    "upay": ["upay", "upay code"],
    "paypal": ["paypal", "pay pal"],
    "paytm": ["paytm"],
    "cashapp": ["cash app", "cashapp"],
    "wise": ["wise", "transferwise"],

    # 🛒 E-commerce & Delivery
    "amazon": ["amazon", "amzn", "amazon code"],
    "ebay": ["ebay"],
    "aliexpress": ["aliexpress", "ali express"],
    "alibaba": ["alibaba"],
    "daraz": ["daraz", "daraz code"],
    "foodpanda": ["foodpanda", "food panda"],
    "uber": ["uber", "uber code", "uber verification", "uber eats"],
    "pathao": ["pathao", "pathao ride"],

    # 🎮 Gaming & Entertainment
    "netflix": ["netflix", "netflix code"],
    "spotify": ["spotify", "spotify code"],
    "steam": ["steam", "steam guard"],
    "epicgames": ["epic games", "epicgames"],
    "roblox": ["roblox", "roblox code"],
    "riotgames": ["riot", "riot games", "valorant", "league of legends"],
    "garena": ["garena", "free fire", "freefire"],
    "playstation": ["playstation", "psn"],

    # 🎲 Betting & Casino
    "1xbet": ["1xbet", "1x bet"],
    "melbet": ["melbet", "melbet code"],
    "linebet": ["linebet"],
    "bet365": ["bet365"],
    "megapari": ["megapari"],

    # ❤️ Dating
    "tinder": ["tinder", "tinder code"],
    "bumble": ["bumble"],
    "badoo": ["badoo"]
}

def _normalize_service_value(value):
    """Normalize API/SMS service labels without ever using the configured panel name."""
    if value is None:
        return ""
    if isinstance(value, dict):
        for k in ("name", "service", "service_name", "title", "app", "app_name", "application", "product", "label", "display_name"):
            if k in value and value[k] not in (None, ""):
                got = _normalize_service_value(value[k])
                if got:
                    return got
        return ""
    if isinstance(value, (list, tuple)):
        for x in value:
            got = _normalize_service_value(x)
            if got:
                return got
        return ""
    text = re.sub(r'\s+', ' ', str(value)).strip()
    if not text or len(text) > 120:
        return ""
    return text

SERVICE_ALIASES = {
    "WA": "WHATSAPP", "WA BUSINESS": "WHATSAPP", "WHATSAPP BUSINESS": "WHATSAPP",
    "TG": "TELEGRAM", "TELEGRAM MESSENGER": "TELEGRAM",
    "FB": "FACEBOOK", "FACEBOOK META": "FACEBOOK", "META": "FACEBOOK",
    "IG": "INSTAGRAM", "TT": "TIKTOK", "TIK TOK": "TIKTOK",
    "GOOGLE GMAIL": "GOOGLE", "GMAIL": "GOOGLE",
}

def _canonical_service(value):
    name = _normalize_service_value(value)
    if not name:
        return ""
    key = re.sub(r"\s+", " ", name).strip().upper()
    return SERVICE_ALIASES.get(key, key)

def _strip_country_visuals(value):
    """Remove leading country/globe emoji from admin-entered country labels.

    Country identity is stored separately from presentation so entries such as
    "🇰🇿 Kazakhstan", "🌍 Kazakhstan", "KZ", and "kazakhstan" all resolve to
    the same canonical country.
    """
    raw = str(value or "").strip()
    if not raw:
        return ""
    # Regional-indicator flag pairs (Unicode country flags).
    raw = re.sub(r"^[\s\U0001F1E6-\U0001F1FF]+", "", raw).strip()
    # Common globe symbols that were previously being shown beside the flag.
    raw = re.sub(r"^[\s🌍🌎🌏🗺️]+", "", raw).strip()
    return raw

def _country_identity(value):
    raw = _strip_country_visuals(value)
    if not raw:
        return ""
    up = raw.upper()
    if len(up) == 2 and up.isalpha() and up in COUNTRY_NAME_BY_ISO:
        return up
    for iso, name in COUNTRY_NAME_BY_ISO.items():
        if str(name).strip().casefold() == raw.casefold():
            return str(iso).upper()
    for data in bot_settings.get("premium_flags", {}).values():
        if str(data.get("name", "")).strip().casefold() == raw.casefold():
            iso = str(data.get("iso", "")).strip().upper()
            if len(iso) == 2:
                return iso
    for code, data in bot_settings.get("premium_flags", {}).items():
        if str(code).strip() == raw:
            iso = str(data.get("iso", "")).strip().upper()
            if len(iso) == 2:
                return iso
    return re.sub(r"\s+", " ", raw).strip().casefold()

def _parse_admin_country_input(value):
    """Parse an admin supplied country label without imposing an ISO whitelist.

    Accepted examples:
      - 🇦🇱 Albena
      - Albena 🇦🇱
      - Albena | 🇦🇱
      - 🇰🇿 Kazakhstan

    The supplied display flag/name are preserved exactly (apart from surrounding
    whitespace) while _country_identity() remains the internal merge key.
    """
    raw = str(value or "").strip()
    if not raw:
        return "", "", ""

    # A Unicode regional-indicator pair is a real flag sequence.
    m = re.match(r"^([\U0001F1E6-\U0001F1FF]{2})(?:\s+|$)(.*)$", raw, flags=re.S)
    if m:
        flag = m.group(1)
        name = m.group(2).strip() or flag
        return name, flag, _country_identity(name)

    # Also accept a flag supplied after the name, optionally separated by '|'.
    m = re.match(r"^(.*?)(?:\s*\|\s*|\s+)([\U0001F1E6-\U0001F1FF]{2})$", raw, flags=re.S)
    if m:
        name = m.group(1).strip()
        flag = m.group(2)
        if name:
            return name, flag, _country_identity(name)

    # Custom emoji flags are allowed too (for example: 🔥 My Country).  Keep
    # one leading emoji grapheme-ish sequence instead of inventing 🌍.
    def take_emoji_prefix(text):
        if not text:
            return "", text
        i = 0
        chars = list(text)
        first = chars[0]
        if not (ord(first) >= 0x1F000 or unicodedata.category(first) in ("So", "Sk")):
            return "", text
        flag_chars = [first]
        i = 1
        while i < len(chars):
            ch = chars[i]
            if unicodedata.combining(ch) or 0xFE00 <= ord(ch) <= 0xFE0F or 0x1F3FB <= ord(ch) <= 0x1F3FF or ord(ch) == 0x200D:
                flag_chars.append(ch)
                i += 1
                continue
            # ZWJ-connected emoji component.
            if i + 1 < len(chars) and ord(ch) >= 0x1F000 and ord(chars[i-1]) == 0x200D:
                flag_chars.append(ch)
                i += 1
                continue
            break
        return "".join(flag_chars), text[i:].strip()

    flag, name = take_emoji_prefix(raw)
    if flag and name:
        return name, flag, _country_identity(name)

    # No explicit visual was supplied. Standard ISO/name countries can still
    # derive their normal flag; arbitrary custom names simply have no flag.
    ident = _country_identity(raw)
    return _strip_country_visuals(raw), "", ident

def _country_display(value, country_name=None, country_flag=None):
    """Return country display data, preferring admin-supplied custom visuals.

    There is intentionally NO 🌍 fallback.  Arbitrary custom country names are
    valid and can carry any flag/emoji supplied by the admin.
    """
    ident = _country_identity(value)
    iso = ident.upper() if len(ident) == 2 and ident.isalpha() else ""

    supplied_name = str(country_name or "").strip()
    supplied_flag = str(country_flag or "").strip()
    clean_value = _strip_country_visuals(value)

    if supplied_name:
        name = supplied_name
    else:
        name = COUNTRY_NAME_BY_ISO.get(iso, clean_value)

    if supplied_flag:
        flag = supplied_flag
    else:
        flag = ISO_TO_FLAG.get(iso, "")

    # Premium admin country data may override the standard ISO display when no
    # explicit custom name/flag was stored with the uploaded batch.
    if iso and not supplied_name:
        for fd in bot_settings.get("premium_flags", {}).values():
            if str(fd.get("iso", "")).strip().upper() == iso:
                name = str(fd.get("name") or name).strip()
                break

    return name, flag, iso

def _batch_country_display(service, country):
    """Get the best display metadata for a service/country from local stock."""
    svc_id = _canonical_service(service)
    cnt_id = _country_identity(country)
    for batch in number_batches.values():
        if not isinstance(batch, dict) or not batch.get("numbers"):
            continue
        if _canonical_service(batch.get("service")) != svc_id:
            continue
        if _country_identity(batch.get("country")) != cnt_id:
            continue
        return _country_display(
            batch.get("country", country),
            batch.get("country_name", ""),
            batch.get("country_flag", "")
        )
    return _country_display(country)

def _merged_get_number_catalog():
    """Build one unlimited unified Service -> Country catalog.

    Sources are merged into the same service identity: manually uploaded
    numbers, configured Stex ranges, and recent Voltx live traffic.  A service
    or country is only exposed when it has real local stock or a usable API
    source; empty configuration shells are not shown to users.
    """
    catalog = {}

    def add(service, country, source, country_name="", country_flag=""):
        svc = _canonical_service(service)
        cnt = _country_identity(country)
        if not svc or not cnt:
            return
        entry = catalog.setdefault(svc, {"sources": set(), "countries": {}, "country_display": {}})
        entry["sources"].add(source)
        entry["countries"].setdefault(cnt, set()).add(source)
        if country_name or country_flag:
            entry["country_display"][cnt] = {
                "name": str(country_name or "").strip(),
                "flag": str(country_flag or "").strip(),
            }

    # Manual/uploaded numbers are ACTIVE immediately.  There is intentionally
    # no service/country count cap here.
    for batch in number_batches.values():
        if not isinstance(batch, dict):
            continue
        if any(str(n.get("num", "")).strip() for n in (batch.get("numbers") or []) if isinstance(n, dict)):
            add(
                batch.get("service"),
                batch.get("country"),
                "local",
                batch.get("country_name", ""),
                batch.get("country_flag", "")
            )

    # Stex services are active only when the configured country has at least
    # one usable range.  Empty service/country shells stay hidden.
    for service, countries in bot_settings.get("stex_services", {}).items():
        if not isinstance(countries, dict):
            continue
        for country, ranges in countries.items():
            usable = [str(r).replace("+", "").replace("X", "").replace("x", "").strip()
                      for r in (ranges or []) if str(r).strip()]
            if usable:
                add(service, country, "stex")

    # Voltx contributes only genuinely recent live traffic.
    try:
        for service, countries in get_voltx_active_catalog(120).items():
            if not isinstance(countries, dict):
                continue
            for country, ranges in countries.items():
                if ranges:
                    add(service, country, "voltx")
    except Exception:
        pass
    return catalog

def _remember_local_assignment(number, chat_id, service="", country=""):
    """Persist every local-number owner so later OTPs can find the user.

    A number may legitimately be shared, therefore ownership is a list rather
    than a single user id.
    """
    key = _clean_compare_number(number)
    if not key:
        return
    entry = local_assigned_numbers.setdefault(key, {"owners": [], "service": "", "country": ""})
    owners = entry.setdefault("owners", [])
    if str(chat_id) not in {str(x) for x in owners}:
        owners.append(chat_id)
    if service:
        entry["service"] = _canonical_service(service)
    if country:
        entry["country"] = _country_identity(country)

def _local_assignment_for_number(number):
    key = _clean_compare_number(number)
    if not key:
        return None
    exact = local_assigned_numbers.get(key)
    if exact:
        return exact
    for stored, entry in local_assigned_numbers.items():
        if _same_phone_number(key, stored):
            return entry
    return None

def _find_local_numbers(service, country, chat_id, req_count):
    svc_id = _canonical_service(service)
    cnt_id = _country_identity(country)
    active_prefix = re.sub(r"\D", "", str(user_prefixes.get(chat_id, "")).strip())
    found = []
    for b_id, batch in number_batches.items():
        if _canonical_service(batch.get("service")) != svc_id:
            continue
        if _country_identity(batch.get("country")) != cnt_id:
            continue
        for idx, n_obj in enumerate(batch.get("numbers", []) or []):
            if chat_id in n_obj.get("used_by", []):
                continue
            num_value = str(n_obj.get("num", "")).strip()
            clean_num = re.sub(r"\D", "", num_value)
            if active_prefix and not clean_num.startswith(active_prefix):
                continue
            if clean_num:
                found.append((b_id, idx))
                if len(found) >= req_count:
                    return found
    return found

def _normalized_stex_ranges(service, country):
    svc_id = _canonical_service(service)
    cnt_id = _country_identity(country)
    result = []
    for srv, countries in bot_settings.get("stex_services", {}).items():
        if _canonical_service(srv) != svc_id or not isinstance(countries, dict):
            continue
        for cnt, ranges in countries.items():
            if _country_identity(cnt) != cnt_id:
                continue
            for r in ranges or []:
                clean = str(r).replace("X", "").replace("x", "").replace("+", "").strip()
                if clean and clean not in result:
                    result.append(clean)
    return result

def _service_keyword_match(keyword, text_lower):
    """Match service keywords without letting short aliases cause false positives."""
    kw = str(keyword or "").strip().lower()
    if not kw:
        return False
    if len(kw) <= 3 and re.fullmatch(r"[a-z0-9]+", kw):
        return bool(re.search(rf"(?<![a-z0-9]){re.escape(kw)}(?![a-z0-9])", text_lower))
    return kw in text_lower

def detect_service(text):
    """Detect the real OTP service from SMS text and configured service names."""
    text_lower = str(text or "").lower()
    if not text_lower:
        return None

    # Built-in service keywords. Longer/specific phrases are safe substring matches;
    # very short aliases (TG/IG/FB/TT etc.) require word boundaries to avoid false hits.
    for service_key, keywords in SERVICE_SMS_KEYWORDS.items():
        for kw in keywords:
            if _service_keyword_match(kw, text_lower):
                return str(service_key).upper()

    # Also learn service names/aliases from the admin's configured Premium Emoji/App list.
    try:
        for app_key, data in bot_settings.get("premium_apps", {}).items():
            candidates = [app_key]
            if isinstance(data, dict):
                candidates += [data.get("name"), data.get("short_name"), data.get("service"), data.get("app")]
            for candidate in candidates:
                candidate = _normalize_service_value(candidate)
                if not candidate:
                    continue
                if candidate.lower() in text_lower:
                    return SERVICE_ALIASES.get(candidate.upper(), candidate.upper())
    except Exception:
        pass
    return None

def _normalize_service_key(value):
    """Normalize a service label for reliable matching against configured app names."""
    text = _normalize_service_value(value).upper()
    text = re.sub(r"[^A-Z0-9]+", " ", text).strip()
    text = re.sub(r"\s+", " ", text)
    return SERVICE_ALIASES.get(text, text)

def _get_configured_service_app(service_text, msg_text=""):
    """Return the admin-configured service name + custom emoji for the actual service."""
    apps = bot_settings.get("premium_apps", {}) or {}
    detected = detect_service(msg_text) if msg_text else None
    target = _normalize_service_key(detected or service_text)
    if not target:
        return None, None, None

    candidates = []
    for app_key, data in apps.items():
        data = data if isinstance(data, dict) else {}
        key = _normalize_service_key(app_key)
        name = _normalize_service_key(data.get("name", ""))
        short_name = _normalize_service_key(data.get("short_name", ""))
        service_name = _normalize_service_key(data.get("service", ""))
        candidates.append((app_key, data, key, name, short_name, service_name))

    # Exact configured service match first.
    for app_key, data, key, name, short_name, service_name in candidates:
        if target in {key, name, short_name, service_name}:
            return data.get("name") or app_key, data.get("id"), data.get("char") or "◉"

    # Controlled match for labels such as "TikTok OTP" or "TikTok verification".
    for app_key, data, key, name, short_name, service_name in candidates:
        keys = [x for x in (key, name, short_name, service_name) if x]
        if any((x in target or target in x) and len(x) >= 3 for x in keys):
            return data.get("name") or app_key, data.get("id"), data.get("char") or "◉"
    return None, None, None

def get_service_info_html(service_text, msg_text=""):
    """Display the actual service from panel/SMS/number assignment, never a provider label."""
    raw_service = _normalize_service_value(service_text)
    explicit = raw_service
    if explicit.upper() in SERVICE_ALIASES:
        explicit = SERVICE_ALIASES[explicit.upper()]

    # Prefer a valid service name attached to the received panel record.
    # If it is unavailable, use SMS detection, then configured service identity.
    resolved = explicit if explicit and not _is_panel_or_provider_label(explicit) else None
    if not resolved:
        resolved = detect_service(msg_text) if msg_text else None
    if not resolved:
        resolved = raw_service if raw_service and not _is_panel_or_provider_label(raw_service) else None

    configured_name, eid, char = _get_configured_service_app(resolved or raw_service, msg_text)
    if configured_name:
        if eid:
            return str(configured_name).strip(), f'<tg-emoji emoji-id="{html.escape(str(eid), quote=True)}">{html.escape(str(char or "◉"))}</tg-emoji>'
        return str(configured_name).strip(), ""

    # If the panel supplied a real service label that is not configured for a custom emoji,
    # show that exact label instead of "UNKNOWN SERVICE".
    if resolved:
        return str(resolved).strip(), ""

    # Do not expose provider/panel labels as a fake service name.
    return "", ""

def _clean_compare_number(value):
    return re.sub(r'\D', '', str(value or ''))

def _same_phone_number(a, b):
    a, b = _clean_compare_number(a), _clean_compare_number(b)
    if not a or not b:
        return False
    return a == b or (len(a) >= 8 and len(b) >= 8 and (a.endswith(b[-8:]) or b.endswith(a[-8:])))

def _is_panel_or_provider_label(value):
    """Reject configured API panel/provider labels so they can never become the OTP service name."""
    text = _normalize_service_value(value).strip().lower()
    if not text:
        return False
    generic = {"api panel", "panel", "sms panel", "sms", "otp panel", "provider", "unknown service"}
    if text in generic:
        return True
    try:
        for p in bot_settings.get("panels", []):
            for key in ("name", "panel_name", "title", "type"):
                pv = _normalize_service_value(p.get(key, "")).strip().lower()
                if pv and text == pv:
                    return True
    except Exception:
        pass
    return False

def resolve_real_service(number, api_service="", sms_text=""):
    """Resolve the actual service for an OTP using SMS evidence + number-to-service assignment."""
    # 1) SMS itself is strongest direct evidence.
    detected = detect_service(sms_text)
    if detected:
        return detected

    # 2) API metadata is allowed only when it is not a configured panel/provider label.
    explicit = _normalize_service_value(api_service)
    if explicit and not _is_panel_or_provider_label(explicit):
        return explicit

    # 3) Match the received number to the user's active request/session service.
    try:
        for session in user_active_sessions.values():
            srv = _normalize_service_value(session.get("service", ""))
            if not srv:
                continue
            for n in session.get("nums", []) or []:
                if _same_phone_number(number, n):
                    return srv
    except Exception:
        pass

    # 4) Match local uploaded/allocated number batches; every batch already has its service.
    try:
        for batch in number_batches.values():
            srv = _normalize_service_value(batch.get("service", ""))
            if not srv:
                continue
            for entry in batch.get("numbers", []) or []:
                n = entry.get("num") if isinstance(entry, dict) else entry
                if _same_phone_number(number, n):
                    return srv
    except Exception:
        pass

    return ""

# Cache service identity by phone number whenever a service is successfully resolved.
# This keeps later OTP records tied to the same number even when a later API record omits service metadata.
resolved_service_by_number = {}

def resolve_real_service(number, api_service="", sms_text=""):
    """Resolve the actual OTP service without exposing panel/provider labels."""
    key = _clean_compare_number(number)

    # 1) Direct SMS evidence is strongest when the message contains the app name.
    detected = detect_service(sms_text)
    if detected:
        resolved_service_by_number[key] = detected
        return detected

    # 2) Persistent local/manual assignment survives batch removal and session changes.
    local_assignment = _local_assignment_for_number(number)
    if local_assignment:
        assigned_service = _normalize_service_value(local_assignment.get("service", ""))
        if assigned_service and not _is_panel_or_provider_label(assigned_service):
            resolved_service_by_number[key] = assigned_service
            return assigned_service

    # 3) Match the received number to the user's active request/session.
    try:
        for session in user_active_sessions.values():
            srv = _normalize_service_value(session.get("service", ""))
            if not srv:
                continue
            for n in session.get("nums", []) or []:
                if _same_phone_number(number, n):
                    resolved_service_by_number[key] = srv
                    return srv
    except Exception:
        pass

    # 4) Match numbers that are still present in uploaded/local batches.
    try:
        for batch in number_batches.values():
            srv = _normalize_service_value(batch.get("service", ""))
            if not srv:
                continue
            for entry in batch.get("numbers", []) or []:
                n = entry.get("num") if isinstance(entry, dict) else entry
                if _same_phone_number(number, n):
                    resolved_service_by_number[key] = srv
                    return srv
    except Exception:
        pass

    # 5) Trust explicit API service metadata only after assignment/SMS checks.
    explicit = _normalize_service_value(api_service)
    if explicit and not _is_panel_or_provider_label(explicit):
        resolved_service_by_number[key] = explicit
        return explicit

    # 6) Previously resolved identity.
    if key and key in resolved_service_by_number:
        return resolved_service_by_number[key]
    return ""

def format_rony_number(number):
    """Mask the real number as: first 5 digits + RONY + last 4 digits."""
    raw = str(number).strip()
    digits = re.sub(r"\D", "", raw)
    if not digits:
        return raw
    # Keep only real digits from the original number; never generate or alter digits.
    first_part = digits[:5]
    last_part = digits[-4:] if len(digits) > 5 else ""
    if last_part:
        return f"+{first_part}🅁🄾🄽🅈-{last_part}"
    return f"+{first_part}🅁🄾🄽🅈"

_bot_username_cache = None

def get_running_bot_url():
    """Resolve the username of the bot represented by the currently configured TOKEN."""
    global _bot_username_cache
    if _bot_username_cache:
        return f"https://t.me/{_bot_username_cache}"
    try:
        data = requests.get(f"{BASE_URL}/getMe", timeout=10).json()
        username = data.get("result", {}).get("username", "").strip().lstrip("@")
        if username:
            _bot_username_cache = username
            return f"https://t.me/{username}"
    except Exception:
        pass
    return "https://t.me"

def _math_italic_upper(text):
    """Convert A-Z to Mathematical Sans-Serif Italic capitals for the requested country-code style."""
    out = []
    for ch in str(text).upper():
        if 'A' <= ch <= 'Z':
            out.append(chr(0x1D608 + ord(ch) - ord('A')))
        else:
            out.append(ch)
    return ''.join(out)

def _math_italic_text(text):
    """Convert simple Latin text to Mathematical Sans-Serif Italic, preserving unsupported characters."""
    out = []
    for ch in str(text):
        if 'A' <= ch <= 'Z':
            out.append(chr(0x1D608 + ord(ch) - ord('A')))
        elif 'a' <= ch <= 'z':
            out.append(chr(0x1D622 + ord(ch) - ord('a')))
        else:
            out.append(ch)
    return ''.join(out)

def format_otp_forward_body(number, service_text, sms_text="", language_hint=""):
    """Build the OTP group message in the user's exact requested layout.

    Only the OTP presentation is changed here. Prefix/back/session logic is
    intentionally untouched. Country comes from the phone number, service
    comes from the real API/SMS service mapping, and language comes from SMS.
    """
    raw_number = f"+{number}" if not str(number).startswith("+") else str(number)
    styled_number = format_rony_number(raw_number)

    # Real service only: never display a panel/provider label.
    resolved_service = resolve_real_service(raw_number, service_text, sms_text)
    if not resolved_service:
        candidate = _normalize_service_value(service_text)
        if candidate and not _is_panel_or_provider_label(candidate):
            resolved_service = candidate

    app_full_name, prem_app_html = get_service_info_html(resolved_service, sms_text)
    service_name = str(app_full_name or resolved_service or "").strip().upper()
    service_html = f"<b>{html.escape(service_name)}</b>" if service_name else ""
    service_line = (
        f"{prem_app_html} {service_html}".strip()
        if prem_app_html and service_html
        else (prem_app_html or service_html)
    )

    # Country is ALWAYS derived from the received number itself.
    # Use the configured premium flag when available; otherwise use the
    # comprehensive phone-prefix fallback so ISO never becomes XX for a
    # recognizable international number.
    configured_flag = get_flag_info_html(raw_number)
    fallback_flag, iso = get_flag_and_code(raw_number)
    iso = str(iso or "XX").upper()
    if iso != "XX":
        if iso in ISO_TO_FLAG:
            # Keep the premium Telegram flag/custom emoji when configured;
            # otherwise use the normal country flag.
            flag_html = configured_flag if configured_flag != "🌍" else ISO_TO_FLAG[iso]
        else:
            flag_html = configured_flag if configured_flag != "🌍" else fallback_flag
    else:
        flag_html = configured_flag

    # Language: prefer the API/test supplied language when present; otherwise
    # detect it from the actual SMS body. Never force English when a real
    # language value is supplied by the panel/test.
    lang_hint = str(language_hint or "").strip()
    if lang_hint:
        lang_code = lang_hint.upper()
        if not lang_code.startswith("#"):
            lang_code = "#" + lang_code
        lang_name = LANG_MAP.get(lang_code, lang_hint.lstrip("#").strip()) if 'LANG_MAP' in globals() else lang_hint.lstrip("#").strip()
    else:
        lang_code = detect_language(sms_text)
        lang_name = LANG_MAP.get(lang_code, "") if 'LANG_MAP' in globals() else str(lang_code).replace("#", "")
    if not lang_name:
        # Only use English when there is genuinely no language information.
        lang_name = "English"

    country_short = _math_italic_upper(iso)
    language_styled = _math_italic_text(lang_name)

    # Prefix is kept exactly as the existing Prefix system provides it.
    exact_digits = re.sub(r"\D", "", str(raw_number))
    prefix8 = exact_digits[:8]
    prefix_line = (
        f'🔢 Prefix: <a href="tg://copy?text={prefix8}"><code>{prefix8}</code></a>'
        if prefix8 else "🔢 Prefix: <code>-</code>"
    )

    # Canonical layout supplied by the user:
    # ╔════════════════╗
    #      ➡️❝𝐀 𝐇 𝐑 𝐕𝐈𝐏 𝐎𝐓𝐏❞⬅️
    #          🔥❤️ SERVICE ❤️🔥
    # 🇰🇿 +72552🅁🄾🄽🅈-8152
    #            (𝘒𝘡).𝘌𝘯𝘨𝘭𝘪𝘴𝘩
    # ╚════════════════╝
    # 🔢 Prefix: 72552928
    #
    # Exact placement from the user's final reference. NBSP keeps the
    # intentional spacing intact in Telegram. The 16-character frame and
    # border are never changed by the service name.
    service_content = f"🔥❤️ {service_line} ❤️🔥"
    # Center the complete service group. Short names get more side spacing,
    # while long names are kept safely inside the body instead of being
    # pushed/pressed against the left edge.
    nbsp = "\u00a0"
    visible_service = re.sub(r"<[^>]+>", "", service_content)
    target_width = 24
    left_pad = max(2, min(10, (target_width - len(visible_service)) // 2))
    centered_service = (nbsp * left_pad) + service_content
    border_top = "╔════════════════╗"
    border_bottom = "╚════════════════╝"

    body = (
        f"{border_top}\n"
        "     ➡️❝𝐀 𝐇 𝐑 𝐕𝐈𝐏 𝐎𝐓𝐏❞⬅️\n"
        f"{centered_service}\n"
        f" {flag_html} {styled_number}\n"
        f"           ({country_short}).{language_styled}\n"
        f"{border_bottom}\n"
        f"{prefix_line}"
    )
    return render_body_text(body)

def build_otp_forward_keyboard(otp, forward_group=None):
    """OTP copy button plus the requested Number and Channel buttons."""
    kb = [[{
        "text": f"{otp}",
        "icon_custom_emoji_id": "5353022963132174959",
        "copy_text": {"text": str(otp)},
        "style": "success"
    }]]

    number_url = get_running_bot_url()
    channel_url = str(bot_settings.get("otp_channel_url", "")).strip()
    row = [{"text": "🤖 Number", "url": number_url, "style": "danger"}]
    if channel_url:
        row.append({"text": "📢 Channel", "url": channel_url, "style": "success"})
    else:
        row.append({"text": "📢 Channel", "callback_data": "otp_channel_not_set", "style": "success"})
    kb.append(row)
    for btn in bot_settings.get("otp_extra_buttons", []):
        text = str(btn.get("text", "")).strip()
        url = str(btn.get("url", "")).strip()
        if text and url:
            row = {"text": text, "url": url, "style": "primary"}
            row["icon_custom_emoji_id"] = str(btn.get("icon_custom_emoji_id") or "5420517437885943844")
            kb.append([row])
    return {"inline_keyboard": kb}

def detect_language(text):
    if not text: return "#EN"
    text_str = str(text)

    # ১. Unicode Block দিয়ে নিখুঁত বর্ণমালা শনাক্তকরণ (100% Accurate for scripts)
    if any('\u0600' <= c <= '\u06ff' for c in text_str): return "#AR" # Arabic / Persian / Urdu
    if any('\u0980' <= c <= '\u09ff' for c in text_str): return "#BN" # Bengali
    if any('\u0900' <= c <= '\u097f' for c in text_str): return "#HI" # Hindi / Marathi / Nepali
    if any('\u0a00' <= c <= '\u0a7f' for c in text_str): return "#PA" # Punjabi (Gurmukhi)
    if any('\u0a80' <= c <= '\u0aff' for c in text_str): return "#GU" # Gujarati
    if any('\u0b00' <= c <= '\u0b7f' for c in text_str): return "#OR" # Odia
    if any('\u0b80' <= c <= '\u0bff' for c in text_str): return "#TA" # Tamil
    if any('\u0c00' <= c <= '\u0c7f' for c in text_str): return "#TE" # Telugu
    if any('\u0c80' <= c <= '\u0cff' for c in text_str): return "#KN" # Kannada
    if any('\u0d00' <= c <= '\u0d7f' for c in text_str): return "#ML" # Malayalam
    if any('\u0d80' <= c <= '\u0dff' for c in text_str): return "#SI" # Sinhala
    if any('\u0e00' <= c <= '\u0e7f' for c in text_str): return "#TH" # Thai
    if any('\u0e80' <= c <= '\u0eff' for c in text_str): return "#LO" # Lao
    if any('\u0f00' <= c <= '\u0fff' for c in text_str): return "#BO" # Tibetan
    if any('\u1000' <= c <= '\u109f' for c in text_str): return "#MY" # Burmese (Myanmar)
    if any('\u1200' <= c <= '\u137f' for c in text_str): return "#AM" # Amharic (Ethiopic)
    if any('\u1780' <= c <= '\u17ff' for c in text_str): return "#KM" # Khmer
    if any('\u10a0' <= c <= '\u10ff' for c in text_str): return "#KA" # Georgian
    if any('\u0530' <= c <= '\u058f' for c in text_str): return "#HY" # Armenian
    if any('\u0590' <= c <= '\u05ff' for c in text_str): return "#HE" # Hebrew
    if any('\u0370' <= c <= '\u03ff' for c in text_str): return "#EL" # Greek
    if any('\u0400' <= c <= '\u04ff' for c in text_str): return "#RU" # Russian / Ukrainian (Cyrillic)
    if any('\u4e00' <= c <= '\u9fff' for c in text_str): return "#ZH" # Chinese
    if any('\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' for c in text_str): return "#JA" # Japanese
    if any('\uac00' <= c <= '\ud7af' for c in text_str): return "#KO" # Korean

    # ২. OTP Keyword দিয়ে ভাষা শনাক্তকরণ (Latin script languages)
    text_lower = text_str.lower()
    
    # Asian / Pacific
    if any(w in text_lower for w in ["kode verifikasi", "jangan bagikan", "rahasia"]): return "#ID" # Indonesian
    if any(w in text_lower for w in ["kod pengesahan", "jangan kongsi"]): return "#MS" # Malay
    if any(w in text_lower for w in ["mã của bạn", "không chia sẻ", "mã xác minh"]): return "#VN" # Vietnamese
    if any(w in text_lower for w in ["ang iyong code", "huwag ibahagi"]): return "#TL" # Tagalog / Filipino
    
    # European / Americas
    if any(w in text_lower for w in ["código", "tu código", "verificación", "no compartas"]): return "#ES" # Spanish
    if any(w in text_lower for w in ["seu código", "código de verificação", "não compartilhe"]): return "#PT" # Portuguese
    if any(w in text_lower for w in ["code secret", "ne partagez pas", "votre code"]): return "#FR" # French
    if any(w in text_lower for w in ["dein code", "bestätigungscode", "nicht teilen"]): return "#DE" # German
    if any(w in text_lower for w in ["il tuo codice", "codice di verifica", "non condividere"]): return "#IT" # Italian
    if any(w in text_lower for w in ["twój kod", "nie udostępniaj", "kod weryfikacyjny"]): return "#PL" # Polish
    if any(w in text_lower for w in ["doğrulama kodu", "paylaşmayın", "onay kodu"]): return "#TR" # Turkish
    if any(w in text_lower for w in ["jouw code", "verificatiecode", "niet delen"]): return "#NL" # Dutch
    if any(w in text_lower for w in ["din kod", "verifieringskod", "dela inte"]): return "#SV" # Swedish
    if any(w in text_lower for w in ["bekræftelseskode", "del ikke"]): return "#DA" # Danish
    if any(w in text_lower for w in ["bekreftelseskode", "ikke del"]): return "#NO" # Norwegian
    if any(w in text_lower for w in ["vahvistuskoodi", "älä jaa"]): return "#FI" # Finnish
    if any(w in text_lower for w in ["váš kód", "ověřovací kód", "nesdílejte"]): return "#CS" # Czech
    if any(w in text_lower for w in ["overovací kód", "nezdieľajte"]): return "#SK" # Slovak
    if any(w in text_lower for w in ["ellenőrző kód", "ne oszd meg"]): return "#HU" # Hungarian
    if any(w in text_lower for w in ["codul tău", "codul de verificare", "nu partaja"]): return "#RO" # Romanian
    if any(w in text_lower for w in ["kontrolni kod", "kod za potvrdu", "ne delite"]): return "#HR" # Croatian/Serbian
    if any(w in text_lower for w in ["код за потвърждение", "не споделяйте"]): return "#BG" # Bulgarian
    if any(w in text_lower for w in ["ваш код", "код підтвердження"]): return "#UK" # Ukrainian
    
    # African
    if any(w in text_lower for w in ["msimbo wako", "usishiriki"]): return "#SW" # Swahili
    if any(w in text_lower for w in ["verifikasiekode", "moenie deel nie"]): return "#AF" # Afrikaans
    
    # ৩. উপরের কোনোটি না মিললে ডিফল্ট
    return "#EN"

def parse_force_join_entry(text):
    """Store public channels as @username.
    For private channels use: -1001234567890 | https://t.me/+InviteHash
    """
    text = str(text).strip()

    # Private channel: numeric Telegram chat ID + optional invite URL.
    if "|" in text:
        chat_id, invite_url = [x.strip() for x in text.split("|", 1)]
        if chat_id.startswith("-100") and invite_url.startswith("https://t.me/"):
            return {"chat_id": chat_id, "url": invite_url}

    # Numeric private channel ID without an invite URL.
    if text.startswith("-100"):
        return {"chat_id": text, "url": ""}

    # Public username or public t.me URL.
    if "t.me/" in text:
        tail = text.split("t.me/", 1)[1].split("?", 1)[0].strip("/")
        if tail.startswith("+") or tail.startswith("joinchat/"):
            # An invite link alone cannot be used with getChatMember.
            return None
        if tail:
            return {"chat_id": "@" + tail.lstrip("@"), "url": "https://t.me/" + tail.lstrip("@")}

    if text.startswith("@"):
        username = text.split()[0]
        return {"chat_id": username, "url": "https://t.me/" + username.lstrip("@")}

    if re.fullmatch(r"[A-Za-z0-9_]{5,}", text):
        return {"chat_id": "@" + text, "url": "https://t.me/" + text}

    return None

# Backward-compatible helper for old configs.
def parse_chat_id(text):
    entry = parse_force_join_entry(text)
    if isinstance(entry, dict):
        return entry["chat_id"]
    return None

def _fj_chat_id(entry):
    if isinstance(entry, dict):
        return str(entry.get("chat_id", "")).strip()
    return str(entry).strip()

def _fj_join_url(entry):
    if isinstance(entry, dict):
        return str(entry.get("url", "")).strip()
    ch = str(entry).strip()
    if ch.startswith("@"):
        return "https://t.me/" + ch.lstrip("@")
    if ch.startswith("https://t.me/") and not "/+" in ch:
        return ch
    return ""

def is_admin(user_id):
    return user_id in bot_settings["admins"] or user_id == OWNER_ID

def check_force_join(user_id):
    if not bot_settings.get("fj_on") or not bot_settings.get("fj_channels"):
        return True
    if is_admin(user_id):
        return True

    for entry in bot_settings["fj_channels"]:
        ch = _fj_chat_id(entry)
        if not ch:
            return False

        res = api_call("getChatMember", {"chat_id": ch, "user_id": user_id})

        # Never treat an API error as a successful join.
        if not res.get("ok"):
            print(f"[FORCE JOIN] getChatMember failed for {ch}: {res.get('description', 'unknown error')}")
            return False

        member = res.get("result", {})
        status = member.get("status")

        # Creator/admin/member are joined. A restricted user is joined only
        # when Telegram explicitly says is_member=True.
        if status in ("creator", "administrator", "member"):
            continue
        if status == "restricted" and member.get("is_member") is True:
            continue

        return False

    return True

def send_force_join_msg(chat_id):
    kb = []
    for entry in bot_settings["fj_channels"]:
        url = _fj_join_url(entry)
        if url:
            kb.append([{"text": "Join Channel", "icon_custom_emoji_id": "5789428375261023681",
                        "url": url, "style": "primary"}])
        else:
            kb.append([{"text": "Join Channel (link not configured)", "icon_custom_emoji_id": "5789428375261023681",
                        "callback_data": "fj_link_missing", "style": "primary"}])

    kb.append([{"text": "Check Joined", "icon_custom_emoji_id": "5352694861990501856",
                "callback_data": "check_fj", "style": "success"}])
    send_message(chat_id, render_body_text(
        f"{PEM['warn']} <b>Please join all required channels to use the bot.</b>\n"
        f"After joining, tap <b>Check Joined</b>."
    ), reply_markup={"inline_keyboard": kb})

def is_user_banned(user_id):
    if is_admin(user_id): return False
    if user_id in user_banned_cache and time.time() - user_banned_cache[user_id]['time'] < 60:
        return user_banned_cache[user_id]['banned']
    banned = str(user_id) in local_banned_users
    if db:
        try:
            doc = db.collection('users').document(str(user_id)).get()
            if doc.exists:
                banned = bool(doc.to_dict().get("banned", False))
        except Exception as e:
            print(f"[BAN] Firestore read error for {user_id}: {e}")
    user_banned_cache[user_id] = {'banned': banned, 'time': time.time()}
    return banned

# ==========================================
# Captcha Auto Login & Parsing Core
# ==========================================
def extract_otp_code(text):
    clean_text = re.sub(r'[\u200B-\u200D\uFEFF]', '', str(text))

    # 1. Multi-part OTPs (e.g. 123-456 or 809-761)
    multi_part = re.search(r'(\d{3}[-\s]+\d{3})|(\d{2}[-\s]+\d{2}[-\s]+\d{2})', clean_text)
    if multi_part:
        # হাইফেন (-) থাকলে সেটা রেখে দিবে, কিন্তু স্পেস থাকলে মুছে একসাথে করে দিবে
        return multi_part.group(0).replace(" ", "")

    # 2. Keyword-based extraction
    otp_keywords = ['code', 'is', 'otp', 'pin', 'verification', 'auth', 'কোড', 'رمز', 'your code']
    keywords_pattern = '|'.join(otp_keywords)
    keyword_match = re.search(rf'(?:{keywords_pattern})\s*(?:is|:|-|=)?\s*([a-z0-9]{{4,10}})', clean_text, re.I)
    if keyword_match and keyword_match.group(1).isdigit():
        return keyword_match.group(1)
        
    keyword_match_rev = re.search(rf'([a-z0-9]{{4,10}})\s*(?:is your|is the|কোড)', clean_text, re.I)
    if keyword_match_rev and keyword_match_rev.group(1).isdigit():
        return keyword_match_rev.group(1)

    # 3. Google OTP
    g_match = re.search(r'G-(\d{6})', clean_text, re.IGNORECASE)
    if g_match: return g_match.group(1)

    # 4. Digit sequences fallback
    digit_matches = re.findall(r'(?<!\d)\d{4,8}(?!\d)', clean_text)
    if digit_matches: return digit_matches[0]

    return None

def parse_panel_response(response_text, p_config=None):
    """Parse OTP records and preserve the actual service/app attached to each received record."""
    results = []
    p_type = p_config.get("type", "API Panel") if p_config else "API Panel"
    n_col_name = p_config.get("num_col_name", "number").lower() if p_config else "number"
    m_col_name = p_config.get("msg_col_name", "message").lower() if p_config else "message"
    n_idx = int(p_config.get("num_col_idx", 1)) - 1 if p_config and p_config.get("num_col_idx") else 1
    m_idx = int(p_config.get("msg_col_idx", 2)) - 1 if p_config and p_config.get("msg_col_idx") else 2

    # Keys that commonly carry the actual OTP service/application in API responses.
    SERVICE_KEYS = {
        "service", "service_name", "servicename", "service_title", "servicetitle", "service_label",
        "app", "app_name", "appname", "app_title", "application", "application_name", "applicationname",
        "product", "product_name", "project", "platform", "site", "website", "provider_service",
        "serviceinfo", "service_info", "service_data", "service_details", "applicationinfo", "appinfo", "serviceid", "service_id", "app_id", "appcode", "app_code", "servicecode", "service_code", "operator", "brand", "sender_name", "sendername", "source", "category", "network"
    }
    SERVICE_OBJECT_KEYS = ("name", "title", "label", "display_name", "service", "service_name", "app", "app_name", "application", "product")

    def service_from_value(v):
        if isinstance(v, dict):
            low = {str(k).lower(): val for k, val in v.items()}
            for k in SERVICE_OBJECT_KEYS:
                if k in low:
                    got = service_from_value(low[k])
                    if got:
                        return got
            for val in v.values():
                got = service_from_value(val)
                if got:
                    return got
            return ""
        if isinstance(v, list):
            for x in v:
                got = service_from_value(x)
                if got:
                    return got
            return ""
        return _normalize_service_value(v)

    def find_service_metadata(node):
        """Recursively inspect a record and nested metadata for the real service field."""
        if not isinstance(node, dict):
            return ""
        lower = {str(k).lower(): v for k, v in node.items()}
        # Exact service/application keys have highest priority.
        for k in SERVICE_KEYS:
            if k in lower:
                got = service_from_value(lower[k])
                if got:
                    return got
        # Some APIs put service metadata inside a named object.
        for k, v in lower.items():
            if any(token in k for token in ("service", "application", "app", "product")) and isinstance(v, (dict, list)):
                got = service_from_value(v)
                if got:
                    return got
        # Nested dictionaries are checked, but only for service-related metadata.
        for v in node.values():
            if isinstance(v, dict):
                got = find_service_metadata(v)
                if got:
                    return got
        return ""

    if p_type == "Auto Captcha Panel":
        try:
            soup = BeautifulSoup(response_text, 'html.parser')
            for table in soup.find_all('table'):
                rows = table.find_all('tr')
                if not rows:
                    continue
                final_n_idx, final_m_idx, final_s_idx = n_idx, m_idx, None
                header_cells = rows[0].find_all(['th', 'td'])
                for i, cell in enumerate(header_cells):
                    c_text = cell.get_text(separator=" ", strip=True).lower()
                    if n_col_name in c_text:
                        final_n_idx = i
                    if m_col_name in c_text:
                        final_m_idx = i
                    if any(k in c_text for k in ("service", "app", "application", "product", "platform", "site")):
                        final_s_idx = i
                for row in rows:
                    cols = row.find_all(['td', 'th'])
                    if not cols or all(c.name == 'th' for c in cols):
                        continue
                    if len(cols) <= max(final_n_idx, final_m_idx):
                        continue
                    num_text = cols[final_n_idx].get_text(separator=" ", strip=True)
                    msg_text = cols[final_m_idx].get_text(separator=" ", strip=True)
                    clean_num = re.sub(r'\D', '', num_text)
                    if clean_num and 5 <= len(clean_num) <= 18:
                        otp = extract_otp_code(msg_text)
                        if otp and len(msg_text) > 4:
                            service = ""
                            if final_s_idx is not None and final_s_idx < len(cols):
                                service = _normalize_service_value(cols[final_s_idx].get_text(separator=" ", strip=True))
                            if not service:
                                service = detect_service(msg_text) or ""
                            results.append({"number": clean_num, "message": msg_text, "otp": otp, "service": service})
        except Exception:
            pass
    else:
        try:
            data = json.loads(response_text)
            temp_results = []

            def process_item(item):
                pot_nums_list, pot_msg = [], None
                pot_service = find_service_metadata(item) if isinstance(item, dict) else ""
                pot_language = ""
                values = list(item.values()) if isinstance(item, dict) else (item if isinstance(item, list) else [])
                if isinstance(item, dict):
                    lower_keys = {str(k).lower(): v for k, v in item.items()}
                    for k in ("language", "lang", "language_name", "lang_name", "sms_language", "message_language", "locale"):
                        if k in lower_keys and str(lower_keys[k]).strip():
                            pot_language = str(lower_keys[k]).strip()
                            break

                if isinstance(item, dict):
                    lower_keys = {str(k).lower(): v for k, v in item.items()}
                    for k in ["number", "num", "phone", "msisdn", "sender", "mobile", "mobile_number", "phone_number"]:
                        if k in lower_keys:
                            clean_val = re.sub(r'\D', '', str(lower_keys[k]))
                            if 5 <= len(clean_val) <= 18 and clean_val not in pot_nums_list:
                                pot_nums_list.append(clean_val)
                    for k in ["message", "msg", "sms", "content", "text", "body", "sms_text", "message_text"]:
                        if k in lower_keys:
                            val = str(lower_keys[k])
                            if len(val) > 4:
                                pot_msg = val
                                break

                for v in values:
                    if isinstance(v, (dict, list)) or v is None:
                        continue
                    v_str = str(v).strip()
                    clean_v = re.sub(r'\D', '', v_str)
                    if 7 <= len(clean_v) <= 18 and not re.search(r'[a-zA-Z]', v_str):
                        if not re.search(r'\d{4}[-/]\d{2}[-/]\d{2}', v_str) and not re.search(r'\d{2}:\d{2}:\d{2}', v_str) and "." not in v_str:
                            if clean_v not in pot_nums_list:
                                pot_nums_list.append(clean_v)
                    if len(v_str) > 4 and not v_str.isdigit() and extract_otp_code(v_str):
                        if pot_msg is None or len(v_str) > len(pot_msg):
                            pot_msg = v_str

                if pot_msg and not pot_service:
                    pot_service = detect_service(pot_msg) or ""

                pot_num = None
                if pot_nums_list:
                    for n in pot_nums_list:
                        if n in stex_assigned_numbers or any(n in str(key) for key in stex_assigned_numbers.keys()):
                            pot_num = n
                            break
                    if not pot_num:
                        pot_num = pot_nums_list[1] if len(pot_nums_list) >= 2 else pot_nums_list[0]

                if pot_num and pot_msg:
                    otp = extract_otp_code(pot_msg)
                    if otp:
                        temp_results.append({"number": pot_num, "message": pot_msg, "otp": otp, "service": pot_service, "language": pot_language})

            def traverse_json(node):
                if isinstance(node, list):
                    if node and not isinstance(node[0], (dict, list)):
                        process_item(node)
                    for child in node:
                        if isinstance(child, (dict, list)):
                            traverse_json(child)
                elif isinstance(node, dict):
                    process_item(node)
                    for val in node.values():
                        if isinstance(val, (dict, list)):
                            traverse_json(val)

            traverse_json(data)
            seen = set()
            for r in temp_results:
                uid = f"{r['number']}_{r['otp']}_{r.get('service','')}"
                if uid not in seen:
                    seen.add(uid)
                    results.append(r)
        except Exception:
            pass
    return results

def api_panel_is_configured(p):
    """Return True when an API panel has a usable URL configuration."""
    full_url = str(p.get("full_api_url", "") or "").strip()
    api_url = str(p.get("api_url", "") or "").strip()
    token = str(p.get("token", "") or "").strip()
    if full_url:
        return full_url.startswith(("http://", "https://"))
    if not api_url:
        return False
    # URL may already contain the credential placeholder/query parameter.
    if "{token}" in api_url or "{key}" in api_url or "token=" in api_url or "key=" in api_url:
        return True
    return bool(token)

# 🌟 Advanced Automated Background Captcha Solver 🌟
def attempt_auto_login(p, idx):
    login_url = p.get("login_url", "").strip()
    if not login_url.startswith("http"):
        login_url = "http://" + login_url
        
    if not login_url.lower().endswith('/login') and not login_url.lower().endswith('.php'):
        login_url = f"{login_url.rstrip('/')}/login"
        
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    })
    
    try:
        res = session.get(login_url, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        all_text = res.text
        
        # 1. SOLVE CAPTCHA (Exact bot 3.py logic)
        captcha_match = re.search(r'(\d+\s*[\+\-\*]\s*\d+)\s*[=\?:]', all_text)
        if not captcha_match:
            captcha_match = re.search(r'what is\s*(\d+\s*[\+\-\*]\s*\d+)', all_text, re.I)
        if not captcha_match:
            elements = soup.find_all(["label", "div", "span", "p", "strong"])
            for el in elements:
                txt = el.get_text(separator=" ", strip=True)
                if any(op in txt for op in ["+", "-", "*"]):
                    m = re.search(r'(\d+\s*[\+\-\*]\s*\d+)', txt)
                    if m:
                        captcha_match = m
                        break
                        
        captcha_text = captcha_match.group(1) if captcha_match else "0 + 0"
        answer = "0"
        m2 = re.search(r'(\d+)\s*([\+\-\*])\s*(\d+)', captcha_text)
        if m2:
            a, op, b = int(m2.group(1)), m2.group(2), int(m2.group(3))
            if op == '+': answer = str(a + b)
            elif op == '-': answer = str(a - b)
            elif op == '*': answer = str(a * b)

        # 2. FIND FORM
        form = soup.find("form")
        if not form:
            p["login_status"] = "❌ No login form found"
            return False
            
        action = form.get("action")
        from urllib.parse import urljoin
        post_url = urljoin(login_url, action) if action else login_url

        form_data = {}
        for hidden in form.find_all("input", type="hidden"):
            name = hidden.get("name")
            if name: form_data[name] = hidden.get("value") or ""
        
        user_input = form.find("input", {"name": re.compile(r"user|email|id", re.I)}) or \
                     form.find("input", {"type": "text", "placeholder": re.compile(r"user|email", re.I)}) or \
                     form.find("input", {"type": "text"})
                     
        pass_input = form.find("input", {"name": re.compile(r"pass", re.I)}) or \
                     form.find("input", {"type": "password"})
                     
        captcha_input = form.find("input", {"placeholder": re.compile(r"answer|ans|code|verification|value|captcha", re.I)}) or \
                        form.find("input", {"name": re.compile(r"ans|captcha|ver|code", re.I)})
        
        user_field = user_input.get("name") if user_input else "username"
        pass_field = pass_input.get("name") if pass_input else "password"
        captcha_field = captcha_input.get("name") if captcha_input else "answer"

        form_data[user_field] = p.get("username", "")
        form_data[pass_field] = p.get("password", "")
        if captcha_field:
            form_data[captcha_field] = answer

        # 3. SUBMIT
        login_req = session.post(post_url, data=form_data, allow_redirects=True, timeout=15)
        
        # 4. VERIFY (Exact bot 3.py check logic)
        msg_link = p.get("msg_link", "").strip()
        if not msg_link.startswith("http") and msg_link != "":
            msg_link = "http://" + msg_link
            
        check_url = msg_link if msg_link else f"{login_url.split('/login')[0]}/client/SMSCDRStats"
        
        check_res = session.get(check_url, timeout=10)
        
        if 'logout' in login_req.text.lower() or 'logout' in check_res.text.lower() or 'sms reports' in check_res.text.lower() or 'dashboard' in check_res.text.lower() or 'cdrs' in check_res.text.lower():
            panel_sessions[idx] = session
            p["login_status"] = "✅ Active & Fetching"
            return True
        else:
            # এখানে ফেইল হলে অংক কী পেয়েছিল তা দেখা যাবে
            p["login_status"] = f"❌ Login Failed (Math: {captcha_text} = {answer})"
            return False
            
    except Exception as e:
        p["login_status"] = f"❌ Error: {str(e)[:20]}"
        
    return False

def panel_monitor_thread():
    global processed_otps, recent_traffic, panel_sessions
    while True:
        try:
            for idx, p in enumerate(bot_settings.get("panels", [])):
                if p.get("status") == "ON":
                    
                    if p.get("type") == "Auto Captcha Panel":
                        sess = panel_sessions.get(idx)
                        
                        if not sess:
                            now = time.time()
                            if now - p.get("last_login_attempt", 0) < 30: 
                                continue 
                            p["last_login_attempt"] = now
                            
                            success = attempt_auto_login(p, idx)
                            save_db() # Save login status text to show in settings
                            if not success:
                                continue 
                            sess = panel_sessions.get(idx)
                            
                        try:
                            # 🌟 auto sessions with sAjaxSource and Fallback HTML Parser
                            parsed_data, res_text = fetch_cpt_panel_cdrs(p, sess, p["msg_link"])
                            p["login_status"] = "✅ Active & Fetching"
                        except Exception as e:
                            p["login_status"] = "❌ Session Expired (Retrying...)"
                            del panel_sessions[idx]
                            save_db()
                            continue

                    elif p.get("api_url") or p.get("full_api_url"): 
                        full_url = p.get("full_api_url", "").strip()
                        url = p.get("api_url", "").strip()
                        token = p.get("token", "").strip()
                        if not full_url and not url: continue
                        
                        urls_to_try = []
                        if full_url:
                            urls_to_try.append(full_url)
                        else:
                            if "{token}" in url or "{key}" in url:
                                urls_to_try.append(url.replace("{token}", token).replace("{key}", token))
                            elif "token=" in url or "key=" in url:
                                urls_to_try.append(url)
                            else:
                                sep = '&' if '?' in url else '?'
                                urls_to_try.append(f"{url}{sep}token={token}")
                                urls_to_try.append(f"{url}{sep}key={token}&start=0")
                                urls_to_try.append(f"{url}{sep}key={token}")
                            
                        parsed_data = []
                        # 🌟 Browser Bypass (403 Forbidden Fix)
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                        for try_url in urls_to_try:
                            try:
                                res = requests.get(try_url, headers=headers, timeout=10)
                                if 200 <= res.status_code < 300:
                                    p["api_status"] = "✅ API Connected"
                                else:
                                    p["api_status"] = f"❌ HTTP {res.status_code}"
                                parsed_data = parse_panel_response(res.text, p)
                                if parsed_data:
                                    if not full_url and try_url != url and token:
                                        p["api_url"] = try_url.replace(token, "{token}")
                                        save_db()
                                    break
                            except: continue
                        if not parsed_data: continue
                    else:
                        continue
                    
                    if p.get("type") != "Auto Captcha Panel":
                        limit = p.get("records", 0)
                        if limit > 0: parsed_data = parsed_data[:limit]
                        
                    for item in parsed_data:
                        num = item["number"]
                        otp = item["otp"]
                        msg_text = item["message"]
                        language_hint = str(item.get("language", "") or "").strip()
                        unique_id = f"{num}_{otp}"
                        
                        if unique_id not in processed_otps:
                            processed_otps.add(unique_id)
                            if len(processed_otps) > 5000: processed_otps.clear()
                                 
                            char, iso = get_flag_and_code(num)
                            item_service = str(item.get("service", "") or "").strip()
                            # Always resolve the real requested service from the SMS/number mapping.
                            # A panel/provider name is never allowed here.
                            item_service = resolve_real_service(num, item_service, msg_text)
                            app_full_name, prem_app_html = get_service_info_html(item_service, msg_text)
                            current_time = time.time()
                            
                            recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                            recent_traffic.append({
                                "service": app_full_name,
                                "iso": iso,
                                "flag": char,
                                "number": num,
                                "time": current_time
                            })
                            # 🌟 শুধু লোকাল ফাইলে সেভ করবে, Firestore এ অহেতুক Write করবে না!
                            save_local_db()
                                 
                            display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                            masked = mask_number(display_num)
                            lang = detect_language(msg_text)
                            
                            lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
                            display_msg = format_otp_forward_body(display_num, item_service, msg_text, language_hint)
                            
                            for fw in bot_settings["fw_groups"]:
                                send_message(fw["chat_id"], display_msg, reply_markup=build_otp_forward_keyboard(otp, fw))
                            
                            owners = []
                            clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                            
                            # 🌟 ALGORITHM FIX: সরাসরি Active Sessions থেকে মালিক খোঁজা 
                            # (কারণ Local Stock থেকে নাম্বার Assign হওয়ার সাথে সাথে ডিলিট হয়ে যায়)
                            for uid, session_data in user_active_sessions.items():
                                for act_num in session_data.get("nums", []):
                                    act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                    if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                        owners.append(uid)
                                        break
                                        
                            # Persistent local/manual ownership survives batch removal.
                            if not owners:
                                local_assignment = _local_assignment_for_number(num)
                                if local_assignment:
                                    owners.extend(local_assignment.get("owners", []) or [])

                            # ব্যাকআপ হিসেবে StexSMS-তে চেক করা 
                            if not owners:
                                for stex_n, n_owner in stex_assigned_numbers.items():
                                    clean_stex = str(stex_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                    if clean_stex == clean_api_num or (len(clean_stex) >= 8 and clean_stex.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_stex[-8:])):
                                        owners.append(n_owner)
                                        
                            owners = list(set(owners)) 
                            for owner_id in owners:
                                lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
                                # OTP reward is credited automatically and shown as text;
                                # no separate "Added X tk" button is used.
                                reward = float(bot_settings.get("otp_reward", 0.0))
                                if reward > 0:
                                    reward_ok, _, _, reward_err = update_balance(owner_id, reward)
                                    reward_line = f"\n\n💰 OTP Reward: {reward:g} TK" if reward_ok else ""
                                    if not reward_ok:
                                        print(f"[OTP REWARD] Balance update failed for {owner_id}: {reward_err}")
                                else:
                                    reward_line = ""
                                inbox_msg = render_body_text(f"{get_flag_info_html(display_num)} {iso} | {prem_app_html} {display_num} | 💬 {lang_name}{reward_line}")
                                inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
                                send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                                try: increment_received_otps(owner_id, otp_number=display_num)
                                except Exception as e: print(f"[USER STATS] Panel OTP counter failed for {owner_id}: {e}")
        except Exception as e:
            pass
        time.sleep(5) 

# ==========================================
# Firebase User Management
# ==========================================
# 🌟 Local User Cache: বারবার Firestore থেকে Read করা বন্ধ করবে!
user_cache = {}

# Persistent fallback for per-user counters. This is used only when Firestore
# is unavailable or a counter write cannot be completed, so the Admin User List
# does not silently fall back to zero after a restart.
USER_STATS_FILE = "user_stats.json"
_user_stats_lock = threading.Lock()
user_stats_local = {}

def _load_local_user_stats():
    global user_stats_local
    try:
        if os.path.exists(USER_STATS_FILE):
            with open(USER_STATS_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            if isinstance(raw, dict):
                user_stats_local = {str(k): (v if isinstance(v, dict) else {}) for k, v in raw.items()}
    except Exception:
        user_stats_local = {}

def _save_local_user_stats():
    try:
        tmp = USER_STATS_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(user_stats_local, f, indent=2)
        os.replace(tmp, USER_STATS_FILE)
    except Exception:
        pass

def _local_counter_value(user_id, field):
    with _user_stats_lock:
        try:
            return int(user_stats_local.get(str(user_id), {}).get(field, 0) or 0)
        except Exception:
            return 0

def _increment_local_counter(user_id, field, count=1):
    with _user_stats_lock:
        uid = str(user_id)
        row = user_stats_local.setdefault(uid, {})
        try:
            row[field] = int(row.get(field, 0) or 0) + int(count)
        except Exception:
            row[field] = int(count)
        _save_local_user_stats()
        return row[field]

_load_local_user_stats()

def get_user(user_id):
    if user_id in user_cache: return user_cache[user_id]
    if not db:
        return {"user_id": user_id, "balance": float(user_balances_local.get(str(user_id), 0.0) or 0.0), "total_refers": 0,
                "total_otps": _local_counter_value(user_id, "total_otps"),
                "numbers_used": _local_counter_value(user_id, "numbers_used")}
    
    doc_ref = db.collection('users').document(str(user_id))
    doc = doc_ref.get()
    if doc.exists: 
        data = doc.to_dict()
        if "total_otps" not in data: data["total_otps"] = 0
        if "numbers_used" not in data: data["numbers_used"] = 0
        if "banned" not in data: data["banned"] = False
        if "verified" not in data: data["verified"] = False
        user_cache[user_id] = data
        return data
    else:
        new_user = {"user_id": user_id, "balance": 0.0, "total_refers": 0, "total_otps": 0, "numbers_used": 0, "banned": False, "verified": False}
        doc_ref.set(new_user)
        user_cache[user_id] = new_user
        return new_user

USER_BALANCES_FILE = "user_balances_local.json"
_user_balances_lock = threading.Lock()
user_balances_local = {}

def _load_local_balances():
    global user_balances_local
    try:
        if os.path.exists(USER_BALANCES_FILE):
            with open(USER_BALANCES_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            if isinstance(raw, dict):
                user_balances_local = {str(k): float(v or 0) for k, v in raw.items()}
    except Exception as e:
        print(f"[BALANCE] Local balance load failed: {e}")
        user_balances_local = {}

def _save_local_balances():
    try:
        tmp = USER_BALANCES_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(user_balances_local, f, indent=2)
        os.replace(tmp, USER_BALANCES_FILE)
    except Exception as e:
        print(f"[BALANCE] Local balance save failed: {e}")

_load_local_balances()

def update_balance(user_id, amount):
    """Reliably add/remove balance and return (success, old_balance, new_balance, error)."""
    uid = str(user_id)
    amount = float(amount)

    # Firebase is authoritative when configured. Read current value, write the new
    # absolute value, then verify it. This prevents a silent 'success' when the
    # Firebase write fails.
    if db:
        try:
            doc_ref = db.collection('users').document(uid)
            doc = doc_ref.get()
            if not doc.exists:
                return False, 0.0, 0.0, "User not found in Firebase."
            data = doc.to_dict() or {}
            old_balance = float(data.get("balance", 0) or 0)
            new_balance = old_balance + amount
            doc_ref.set({"user_id": int(user_id), "balance": new_balance}, merge=True)
            verify = doc_ref.get()
            verify_balance = float((verify.to_dict() or {}).get("balance", 0) or 0)
            if abs(verify_balance - new_balance) > 1e-9:
                return False, old_balance, verify_balance, f"Firebase verification failed (saved {verify_balance}, expected {new_balance})."
            user_cache[int(user_id)] = dict(verify.to_dict() or {})
            user_cache[int(user_id)]["balance"] = verify_balance
            return True, old_balance, verify_balance, ""
        except Exception as e:
            print(f"[BALANCE] Firebase update failed for {uid}: {e}")
            return False, 0.0, 0.0, str(e)

    # Firebase unavailable: persist the balance locally instead of silently returning.
    with _user_balances_lock:
        old_balance = float(user_balances_local.get(uid, user_cache.get(int(user_id), {}).get("balance", 0) if int(user_id) in user_cache else 0) or 0)
        new_balance = old_balance + amount
        user_balances_local[uid] = new_balance
        _save_local_balances()
    if int(user_id) not in user_cache:
        user_cache[int(user_id)] = {"user_id": int(user_id), "balance": new_balance}
    else:
        user_cache[int(user_id)]["balance"] = new_balance
    return True, old_balance, new_balance, ""

def increment_numbers_used(user_id, count=1):
    """Record every successfully assigned number without changing allocation logic."""
    try:
        count = int(count)
        if count <= 0:
            return
        # Persist locally first so the counter survives Firestore/API failures.
        new_local = _increment_local_counter(user_id, "numbers_used", count)
        if user_id in user_cache:
            user_cache[user_id]["numbers_used"] = max(
                int(user_cache[user_id].get("numbers_used", 0) or 0), new_local
            )
        if db:
            db.collection('users').document(str(user_id)).set({
                "user_id": user_id,
                "numbers_used": firestore.Increment(count)
            }, merge=True)
    except Exception as e:
        print(f"[USER STATS] Numbers Used update failed for {user_id}: {e}")

def increment_received_otps(user_id, count=1, otp_number=None):
    """Record every received OTP and keep the latest OTP number for admin leaderboards."""
    try:
        count = int(count)
        if count <= 0:
            return
        # Persist locally first so the existing OTP counter is not lost when
        # Firestore is temporarily unavailable.
        new_local = _increment_local_counter(user_id, "total_otps", count)
        if user_id in user_cache:
            user_cache[user_id]["total_otps"] = max(
                int(user_cache[user_id].get("total_otps", 0) or 0), new_local
            )
            if otp_number:
                user_cache[user_id]["last_otp_number"] = str(otp_number)
        if db:
            patch = {
                "user_id": user_id,
                "total_otps": firestore.Increment(count)
            }
            if otp_number:
                patch["last_otp_number"] = str(otp_number)
            db.collection('users').document(str(user_id)).set(patch, merge=True)
    except Exception as e:
        print(f"[USER STATS] Received OTP update failed for {user_id}: {e}")

def update_user_identity(user_id, from_user):
    """Keep name and username current for the admin user list."""
    if not from_user:
        return
    first = str(from_user.get("first_name") or "").strip()
    last = str(from_user.get("last_name") or "").strip()
    full_name = (first + " " + last).strip() or from_user.get("username") or "Unknown User"
    username = str(from_user.get("username") or "").strip().lstrip("@")
    data = {"user_id": user_id, "full_name": full_name, "username": username}
    try:
        if user_id in user_cache:
            user_cache[user_id].update(data)
        if db:
            db.collection('users').document(str(user_id)).set(data, merge=True)
    except Exception:
        pass

def add_referral(inviter_id, new_user_id):
    if not db.collection('users').document(str(new_user_id)).get().exists:
        get_user(new_user_id) 
        reward = bot_settings.get("refer_reward", 0.2)
        update_balance(inviter_id, reward)
        db.collection('users').document(str(inviter_id)).update({"total_refers": firestore.Increment(1)})
        
        # আপনার দেওয়া নতুন ডিজাইন
        ref_msg = (
            f"{PEM['gift']} <b>New Referral !</b>\n"
            f"------------------\n"
            f"🔥 <b>You Received {reward} TK</b>\n"
            f"------------------\n"
            f"{PEM['user']} <b>From User ID:</b> <code>{new_user_id}</code>"
        )
        send_message(inviter_id, render_body_text(ref_msg))

# ==========================================
# UI Keyboards & Menu Builders
# ==========================================
def get_cancel_kb():
    return {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_state", "style": "danger"}]]}

def main_menu(user_id):
    kb = [
        [
            {"text": "GET NUMBER", "icon_custom_emoji_id": "5337132498965010628", "style": "primary"}, 
            {"text": "Search Number", "icon_custom_emoji_id": "5463352748751753567", "style": "primary"}
        ],
        [
            {"text": "TRAFFIC", "icon_custom_emoji_id": "5352877703043258544", "style": "success"}, 
            {"text": "2FA ONLINE", "icon_custom_emoji_id": "5267421176841398765", "style": "primary"}
        ],
        [
            {"text": "Refer", "icon_custom_emoji_id": "5420396762189831222", "style": "success"}, 
            {"text": "WITHDRAWAL", "icon_custom_emoji_id": "5352585194295564660", "style": "danger"}
        ],
        [
            {"text": "SUPPORT", "icon_custom_emoji_id": "5420145051336485498", "style": "primary"}
        ]
    ]
    if is_admin(user_id): 
        kb.append([{"text": "Admin Panel", "icon_custom_emoji_id": "5420155432272438703", "style": "danger"}])
    return {"keyboard": kb, "resize_keyboard": True}

def get_admin_text():
    users_count = len(all_known_users) # 🌟 Zero Cost User Count!
    total_files = len(number_batches)
    available_nums = sum(len(b["numbers"]) for b in number_batches.values())

    txt = f"""
{PEM['admin']} <b>ADMIN CONTROL PANEL</b> {PEM['admin']}
━━━━━━━━━━━━━━━━━━

{PEM['graph']} <b>DATABASE OVERVIEW</b>
— — — — — — — — — —
{PEM['user']} Users      » {users_count}
{PEM['file']} Files      » {total_files}
{PEM['num']} Numbers    » {total_uploaded_stats}
{PEM['ok']} Assigned   » {total_assigned_stats}
{PEM['rocket']} Available  » {available_nums}

{PEM['graph']} <b>STOCK LEVEL</b>
— — — — — — — — — —
[██████░░░░░░░░░] {available_nums} free
"""
    return render_body_text(txt)

def admin_panel_keyboard():
    return {"inline_keyboard": [
        [{"text": "LEADER BOARD SYSTEM", "icon_custom_emoji_id": "5353032893096567467", "callback_data": "lb_main", "style": "success"}],
        [{"text": "USER LIST", "icon_custom_emoji_id": "5193063022226086560", "callback_data": "user_list_0", "style": "primary"}],
        [{"text": "Upload Number", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "upload_num", "style": "primary"},
         {"text": "Delete files", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "delete_files", "style": "danger"}],
        [{"text": "Broadcast", "icon_custom_emoji_id": "5789428375261023681", "callback_data": "broadcast_msg", "style": "success"},
         {"text": "System", "icon_custom_emoji_id": "5420155432272438703", "callback_data": "system_settings", "style": "primary"}],
        [{"text": "Used number", "icon_custom_emoji_id": "5352694861990501856", "callback_data": "show_used", "style": "success"},
         {"text": "Unused number", "icon_custom_emoji_id": "5352597830089347330", "callback_data": "show_unused", "style": "success"}],
        [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]
    ]}

def system_settings_keyboard():
    return {"inline_keyboard": [
        [{"text": "StexSMS Control", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "stex_control", "style": "success"},
         {"text": "Voltx Control", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "voltx_control", "style": "primary"}],
        [{"text": "Force Join System", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "manage_fj", "style": "primary"},
         {"text": "Admin Management", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "manage_admins", "style": "danger"}],
        [{"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "callback_data": "manage_otp_groups", "style": "danger"},
         {"text": "CUSTOM OTP", "icon_custom_emoji_id": "5190781475468915802", "callback_data": "custom_otp", "style": "success"}],
        [{"text": "User Management", "icon_custom_emoji_id": "5193063022226086560", "callback_data": "user_management", "style": "primary"}], 
        [{"text": "Panel MANAGEMENT", "icon_custom_emoji_id": "5336879280578138635", "callback_data": "manage_panels", "style": "danger"},
         {"text": "Subscription", "icon_custom_emoji_id": "5190899075968441286", "callback_data": "dummy_alert", "style": "success"}],
        [{"text": "DXA Control", "icon_custom_emoji_id": "5193100774988617665", "callback_data": "dxa_control", "style": "primary"},
         {"text": "Premium Emoji", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "manage_emojis", "style": "success"}],
        [{"text": "Menu Design", "icon_custom_emoji_id": "5190751148704833975", "callback_data": "menu_design_list", "style": "primary"},
         {"text": "Test", "icon_custom_emoji_id": "5190781475468915802", "callback_data": "test_message_flow", "style": "primary"}], 
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
    ]}

def get_user_management_text():
    # 🌟 Fast & Free User Management Stats!
    total = len(all_known_users)
    
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    txt = f"""➖➖➖➖➖➖➖➖
《 👋 USER VIEW 》
➖➖➖➖➖➖➖➖
📊 LIVE STATISTICS:
➖➖➖➖➖➖➖➖
🫂 TOTAL USERS: {total}
✅ VERIFIED USERS: (Hidden to save DB Cost)
🚫 BANNED USERS: (Hidden to save DB Cost)
➖➖➖➖➖➖➖➖
⌛ UPDATED: {now_str}"""
    return render_body_text(txt)

def user_management_keyboard():
    return {"inline_keyboard": [
        [{"text": "Manage Balance", "icon_custom_emoji_id": "5190576863226933563", "callback_data": "um_manage_balance", "style": "primary"},
         {"text": "Ban/Unban User", "icon_custom_emoji_id": "5334807341109908955", "callback_data": "um_ban_unban", "style": "danger"}],
        [{"text": "User Profile", "icon_custom_emoji_id": "5352861489541714456", "callback_data": "um_user_profile", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def menu_design_list_keyboard():
    return {"inline_keyboard": [
        [{"text": "Edit /start Menu", "icon_custom_emoji_id": "5395444784611480792", "callback_data": "md_edit_start", "style": "primary"}],
        [{"text": "Edit GET NUMBER", "icon_custom_emoji_id": "5337132498965010628", "callback_data": "md_edit_get_number", "style": "success"},
         {"text": "Edit Search Number", "icon_custom_emoji_id": "5190645917711114179", "callback_data": "md_edit_search_number", "style": "success"}],
        [{"text": "Edit Select Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "md_edit_select_country", "style": "primary"}],
        [{"text": "Edit TRAFFIC", "icon_custom_emoji_id": "5353032893096567467", "callback_data": "md_edit_traffic", "style": "primary"},
         {"text": "Edit Refer", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "md_edit_refer", "style": "primary"}],
        [{"text": "Edit WITHDRAWAL", "icon_custom_emoji_id": "5352585194295564660", "callback_data": "md_edit_withdrawal", "style": "danger"},
         {"text": "Edit SUPPORT", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "md_edit_support", "style": "danger"}],
        [{"text": "Reset Defaults", "icon_custom_emoji_id": "5192812028632274956", "callback_data": "md_reset_defaults", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def menu_edit_options_keyboard(menu_key):
    return {"inline_keyboard": [
        [{"text": "Edit Body (Text)", "icon_custom_emoji_id": "5395444784611480792", "callback_data": f"md_text_{menu_key}", "style": "primary"}],
        [{"text": "Edit Inline Buttons", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"md_btns_{menu_key}", "style": "success"}],
        [{"text": "Back to Menus", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "menu_design_list", "style": "danger"}]
    ]}

def menu_buttons_list_keyboard(menu_key):
    kb = []
    btns = bot_settings["custom_messages"].get(menu_key, {}).get("buttons", [])
    for idx, btn in enumerate(btns):
        kb.append([{"text": f"Del: {btn['text']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"md_delbtn_{menu_key}_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Inline Button", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"md_addbtn_{menu_key}", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_edit_{menu_key}", "style": "primary"}])
    return {"inline_keyboard": kb}

def emoji_settings_keyboard():
    return {"inline_keyboard": [
        [{"text": "Upload Flags (TXT)", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "up_flags_txt", "style": "primary"},
         {"text": "Download Flags", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_flags_txt", "style": "success"}],
        [{"text": "Upload Services (TXT)", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "up_apps_txt", "style": "primary"},
         {"text": "Download Services", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_apps_txt", "style": "success"}],
        [{"text": "Delete All Flags", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "del_all_flags", "style": "danger"},
         {"text": "Add Single Emoji", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_single_emoji", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
    ]}

def fj_settings_keyboard():
    status_text = 'ON' if bot_settings['fj_on'] else 'OFF'
    status_icon = "5352694861990501856" if bot_settings['fj_on'] else "5318840353510408444"
    kb = [[{"text": f"STATUS: {status_text}", "icon_custom_emoji_id": status_icon, "callback_data": "toggle_fj", "style": "primary"}]]
    for idx, ch in enumerate(bot_settings["fj_channels"]):
        display_ch = _fj_chat_id(ch)
        kb.append([{"text": f"Delete: {display_ch}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_fj_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Channel", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_fj", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}])
    return {"inline_keyboard": kb}

def admin_settings_keyboard():
    kb = []
    for idx, adm in enumerate(bot_settings["admins"]):
        text_btn = f"Owner: {adm}" if adm == OWNER_ID else f"Delete: {adm}"
        icon_id = "5353032893096567467" if adm == OWNER_ID else "5420130255174145507"
        cb_data = "ignore" if adm == OWNER_ID else f"del_adm_{idx}"
        kb.append([{"text": text_btn, "icon_custom_emoji_id": icon_id, "callback_data": cb_data, "style": "danger" if adm != OWNER_ID else "primary"}])
    kb.append([{"text": "Add Admin", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_adm", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}])
    return {"inline_keyboard": kb}

def otp_groups_list_keyboard():
    kb = [
        [{"text": "Set OTP Group Link", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "edit_otp_link", "style": "primary"},
         {"text": "Set Channel Link", "icon_custom_emoji_id": "5789428375261023681", "callback_data": "set_otp_channel_link", "style": "success"}],
        [{"text": "Add New Button", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "otp_add_button", "style": "success"},
         {"text": "Button Management", "icon_custom_emoji_id": "5336879280578138635", "callback_data": "otp_button_management", "style": "primary"}]
    ]
    for idx, fg in enumerate(bot_settings["fw_groups"]):
        kb.append([{"text": f"Group: {fg['chat_id']}", "icon_custom_emoji_id": "5193063022226086560", "callback_data": f"manage_fw_{idx}", "style": "primary"}])
    kb.append([{"text": "Add Forward Group", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_fw", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}])
    return {"inline_keyboard": kb}

def otp_button_management_keyboard():
    kb = []
    for idx, btn in enumerate(bot_settings.get("otp_extra_buttons", [])):
        row = {"text": btn.get("text", f"Button {idx+1}"), "callback_data": f"otp_manage_btn_{idx}", "style": "primary"}
        if btn.get("icon_custom_emoji_id"):
            row["icon_custom_emoji_id"] = str(btn["icon_custom_emoji_id"])
        kb.append([row])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "danger"}])
    return {"inline_keyboard": kb}

def otp_single_button_keyboard(idx):
    return {"inline_keyboard": [
        [{"text": "Edit Button", "icon_custom_emoji_id": "5352552689983067014", "callback_data": f"otp_edit_btn_{idx}", "style": "primary"}],
        [{"text": "Customize Emoji", "icon_custom_emoji_id": "5352552689983067014", "callback_data": f"otp_customize_emoji_{idx}", "style": "success"}],
        [{"text": "Delete Button", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"otp_delete_btn_{idx}", "style": "danger"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "otp_button_management", "style": "primary"}]
    ]}

def stex_control_keyboard():
    return {"inline_keyboard": [
        [{"text": "Add StexSMS Key", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_stex_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_stex_keys", "style": "danger"}],
        [{"text": "Manage StexSMS Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_stex_srv", "style": "success"}],
        [{"text": "Search Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "stex_search_country", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def voltx_control_keyboard():
    return {"inline_keyboard": [
        [{"text": "Add Voltx Key", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_voltx_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_voltx_keys", "style": "danger"}],
        [{"text": "Manage Voltx Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_voltx_srv", "style": "success"}],
        [{"text": "Search Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "voltx_search_country", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def specific_fw_group_keyboard(idx):
    group = bot_settings["fw_groups"][idx]
    kb = []
    for b_idx, btn in enumerate(group.get("buttons", [])):
        kb.append([{"text": f"Del: {btn['text']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_fwbtn_{idx}_{b_idx}", "style": "danger"}])
    
    kb.append([{"text": "Add Inline Button", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"add_fwbtn_{idx}", "style": "success"}])
    kb.append([{"text": "Delete Entire Group", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"del_fw_{idx}", "style": "danger"}])
    kb.append([{"text": "Back to Groups", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "primary"}])
    return {"inline_keyboard": kb}

def dxa_control_keyboard():
    w_status = "ON" if bot_settings["withdraw_on"] else "OFF"
    sup_status = "ON" if bot_settings.get("support_link") else "OFF"
    grp_status = "ON" if bot_settings.get("w_group") else "OFF"
    return {"inline_keyboard": [
        [{"text": f"WITHDRAW: {w_status}", "icon_custom_emoji_id": "5348469219761626211", "callback_data": "dxa_toggle_w", "style": "primary"}],
        [{"text": f"MIN WITHDRAW: {bot_settings['min_withdraw']}", "icon_custom_emoji_id": "5352877703043258544", "callback_data": "dxa_min_w", "style": "success"},
         {"text": f"OTP REWARD: {bot_settings['otp_reward']}", "icon_custom_emoji_id": "5190576863226933563", "callback_data": "dxa_otp_r", "style": "primary"}],
        [{"text": f"REFER REWARD: {bot_settings['refer_reward']}", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "dxa_ref_r", "style": "success"},
         {"text": f"COOLDOWN: {bot_settings['cooldown']}s", "icon_custom_emoji_id": "5337172996211648018", "callback_data": "dxa_cool", "style": "primary"}],
        [{"text": f"NUM/REQ: {bot_settings['num_req']}", "icon_custom_emoji_id": "5337132498965010628", "callback_data": "dxa_num_req", "style": "success"},
         {"text": f"NUM/SHARE: {bot_settings['num_share']}", "icon_custom_emoji_id": "5352862640592949843", "callback_data": "dxa_num_share", "style": "primary"}],
        [{"text": f"SUPPORT LINK: {sup_status}", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "dxa_sup_link", "style": "success"},
         {"text": "W. METHODS", "icon_custom_emoji_id": "5190899075968441286", "callback_data": "manage_w_methods", "style": "primary"}],
        [{"text": f"W. GROUP: {grp_status}", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "dxa_w_group", "style": "success"},
         {"text": "BACK", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
    ]}

def w_methods_keyboard():
    kb = []
    for idx, m in enumerate(bot_settings["w_methods"]):
        kb.append([{"text": f"Delete: {m}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_wm_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Method", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_wm", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "dxa_control", "style": "primary"}])
    return {"inline_keyboard": kb}

def typed_panels_list_keyboard(p_type):
    kb = []
    for idx, p in enumerate(bot_settings["panels"]):
        if p.get("type", "API Panel") != p_type: continue
        action_text = f"Turn OFF {p['name']}" if p['status'] == 'ON' else f"Turn ON {p['name']}"
        action_icon = "5318840353510408444" if p['status'] == 'ON' else "5192812028632274956"
        icon_id = "5420155432272438703" 
        kb.append([
            {"text": action_text, "icon_custom_emoji_id": action_icon, "callback_data": f"tog_pnl_{idx}", "style": "danger" if p['status'] == 'ON' else "success"},
            {"text": f"{p['name']}", "icon_custom_emoji_id": icon_id, "callback_data": f"conf_pnl_{idx}", "style": "primary"}
        ])
    add_cb = "add_api_panel" if p_type == "API Panel" else "add_cpt_panel"
    kb.append([{"text": "Add New Provider", "icon_custom_emoji_id": "5420323438508155202", "callback_data": add_cb, "style": "success"}])
    kb.append([{"text": "Delete Provider", "icon_custom_emoji_id": "5336944168944047463", "callback_data": f"list_del_{'api' if p_type=='API Panel' else 'cpt'}", "style": "danger"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_panels", "style": "primary"}])
    return {"inline_keyboard": kb}

def panel_config_keyboard(idx):
    p = bot_settings["panels"][idx]
    
    kb = []
    action_text = "Turn OFF" if p['status'] == 'ON' else "Turn ON"
    action_icon = "5318840353510408444" if p['status'] == 'ON' else "5192812028632274956"
    kb.append([{"text": action_text, "icon_custom_emoji_id": action_icon, "callback_data": f"tog_pnl_{idx}", "style": "danger" if p['status'] == 'ON' else "success"}])
    
    if p["type"] != "Auto Captcha Panel":
        rec_count_text = "All (Unlimited)" if p.get('records', 0) == 0 else str(p.get('records'))
        kb.append([{"text": "Set API URL", "icon_custom_emoji_id": "5420517437885943844", "callback_data": f"set_p_api_{idx}", "style": "primary"}])
        kb.append([{"text": "Set Token", "icon_custom_emoji_id": "5353022963132174959", "callback_data": f"set_p_tok_{idx}", "style": "primary"}])
        kb.append([{"text": "🌐 Full API (URL+Token)", "icon_custom_emoji_id": "5420517437885943844", "callback_data": f"set_p_fapi_{idx}", "style": "primary"}])
        kb.append([{"text": f"Set Records Count: {rec_count_text}", "icon_custom_emoji_id": "5192739271886282680", "callback_data": f"set_p_rec_{idx}", "style": "primary"}])
        
    kb.append([{"text": "Test Connection", "icon_custom_emoji_id": "5352694861990501856", "callback_data": f"test_p_conn_{idx}", "style": "success"}])
        
    back_data = "manage_api_panels" if p.get("type", "API Panel") == "API Panel" else "manage_cpt_panels"
    kb.append([{"text": "Back to Providers", "icon_custom_emoji_id": "5267490665117275176", "callback_data": back_data, "style": "danger"}])
    return {"inline_keyboard": kb}



# Live Access display window: Voltex Console activity from the last 0–30 minutes.
LIVE_ACCESS_DISPLAY_WINDOW = 30 * 60

def get_voltx_active_catalog(max_age=LIVE_ACCESS_DISPLAY_WINDOW):
    """Return only Voltx services/countries/ranges that have recent live traffic."""
    now = time.time()
    catalog = {}
    for hit in recent_traffic:
        if "real_range" not in hit:
            continue
        try:
            age = now - float(hit.get("time", 0))
        except Exception:
            continue
        if age < 0 or age > max_age:
            continue
        service = str(hit.get("service", "")).strip()
        iso = str(hit.get("iso", "")).strip().upper()
        rng = str(hit.get("real_range", "")).replace("X", "").strip()
        if not service or not iso or not rng:
            continue
        country = get_flag_info_html(iso, return_full_name=True).title()
        catalog.setdefault(service, {}).setdefault(country, set()).add(rng)
    return catalog

def voltx_allocate_number(range_hint=""):
    """Allocate a VOLTX number and retain the active service/range metadata."""
    keys = [str(k).strip() for k in bot_settings.get("voltx_keys", []) if str(k).strip()]
    if not keys:
        return None, "VOLTX API key is missing.", {}

    hint = str(range_hint or "").strip().replace("X", "").replace("x", "")
    range_items = []  # (service, range, configured_country)

    # Prefer the live VOLTX catalog because it is the source that tells us
    # which service owns the range.
    for key in keys:
        try:
            r = requests.get(
                f"{VOLTX_BASE_URL}/liveaccess",
                headers={"mauthapi": key, "Accept": "application/json", "User-Agent": "Mozilla/5.0"},
                timeout=8
            )
            j = r.json()
            if j.get("meta", {}).get("code") != 200:
                continue
            services = (j.get("data") or {}).get("services") or []
            for svc in services:
                service_name = str(svc.get("sid", "")).strip()
                for rr in (svc.get("ranges") or []):
                    clean = str(rr).strip().replace("X", "").replace("x", "")
                    if clean and (not hint or clean.startswith(hint) or hint.startswith(clean)):
                        item = (service_name, clean, "")
                        if item not in range_items:
                            range_items.append(item)
            if range_items:
                break
        except Exception:
            continue

    # If a specific range was supplied but liveaccess did not return it, keep
    # the range usable and recover service/country from the bot's saved VOLTX
    # service map when available.
    if hint and not range_items:
        for service_name, countries in bot_settings.get("voltx_services", {}).items():
            for country_name, ranges in (countries or {}).items():
                for rr in ranges or []:
                    clean = str(rr).strip().replace("X", "").replace("x", "")
                    if clean and (clean.startswith(hint) or hint.startswith(clean)):
                        range_items.append((str(service_name), clean, str(country_name)))

    # Final fallback: use the supplied range itself. This keeps allocation
    # working even when liveaccess is temporarily empty.
    if not range_items and hint:
        range_items = [("", hint, "")]

    if not range_items:
        return None, "No active VOLTX range was returned by liveaccess.", {}

    last_error = "VOLTX allocation failed."
    for service_name, rng, configured_country in range_items:
        for key in keys:
            try:
                res = requests.post(
                    f"{VOLTX_BASE_URL}/getnum",
                    json={"rid": rng},
                    headers={"mauthapi": key, "Accept": "application/json", "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
                    timeout=10
                )
                try:
                    data = res.json()
                except Exception:
                    data = {}
                if data.get("meta", {}).get("code") != 200:
                    last_error = str(data.get("message") or data.get("meta", {}).get("status") or f"HTTP {res.status_code}")
                    continue
                d = data.get("data") or {}
                for field in ("full_number", "no_plus_number", "national_number"):
                    value = str(d.get(field, "") or "").strip()
                    digits = re.sub(r"\D", "", value)
                    if 7 <= len(digits) <= 18:
                        country_name = str(d.get("country", "") or configured_country).strip()
                        if not country_name:
                            try:
                                _, iso = get_flag_and_code(digits)
                                country_name = COUNTRY_NAME_BY_ISO.get(str(iso).upper(), "")
                            except Exception:
                                country_name = ""
                        return digits, "", {
                            "service": service_name,
                            "country": country_name,
                            "range": rng,
                            "operator": str(d.get("operator", "") or "").strip(),
                        }
                last_error = "VOLTX returned success but no number field."
            except Exception as e:
                last_error = str(e)
    return None, last_error, {}

def voltx_has_active_service(service, country=None, target_range=None, max_age=120):
    """Strictly allow only a service/country/range with live Voltx traffic."""
    catalog = get_voltx_active_catalog(max_age)
    svc = next((k for k in catalog if k.upper() == str(service).upper()), None)
    if not svc:
        return False
    if country is None:
        return True
    cnt = next((k for k in catalog[svc] if k.upper() == str(country).upper()), None)
    if not cnt:
        return False
    if target_range is None:
        return True
    return str(target_range).replace("X", "").startswith(tuple(catalog[svc][cnt]))

def build_traffic_ui():
    global recent_traffic
    current_time = time.time()
    recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= LIVE_ACCESS_DISPLAY_WINDOW]
    
    stats = {}
    for t in recent_traffic:
        srv = t.get("service", "Unknown")
        iso = t.get("iso", "XX")
        flag = t.get("flag", "🌍")
        
        if srv not in stats:
            stats[srv] = {}
        if iso not in stats[srv]:
            stats[srv][iso] = {"count": 0, "flag": flag}
        stats[srv][iso]["count"] += 1
        
    txt = "╔═════════════════╗\n║  📈 <b>NETWORK TRAFFIC</b>\n╚═════════════════╝\n\n"
    
    kb = []
    if not stats:
        txt += "<i>No recent traffic found in the last hour...</i>\n"
    else:
        srv_totals = []
        for srv, countries in stats.items():
            total = sum(c["count"] for c in countries.values())
            srv_totals.append((srv, total, countries))
        
        srv_totals.sort(key=lambda x: x[1], reverse=True)
        
        for srv, total, countries in srv_totals:
            app_full_name, prem_app_html = get_service_info_html(srv)
            txt += f"[ {prem_app_html} <b>{app_full_name}</b> ]\n│\n"
            
            c_list = sorted(countries.items(), key=lambda x: x[1]["count"], reverse=True)
            c_list = c_list[:7] 
            
            for i, (iso, c_data) in enumerate(c_list):
                prem_flag_html = get_flag_info_html(iso)
                count = c_data["count"]
                
                c_name = iso
                for code, fdata in bot_settings.get("premium_flags", {}).items():
                    if fdata.get("iso") == iso:
                        c_name = fdata.get("name", iso)
                        break
                        
                unicode_flag = ISO_TO_FLAG.get(str(iso).upper(), "🌍")
                txt += f"├ {unicode_flag} {prem_flag_html} <b>{c_name} ({iso})</b>\n"
                txt += f"│ ╰ Success: {count}\n"
                if i < len(c_list) - 1:
                    txt += "│\n"
            txt += "\n"
        
        # 🌟 FIX: [:3] লিমিট তুলে দেওয়া হলো, এখন যতো সার্ভিস থাকবে সবগুলোর বাটন নিচে শো করবে!
        for srv, _, _ in srv_totals: 
            safe_srv = srv[:20] 
            # বাটনে সুন্দরভাবে ফুল নাম দেখানোর জন্য
            app_full_name, _ = get_service_info_html(safe_srv, safe_srv)
            kb.append([{"text": f"Explore {app_full_name} Range", "icon_custom_emoji_id": "5190645917711114179", "callback_data": f"exp_rng_{safe_srv}", "style": "success"}])
            
    txt = render_body_text(txt)
    kb.append([{"text": "Refresh", "icon_custom_emoji_id": "5465368548702446780", "callback_data": "refresh_traffic", "style": "primary"}])
    kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
    
    return txt, {"inline_keyboard": kb}

# ==========================================
# CUSTOM OTP TEST CONFIGURATION
# NOTE: This module sends synthetic/test messages only.
# The existing OTP formatting function is intentionally untouched.
# ==========================================
def custom_otp_normalize_services():
    """Normalize service names and keep per-service synthetic code-digit settings."""
    raw = bot_settings.get("custom_otp_services", []) or []
    digits_map = bot_settings.setdefault("custom_otp_service_digits", {})
    clean = []
    seen = set()
    for item in raw:
        name = str(item).strip()
        if not name:
            continue
        # Legacy entries like "Facebook-8" are still accepted, but the UI now
        # manages digits from inside each service button.
        m = re.match(r"^(.+?)\s*[-:]\s*(\d{1,2})$", name)
        if m:
            name = m.group(1).strip()
            digits_map[name] = max(1, min(12, int(m.group(2))))
        key = name.lower()
        if key not in seen:
            clean.append(name)
            seen.add(key)
    bot_settings["custom_otp_services"] = clean
    # Migrate case-variant digit keys to the current service spelling.
    for srv in clean:
        for k in list(digits_map.keys()):
            if str(k).lower() == srv.lower() and k != srv:
                digits_map[srv] = digits_map.pop(k)
                break
        if srv not in digits_map:
            digits_map[srv] = 6
        try:
            digits_map[srv] = max(1, min(12, int(digits_map[srv])))
        except Exception:
            digits_map[srv] = 6
    return clean, digits_map


def _custom_otp_service_digits(service):
    """Return the saved synthetic code length for a service."""
    services, digits_map = custom_otp_normalize_services()
    key = str(service).strip().lower()
    for srv in services:
        if srv.lower() == key:
            try:
                return max(1, min(12, int(digits_map.get(srv, 6))))
            except Exception:
                return 6
    return 6


def custom_otp_keyboard():
    # Always derive the button text, callback and color directly from the
    # persisted running state so START can never keep the STOP color (or vice versa).
    running = bool(bot_settings.get("custom_otp_running", False))
    services, _ = custom_otp_normalize_services()
    configs = bot_settings.get("custom_otp_configs", []) or []

    # State button must visibly reflect the real saved running state.
    status_text = "⛔ STOP" if running else "▶️ START"
    status_callback = "cotp_stop" if running else "cotp_start"
    status_style = "danger" if running else "success"

    kb = [
        [{"text": "Add Service", "callback_data": "cotp_add_service", "style": "success"},
         {"text": "Add Number", "callback_data": "cotp_add_number", "style": "primary"}],
        [{"text": f"Services ({len(services)})", "callback_data": "cotp_services", "style": "primary"},
         {"text": f"Numbers ({len(configs)})", "callback_data": "cotp_numbers", "style": "primary"}],
        [{"text": status_text, "callback_data": status_callback, "style": status_style}],
        [{"text": "Back", "callback_data": "system_settings", "style": "primary"}],
    ]
    return {"inline_keyboard": kb}


def custom_otp_text():
    services, digits_map = custom_otp_normalize_services()
    configs = bot_settings.get("custom_otp_configs", []) or []
    running = bool(bot_settings.get("custom_otp_running", False))
    lines = ["🧪 <b>CUSTOM OTP TEST</b>", "", "Service → Number → Interval"]
    lines.append(f"Services: {len(services)}")
    lines.append(f"Numbers: {len(configs)}")
    lines.append(f"Status: {'RUNNING' if running else 'STOPPED'}")
    lines.append("")
    lines.append("Add Service:")
    lines.append("<code>Facebook, WhatsApp, Telegram, Imo</code>")
    lines.append("")
    lines.append("Add Number format:")
    lines.append("<code>263772266797-Facebook-4s</code>")
    lines.append("<code>417262252552-Telegram-8s</code>")
    lines.append("<code>528228282672-WhatsApp-10s</code>")
    lines.append("<b>+ চিহ্ন লাগবে না।</b>")
    lines.append("একসাথে একাধিক লাইন দিতে পারবেন।")
    lines.append("")
    lines.append("Code digits are set inside each Service button.")
    lines.append("Service code length: " + (", ".join(f"{x}={int(digits_map.get(x, 6))} digit" for x in services) if services else "Not set"))
    lines.append("This test module uses the existing OTP message-body formatter unchanged.")
    return render_body_text("\n".join(lines))


def custom_otp_services_view(chat_id, msg_id):
    services, digits_map = custom_otp_normalize_services()
    txt = "🧩 <b>CUSTOM SERVICES</b>\n\n"
    if services:
        txt += "Select a service to set its code digits:\n\n"
        txt += "\n".join(f"• {x} — {int(digits_map.get(x, 6))} digit" for x in services)
    else:
        txt += "No services added."
    kb = []
    for idx, srv in enumerate(services):
        kb.append([{"text": str(srv), "callback_data": f"cotp_service_{idx}", "style": "primary"}])
    kb.append([{"text": "Add Service", "callback_data": "cotp_add_service", "style": "success"}])
    kb.append([{"text": "Back", "callback_data": "custom_otp", "style": "primary"}])
    edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})


def custom_otp_service_view(chat_id, msg_id, idx):
    services, digits_map = custom_otp_normalize_services()
    if not (0 <= idx < len(services)):
        custom_otp_services_view(chat_id, msg_id)
        return
    srv = services[idx]
    digits = _custom_otp_service_digits(srv)
    txt = (
        f"🧩 <b>{srv}</b>\n\n"
        f"Current Code Digit: <b>{digits}</b>\n\n"
        "Set the synthetic/test code length for this service.\n"
        "Example: <code>6</code> for WhatsApp, <code>5</code> for Telegram, <code>4</code> for Imo."
    )
    kb = [
        [{"text": "Set Code Digit", "callback_data": f"cotp_set_digit_{idx}", "style": "success"}],
        [{"text": "Delete Service", "callback_data": f"cotp_del_service_{idx}", "style": "danger"}],
        [{"text": "⬅️ Back to Services", "callback_data": "cotp_services", "style": "primary"}],
        [{"text": "⬅️ Back to CUSTOM OTP", "callback_data": "custom_otp", "style": "primary"}],
    ]
    edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})


def custom_otp_numbers_view(chat_id, msg_id):
    configs = bot_settings.get("custom_otp_configs", []) or []
    txt = "📱 <b>CUSTOM NUMBERS</b>\n\n"
    if configs:
        rows = []
        for cfg in configs:
            num = str(cfg.get("number", ""))
            srv = str(cfg.get("service", ""))
            sec = int(cfg.get("seconds", 1))
            try:
                flag, country = get_flag_and_code(num)
                country_line = f"{flag} {country}"
            except Exception:
                country_line = "🌐 Unknown"
            rows.append(f"{country_line}\n<code>{num}-{srv}-{sec}s</code>\nCode: <b>{_custom_otp_service_digits(srv)} digit</b>")
        txt += "\n\n".join(rows)
    else:
        txt += "No numbers added."
    kb = []
    for i, cfg in enumerate(configs):
        num = str(cfg.get("number", ""))
        srv = str(cfg.get("service", ""))
        kb.append([{"text": f"Delete {num} • {srv}", "callback_data": f"cotp_del_number_{i}", "style": "danger"}])
    kb.append([{"text": "Add Number", "callback_data": "cotp_add_number", "style": "primary"}])
    kb.append([{"text": "Back", "callback_data": "custom_otp", "style": "primary"}])
    edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

def _custom_otp_send_synthetic(cfg):
    """Send a synthetic test code using the existing formatter; never a received OTP."""
    number = str(cfg.get("number", "")).strip()
    service = str(cfg.get("service", "")).strip()
    digits = _custom_otp_service_digits(service)
    cfg["digits"] = digits
    code = "".join(str(random.randint(0, 9)) for _ in range(digits))

    # Synthetic display number: keep the configured prefix/country portion,
    # but randomize the final 4 digits on every test message.
    raw_digits = re.sub(r"\D", "", number)
    if len(raw_digits) >= 4:
        display_number = raw_digits[:-4] + "".join(str(random.randint(0, 9)) for _ in range(4))
    else:
        display_number = number

    body = format_otp_forward_body(display_number, service, "")
    for fw in bot_settings.get("fw_groups", []):
        try:
            send_message(fw.get("chat_id"), body, reply_markup=build_otp_forward_keyboard(code, fw))
        except Exception as e:
            print(f"CUSTOM OTP TEST send error: {e}")

# Synthetic-test sender state.  Each config is allowed only one in-flight send,
# so a slow Telegram/API request cannot pause the scheduler for all other configs.
_custom_otp_inflight = set()
_custom_otp_inflight_lock = threading.Lock()

def _custom_otp_send_async(idx, cfg):
    try:
        _custom_otp_send_synthetic(cfg)
    except Exception as e:
        print(f"CUSTOM OTP TEST async send error: {e}")
    finally:
        with _custom_otp_inflight_lock:
            _custom_otp_inflight.discard(idx)

def _custom_otp_worker():
    next_due = {}
    while not custom_otp_stop_event.is_set():
        if not bot_settings.get("custom_otp_running", False):
            custom_otp_stop_event.wait(0.5)
            continue

        now = time.time()
        configs = bot_settings.get("custom_otp_configs", []) or []

        # Remove stale scheduler entries if numbers were deleted/reordered.
        for idx in list(next_due):
            if idx >= len(configs):
                next_due.pop(idx, None)

        for idx, cfg in enumerate(configs):
            try:
                interval = max(1, int(cfg.get("seconds", 1)))
            except Exception:
                continue

            due = next_due.get(idx, 0)
            if now >= due:
                with _custom_otp_inflight_lock:
                    already_running = idx in _custom_otp_inflight
                    if not already_running:
                        _custom_otp_inflight.add(idx)

                if not already_running:
                    # IMPORTANT: never wait for Telegram here. The scheduler keeps running
                    # even if one API request is slow or temporarily unavailable.
                    threading.Thread(
                        target=_custom_otp_send_async,
                        args=(idx, cfg.copy()),
                        daemon=True
                    ).start()
                    cfg["sent"] = int(cfg.get("sent", 0)) + 1

                # Schedule from the current scheduler time, not from the end of the API call.
                next_due[idx] = now + interval

        # Do NOT call save_db() for every synthetic message. That can create many
        # background Firestore writes and slow the bot when intervals are short.
        custom_otp_stop_event.wait(0.2)

def custom_otp_start():
    global custom_otp_worker_thread
    configs = bot_settings.get("custom_otp_configs", [])
    if not configs:
        return False, "❌ Add at least one number configuration first."
    for cfg in configs:
        cfg.pop("quantity", None)
        cfg["sent"] = 0
    bot_settings["custom_otp_running"] = True
    custom_otp_stop_event.clear()
    if custom_otp_worker_thread is None or not custom_otp_worker_thread.is_alive():
        custom_otp_worker_thread = threading.Thread(target=_custom_otp_worker, daemon=True)
        custom_otp_worker_thread.start()
    save_db()
    return True, "▶️ CUSTOM OTP TEST STARTED"

def custom_otp_stop():
    bot_settings["custom_otp_running"] = False
    custom_otp_stop_event.set()
    save_db()
    return "⏹ CUSTOM OTP TEST STOPPED"

# ==========================================
# Message Handler
# ==========================================
def handle_message(msg):
    global total_uploaded_stats
    chat_id = msg["chat"]["id"]
    chat_type = msg["chat"].get("type", "private")
    
    if chat_type != "private":
        return
        
    text = msg.get("text", "")
    register_user_local(chat_id) # 🌟 Save User locally for Free Broadcasts!
    update_user_identity(chat_id, msg.get("from", {})) # Keep admin user list info accurate

    if is_user_banned(chat_id):
        send_message(chat_id, render_body_text("🚫 <b>You are banned from using this bot!</b>\nIf you think this is a mistake, please contact support."))
        return
    
    # --- REFERRAL FIX: Save inviter BEFORE Force Join ---
    if text.startswith("/start"):
        parts = text.split()
        if len(parts) > 1 and parts[1].isdigit():
            inviter = int(parts[1])
            if inviter != chat_id:
                if db:
                    doc = db.collection('users').document(str(chat_id)).get()
                    if not doc.exists:
                        get_user(chat_id)
                        db.collection('users').document(str(chat_id)).update({"referred_by": inviter, "ref_paid": False})
                        
    if not check_force_join(chat_id):
        send_force_join_msg(chat_id)
        return
        
    MAIN_MENU_CMDS = ["GET NUMBER", "Search Number", "TRAFFIC", "Refer", "WITHDRAWAL", "SUPPORT", "Admin Panel", "2FA ONLINE"]
    
    is_main_cmd = False
    if text in MAIN_MENU_CMDS or text.startswith("/start"):
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        is_main_cmd = True
    
    if chat_id in user_states and not is_main_cmd:
        state = user_states[chat_id]
        
        # PREFIX SETTING FLOW
        if state == "wait_for_prefix" and text:
            prefix = re.sub(r"\D", "", text.strip())
            if not (5 <= len(prefix) <= 10):
                send_message(
                    chat_id,
                    render_body_text(
                        "❌ <b>Invalid Prefix</b>\n\n"
                        "Prefix must contain <b>5 to 10 digits</b>.\n"
                        "Example: <code>26138234</code>"
                    ),
                    reply_markup=get_cancel_kb()
                )
                return

            user_prefixes[chat_id] = prefix
            user_states.pop(chat_id, None)

            # Restore the same Number page and only change the Prefix button.
            saved = temp_data.pop(chat_id, {})
            # Prefer the persistent Number-page snapshot; it survives the no-stock
            # transition and is therefore also available for the Back button.
            saved = number_page_snapshots.get(chat_id, saved)
            page_msg_id = saved.get("msg_id")
            saved_markup = saved.get("reply_markup")
            saved_text = saved.get("text", "NEW NUMBER\n")
            if page_msg_id and saved_markup:
                try:
                    markup = {"inline_keyboard": [list(row) for row in saved_markup.get("inline_keyboard", [])]}
                    for row in markup["inline_keyboard"]:
                        for btn in row:
                            if btn.get("callback_data") == "set_prefix":
                                btn["text"] = f"🔢 Prefix ON • {prefix}"
                    edit_message(chat_id, page_msg_id, saved_text, reply_markup=markup)
                    return
                except Exception:
                    pass

            # Fallback only if the original Number page cannot be restored.
            send_message(chat_id, render_body_text(f"🔢 <b>Prefix ON • {prefix}</b>"))
            return

        # CUSTOM OTP TEST CONFIGURATION FLOWS
        if state == "wait_for_cotp_service" and text:
            raw_services = [x.strip() for x in text.split(",") if x.strip()]
            if not raw_services:
                send_message(chat_id, render_body_text("❌ Send at least one service name."), reply_markup=get_cancel_kb())
                return
            services = bot_settings.setdefault("custom_otp_services", [])
            digits_map = bot_settings.setdefault("custom_otp_service_digits", {})
            existing = {str(x).lower() for x in services}
            for item in raw_services:
                m = re.match(r"^(.+?)\s*[-:]\s*(\d{1,2})$", item)
                srv = m.group(1).strip() if m else item.strip()
                digits = int(m.group(2)) if m else int(digits_map.get(srv, 6) or 6)
                digits = max(1, min(12, digits))
                if srv.lower() not in existing:
                    services.append(srv)
                    existing.add(srv.lower())
                old_key = next((k for k in list(digits_map.keys()) if str(k).lower() == srv.lower()), None)
                if old_key and old_key != srv:
                    digits_map[srv] = digits_map.pop(old_key)
                digits_map[srv] = digits
            custom_otp_normalize_services()
            save_db()
            del user_states[chat_id]
            del temp_data[chat_id]
            send_message(chat_id, custom_otp_text(), reply_markup=custom_otp_keyboard())
            return

        elif state == "wait_for_cotp_digit" and text:
            idx = int(temp_data.get(chat_id, {}).get("service_idx", -1))
            services, digits_map = custom_otp_normalize_services()
            try:
                digits = int(text.strip())
            except Exception:
                digits = 0
            if not (1 <= digits <= 12):
                send_message(chat_id, render_body_text("❌ Code digit must be a whole number from 1 to 12. Example: <code>6</code>"), reply_markup=get_cancel_kb())
                return
            if 0 <= idx < len(services):
                digits_map[services[idx]] = digits
                # Keep any already-added number configs synchronized with the service setting.
                for cfg in bot_settings.get("custom_otp_configs", []) or []:
                    if str(cfg.get("service", "")).lower() == services[idx].lower():
                        cfg["digits"] = digits
                save_db()
                del user_states[chat_id]
                temp = temp_data.pop(chat_id, {})
                service_msg_id = temp.get("msg_id")
                if service_msg_id:
                    edit_message(
                        chat_id,
                        service_msg_id,
                        render_body_text(
                            f"✅ <b>{services[idx]}</b> code digit set to <b>{digits}</b>.\n\n"
                            f"🧩 <b>{services[idx]}</b>\n"
                            f"Current Code Digit: <b>{digits}</b>\n\n"
                            "You can change it again or go back."
                        ),
                        reply_markup={"inline_keyboard": [
                            [{"text": "Set Code Digit", "callback_data": f"cotp_set_digit_{idx}", "style": "success"}],
                            [{"text": "Delete Service", "callback_data": f"cotp_del_service_{idx}", "style": "danger"}],
                            [{"text": "⬅️ Back to Services", "callback_data": "cotp_services", "style": "primary"}],
                            [{"text": "⬅️ Back to CUSTOM OTP", "callback_data": "custom_otp", "style": "primary"}],
                        ]}
                    )
                else:
                    custom_otp_service_view(chat_id, temp.get("msg_id", 0), idx)
                return
            send_message(chat_id, render_body_text("❌ Service not found."), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_cotp_number" and text:
            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            parsed = []
            errors = []
            services = bot_settings.get("custom_otp_services", []) or []
            service_lookup = {str(x).strip().lower(): str(x).strip() for x in services}

            for line in lines:
                # Exact user format: NUMBER-SERVICE-SECONDSs
                # Example: 417262252552-Imo-8s
                clean_line = line.strip().replace("–", "-").replace("—", "-")

                # Split from the right so service names containing '-' still work.
                parts = clean_line.rsplit("-", 2)
                if len(parts) != 3:
                    errors.append(line)
                    continue

                number, service, interval_text = [x.strip() for x in parts]
                number = number.replace(" ", "")
                service = service.strip()

                # Optional + is tolerated, but the UI tells the user not to use it.
                if number.startswith("+"):
                    number = number[1:]

                # Number must contain digits only after removing the optional +.
                if not number.isdigit():
                    errors.append(line)
                    continue

                # Accept exact 4s/8s/10s format. Parentheses are accepted only for
                # compatibility with older entries: (8s).
                interval_match = re.fullmatch(
                    r"\(?\s*(\d+)\s*(?:s|sec|secs|second|seconds)?\s*\)?",
                    interval_text,
                    re.I
                )
                if not interval_match:
                    errors.append(line)
                    continue

                try:
                    seconds = int(interval_match.group(1))
                except Exception:
                    errors.append(line)
                    continue

                if seconds < 1:
                    errors.append(line)
                    continue

                # If services have been created, the entered service must match one
                # of them (case-insensitive), while preserving the configured name.
                if service_lookup:
                    canonical_service = service_lookup.get(service.lower())
                    if not canonical_service:
                        errors.append(line)
                        continue
                    service = canonical_service

                parsed.append({
                    "number": number,
                    "service": service,
                    "seconds": seconds,
                    "digits": _custom_otp_service_digits(service),
                    "sent": 0
                })

            if errors:
                error_lines = "\n".join(f"• <code>{html.escape(x)}</code>" for x in errors[:10])
                more = f"\n...and {len(errors) - 10} more." if len(errors) > 10 else ""
                send_message(
                    chat_id,
                    render_body_text(
                        "❌ <b>Format ভুল।</b>\n\n"
                        "এই exact format-এ দিন:\n"
                        "<code>NUMBER-SERVICE-SECONDSs</code>\n\n"
                        "Copy & paste examples:\n"
                        "<code>263772266797-Facebook-4s</code>\n"
                        "<code>417262252552-Telegram-8s</code>\n"
                        "<code>528228282672-WhatsApp-10s</code>\n"
                        "<code>275234522681-Imo-1s</code>\n\n"
                        "⚠️ <b>Quantity/otp লিখবেন না।</b>\n"
                        "⚠️ <b>+ চিহ্ন না দিলেই হবে।</b>\n"
                        "একাধিক number হলে প্রতিটি আলাদা লাইনে দিন.\n\n"
                        f"<b>যে লাইনগুলো ভুল:</b>\n{error_lines}{more}"
                    ),
                    reply_markup={"inline_keyboard": [
                        [{"text": "⬅️ Back", "callback_data": "cotp_numbers", "style": "primary"}],
                        [{"text": "Cancel", "callback_data": "custom_otp", "style": "danger"}]
                    ]}
                )
                return

            bot_settings.setdefault("custom_otp_configs", []).extend(parsed)
            save_db()
            temp = temp_data.pop(chat_id, {})
            del user_states[chat_id]
            source_msg_id = temp.get("msg_id")
            if source_msg_id:
                custom_otp_numbers_view(chat_id, source_msg_id)
            else:
                send_message(chat_id, custom_otp_text(), reply_markup=custom_otp_keyboard())
            return

        # 🌟 Auto Captcha Panel Setup Flow 
        if state == "wait_for_cpanel_url" and text:
            temp_data[chat_id]["p_data"]["login_url"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_user"
            send_message(chat_id, render_body_text("2️⃣ <b>Username</b>\n➡️ Panel এর Username দিন:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_user" and text:
            temp_data[chat_id]["p_data"]["username"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_pass"
            send_message(chat_id, render_body_text("3️⃣ <b>Password</b>\n➡️ Panel এর Password দিন:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_pass" and text:
            temp_data[chat_id]["p_data"]["password"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_msg_link"
            send_message(chat_id, render_body_text("4️⃣ <b>Message Link</b>\n➡️ যেখান থেকে SMS/OTP ডাটা (JSON) আসবে সেই Link দিন:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_msg_link" and text:
            temp_data[chat_id]["p_data"]["msg_link"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_num_col_name"
            send_message(chat_id, render_body_text("5️⃣ <b>Number Column Name</b>\n➡️ Data তে Number column এর নাম কী? (যেমন: number, phone):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_num_col_name" and text:
            temp_data[chat_id]["p_data"]["num_col_name"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_num_col_idx"
            send_message(chat_id, render_body_text("6️⃣ <b>Number Column Serial</b>\n➡️ Number Column এর Serial Number কত? (যেমন: 3, 5):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_num_col_idx" and text:
            if text.isdigit():
                temp_data[chat_id]["p_data"]["num_col_idx"] = int(text)
                user_states[chat_id] = "wait_for_cpanel_msg_col_name"
                send_message(chat_id, render_body_text("7️⃣ <b>Message Column Name</b>\n➡️ Message/OTP column এর নাম কী? (যেমন: message, sms):"), reply_markup=get_cancel_kb())
            else:
                 send_message(chat_id, render_body_text("❌ Please enter a valid number serial!"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_msg_col_name" and text:
            temp_data[chat_id]["p_data"]["msg_col_name"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_msg_col_idx"
            send_message(chat_id, render_body_text("8️⃣ <b>Message Column Serial</b>\n➡️ Message Column এর Serial Number কত? (যেমন: 5, 7):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_msg_col_idx" and text:
            if text.isdigit():
                temp_data[chat_id]["p_data"]["msg_col_idx"] = int(text)
                temp_data[chat_id]["p_data"]["login_status"] = "⏳ Pending Auto-Login..."
                
                # Save the panel configuration
                bot_settings["panels"].append(temp_data[chat_id]["p_data"])
                save_db()
                
                send_message(chat_id, render_body_text(f"{PEM['ok']} <b>Auto Captcha Panel Added Successfully!</b>\nবট এখন থেকে নিজেই ব্যাকগ্রাউন্ডে ক্যাপচা সলভ করে লগিন করে নিবে।"), reply_markup=main_menu(chat_id))
                
                msg_id = temp_data[chat_id]["msg_id"]
                handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_cpt_panels", "id": "internal"})
                
                del user_states[chat_id]
                del temp_data[chat_id]
            else:
                 send_message(chat_id, render_body_text("❌ Please enter a valid number serial!"), reply_markup=get_cancel_kb())
            return

        # --- User Management Flows ---
        elif state == "wait_for_um_bal_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID! Please send a numeric User ID."), reply_markup=get_cancel_kb())
                return
            target_uid = int(target_uid_str)
            try:
                user_data = get_user(target_uid)
                # A non-existing local user is still valid if it is in the known-user list.
                if db:
                    doc = db.collection('users').document(str(target_uid)).get()
                    if not doc.exists:
                        send_message(chat_id, render_body_text("❌ User not found in database!"), reply_markup=get_cancel_kb())
                        return
                    user_data = doc.to_dict()
                elif str(target_uid) not in all_known_users:
                    send_message(chat_id, render_body_text("❌ User not found!"), reply_markup=get_cancel_kb())
                    return
                # Always show the latest balance when Firebase is available.
                if db:
                    current_bal = float((db.collection('users').document(str(target_uid)).get().to_dict() or {}).get('balance', 0) or 0)
                else:
                    current_bal = float(user_balances_local.get(str(target_uid), user_data.get('balance', 0)) or 0)
                temp_data[chat_id]["target_uid"] = target_uid
                user_states[chat_id] = "wait_for_um_bal_amt"
                send_message(chat_id, render_body_text(f"✅ User found!\n💰 Current Balance: {current_bal:.4f} ৳\n\n📝 Send the amount to ADD (e.g. 50) or REMOVE (e.g. -50):"), reply_markup=get_cancel_kb())
            except Exception as e:
                send_message(chat_id, render_body_text(f"❌ User lookup failed: {e}"), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_um_bal_amt" and text:
            try:
                amt = float(text.strip())
                if not (amt == amt) or abs(amt) == float("inf"):
                    raise ValueError
                target_uid = int(temp_data[chat_id]["target_uid"])
                ok, old_bal, new_bal, err = update_balance(target_uid, amt)
                if not ok:
                    send_message(chat_id, render_body_text(
                        f"❌ <b>Balance update failed!</b>\n\n👤 User ID: <code>{target_uid}</code>\n⚠️ {html.escape(str(err))}"
                    ), reply_markup=get_cancel_kb())
                    return
                sign = "+" if amt >= 0 else ""
                send_message(chat_id, render_body_text(
                    f"{PEM['ok']} <b>Balance updated successfully!</b>\n\n👤 User ID: <code>{target_uid}</code>\n💰 Previous: <b>{old_bal:.4f} ৳</b>\n➕ Adjustment: <b>{sign}{amt:.4f} ৳</b>\n💵 New Balance: <b>{new_bal:.4f} ৳</b>"
                ), reply_markup=main_menu(chat_id))
                notify = send_message(target_uid, render_body_text(f"🔔 Your balance has been adjusted by <b>{sign}{amt:.4f} ৳</b> by an Admin.\n💰 New Balance: <b>{new_bal:.4f} ৳</b>"))
                if not notify.get("ok", False):
                    print(f"[BALANCE] Could not notify user {target_uid}: {notify}")
                del user_states[chat_id]
                del temp_data[chat_id]
            except ValueError:
                send_message(chat_id, render_body_text("❌ Invalid amount! Please send a valid number, e.g. 50 or -50."), reply_markup=get_cancel_kb())
            except Exception as e:
                send_message(chat_id, render_body_text(f"❌ <b>Balance update error:</b> {html.escape(str(e))}"), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_um_ban_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID!"), reply_markup=get_cancel_kb())
                return
            target_uid = int(target_uid_str)
            try:
                exists = str(target_uid) in all_known_users
                current_status = str(target_uid) in local_banned_users
                if db:
                    doc_ref = db.collection('users').document(str(target_uid))
                    doc = doc_ref.get()
                    if doc.exists:
                        exists = True
                        current_status = bool(doc.to_dict().get("banned", False))
                    elif not exists:
                        send_message(chat_id, render_body_text("❌ User not found!"), reply_markup=get_cancel_kb())
                        return
                    doc_ref.set({"user_id": target_uid, "banned": not current_status}, merge=True)
                elif not exists:
                    send_message(chat_id, render_body_text("❌ User not found!"), reply_markup=get_cancel_kb())
                    return

                new_status = not current_status
                if new_status:
                    local_banned_users.add(str(target_uid))
                else:
                    local_banned_users.discard(str(target_uid))
                _save_local_bans()
                user_banned_cache[target_uid] = {'banned': new_status, 'time': time.time()}
                status_text = "BANNED 🚫" if new_status else "UNBANNED ✅"
                send_message(chat_id, render_body_text(f"✅ User <code>{target_uid}</code> has been {status_text}!"), reply_markup=main_menu(chat_id))
                user_states.pop(chat_id, None)
                temp_data.pop(chat_id, None)
            except Exception as e:
                send_message(chat_id, render_body_text(f"❌ Ban/Unban failed: {e}"), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_um_prof_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID!"), reply_markup=get_cancel_kb())
                return
            target_uid = int(target_uid_str)
            try:
                if db:
                    doc = db.collection('users').document(str(target_uid)).get()
                    if not doc.exists:
                        send_message(chat_id, render_body_text("❌ User not found!"), reply_markup=get_cancel_kb())
                        return
                    data = doc.to_dict()
                else:
                    if str(target_uid) not in all_known_users:
                        send_message(chat_id, render_body_text("❌ User not found!"), reply_markup=get_cancel_kb())
                        return
                    data = get_user(target_uid).copy()
                    data["banned"] = str(target_uid) in local_banned_users
                is_verified = True if data.get('total_otps', 0) > 0 else data.get('verified', False)
                prof_text = f"""➖➖➖➖➖➖➖➖
👤 <b>USER PROFILE</b>
➖➖➖➖➖➖➖➖
🆔 ID: <code>{target_uid}</code>
💰 Balance: {data.get('balance', 0.0)} ৳
🤝 Total Refers: {data.get('total_refers', 0)}
🔐 Total OTPs: {data.get('total_otps', 0)}
✅ Verified: {is_verified}
🚫 Banned: {data.get('banned', False)}
➖➖➖➖➖➖➖➖"""
                kb = {"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "user_management", "style": "primary"}]]}
                send_message(chat_id, render_body_text(prof_text), reply_markup=kb)
                user_states.pop(chat_id, None)
                temp_data.pop(chat_id, None)
            except Exception as e:
                send_message(chat_id, render_body_text(f"❌ Profile lookup failed: {e}"), reply_markup=get_cancel_kb())
            return

        # --- Menu Design Flow ---
        elif state == "wait_for_menu_text" and text:
            try:
                menu_key = temp_data[chat_id]["menu_key"]
                formatted_html_text = extract_premium_html(msg)
                
                bot_settings["custom_messages"][menu_key]["text"] = formatted_html_text
                save_db()
                
                delete_message(chat_id, msg["message_id"])
                
                preview_text = render_body_text(formatted_html_text)
                success_text = f"{PEM['ok']} <b>Message Body Updated successfully!</b>\n\n🎨 <b>Editing: {menu_key.upper()}</b>\n\nPreview of current Text:\n{preview_text}"
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(success_text), reply_markup=menu_edit_options_keyboard(menu_key))
            except Exception as e:
                send_message(chat_id, f"❌ Error saving text: {e}")
            finally:
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            return
            
        elif state == "wait_for_menu_btn" and text:
            try:
                menu_key = temp_data[chat_id]["menu_key"]
                if "-" in text:
                    parts = text.split("-", 1)
                    btn_text = parts[0].strip()
                    btn_url = parts[1].strip()
                    
                    emoji_id = None
                    emoji_char = ""
                    for ent in msg.get("entities", []):
                        if ent.get("type") == "custom_emoji":
                            emoji_id = ent.get("custom_emoji_id")
                            offset = ent.get("offset", 0)
                            length = ent.get("length", 0)
                            b_text = text.encode('utf-16-le')
                            emoji_char = b_text[offset*2:(offset+length)*2].decode('utf-16-le')
                            break
                            
                    if emoji_char:
                        btn_text = btn_text.replace(emoji_char, "").strip()
                        
                    btn_data = {"text": btn_text, "url": btn_url, "style": "primary"}
                    if emoji_id:
                        btn_data["icon_custom_emoji_id"] = emoji_id
                        
                    bot_settings["custom_messages"][menu_key]["buttons"].append(btn_data)
                    save_db()
                    delete_message(chat_id, msg["message_id"])
                    edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"{PEM['gear']} <b>Edit Inline Buttons: {menu_key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(menu_key))
                else:
                    send_message(chat_id, render_body_text(f"{PEM['no']} Invalid format. Use <code>Button Text - https://link.com</code>"))
            except Exception as e:
                 pass
            finally:
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            return

        elif state == "wait_for_test_service" and text:
            temp_data[chat_id]["service"] = text.strip()
            user_states[chat_id] = "wait_for_test_number"
            send_message(chat_id, render_body_text("📝 Send the Number (e.g. +8801712345678):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_test_number" and text:
            temp_data[chat_id]["number"] = text.strip()
            user_states[chat_id] = "wait_for_test_otp"
            send_message(chat_id, render_body_text("📝 Send the OTP (e.g. 556677):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_test_otp" and text:
            temp_data[chat_id]["otp"] = text.strip()
            user_states[chat_id] = "wait_for_test_lang"
            send_message(chat_id, render_body_text("📝 Send the Language (e.g. EN, AR):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_test_lang" and text:
            lang = text.strip().upper()
            if not lang.startswith("#"):
                lang = "#" + lang
                
            srv = temp_data[chat_id]["service"]
            num = temp_data[chat_id]["number"]
            otp = temp_data[chat_id]["otp"]
            
            masked = mask_number(num)
            prem_flag_html = get_flag_info_html(num)
            char, iso = get_flag_and_code(num)
            app_full_name, prem_app_html = get_service_info_html(srv)
            
            lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
            msg_text = format_otp_forward_body(num, srv, "", lang)
            
            for fw in bot_settings["fw_groups"]:
                send_message(fw["chat_id"], msg_text, reply_markup=build_otp_forward_keyboard(otp, fw))
                
            send_message(chat_id, render_body_text(f"{PEM['ok']} Test message formatted and sent to all Forward Groups!"), reply_markup=main_menu(chat_id))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_emoji_extract":
            entities = msg.get("entities", [])
            custom_emoji_id = None
            emoji_text = ""
            for ent in entities:
                if ent.get("type") == "custom_emoji":
                    custom_emoji_id = ent.get("custom_emoji_id")
                    offset = ent.get("offset", 0)
                    length = ent.get("length", 0)
                    b_text = msg.get("text", "").encode('utf-16-le')
                    emoji_text = b_text[offset*2:(offset+length)*2].decode('utf-16-le')
                    break
            
            if custom_emoji_id:
                temp_data[chat_id] = {"id": custom_emoji_id, "char": emoji_text}
                user_states[chat_id] = "wait_for_emoji_details"
                send_message(chat_id, render_body_text(f"{PEM['ok']} Emoji ID পাওয়া গেছে: <code>{custom_emoji_id}</code>\n\n📌 এখন এটি সেভ করার জন্য টাইপ এবং নাম লিখুন।\n\n<b>ফরমেট:</b>\n`FLAG | 880 | BD | Bangladesh`\nঅথবা\n`APP | WhatsApp`"), reply_markup=get_cancel_kb())
            else:
                send_message(chat_id, render_body_text(f"{PEM['no']} কোনো Premium Emoji পাওয়া যায়নি! দয়া করে Custom Emoji সেন্ড করুন।"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_emoji_details" and text:
            parts = [p.strip() for p in text.split("|")]
            mode = parts[0].upper()
            eid = temp_data[chat_id]["id"]
            char = temp_data[chat_id]["char"]
            
            if mode == "FLAG" and len(parts) == 4:
                code, iso, name = parts[1], parts[2], parts[3]
                bot_settings["premium_flags"][code] = {"char": char, "iso": iso.upper(), "name": name, "id": eid}
                save_db()
                send_message(chat_id, render_body_text(f"{PEM['ok']} Flag Emoji সেভ হয়েছে!\nCode: {code} | Name: {name}"), reply_markup=emoji_settings_keyboard())
            elif mode == "APP" and len(parts) == 2:
                name = parts[1]
                bot_settings["premium_apps"][name.upper()] = {"char": char, "id": eid, "name": name.title()}
                save_db()
                send_message(chat_id, render_body_text(f"{PEM['ok']} App Emoji সেভ হয়েছে!\nName: {name}"), reply_markup=emoji_settings_keyboard())
            else:
                send_message(chat_id, render_body_text(f"{PEM['no']} ফরম্যাট ভুল!\n\nসঠিক ফরম্যাট:\n`FLAG | 880 | BD | Bangladesh`\n`APP | WhatsApp`"))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state in ["wait_for_flag_txt", "wait_for_app_txt"] and "document" in msg:
            doc = msg["document"]
            if not doc["file_name"].endswith(".txt"):
                send_message(chat_id, render_body_text(f"{PEM['no']} Please upload a .txt file only."))
                return
            file_id = doc["file_id"]
            file_info = requests.get(f"{BASE_URL}/getFile?file_id={file_id}").json()
            file_path = file_info["result"]["file_path"]
            content = requests.get(f"{FILE_URL}{file_path}").text
            
            mode = "flags" if state == "wait_for_flag_txt" else "apps"
            count = 0
            
            if mode == "flags":
                for line in content.splitlines():
                    json_match = re.search(r'(\{.*\})', line)
                    if json_match:
                        try:
                            data = json.loads(json_match.group(1))
                            char = data.get("emoji")
                            eid = data.get("id")
                            
                            prefix_str = line[:json_match.start()].strip()
                            code_match = re.search(r'\((\d+)\)', prefix_str)
                            iso_match = re.search(r'\(([A-Za-z]+)\)', prefix_str)
                            
                            if code_match and iso_match and char and eid:
                                code = code_match.group(1)
                                iso = iso_match.group(1).upper()
                                name = prefix_str.replace(f"({code})", "").replace(f"({iso_match.group(1)})", "").replace(char, "").strip()
                                bot_settings["premium_flags"][code] = {"char": char, "iso": iso, "name": name, "id": eid}
                                count += 1
                        except: pass
            else:
                for line in content.splitlines():
                    json_match = re.search(r'(\{.*\})', line)
                    if json_match:
                        try:
                            data = json.loads(json_match.group(1))
                            char = data.get("emoji")
                            eid = data.get("id")
                            
                            name_part = line[:json_match.start()].strip()
                            name = name_part.replace(char, '').strip() if char else name_part
                            
                            if char and eid and name:
                                bot_settings["premium_apps"][name.upper()] = {"char": char, "id": eid, "name": name}
                                count += 1
                        except: pass
            
            save_db()
            send_message(chat_id, render_body_text(f"{PEM['ok']} Successfully loaded {count} Emojis!"), reply_markup=emoji_settings_keyboard())
            del user_states[chat_id]
            return

        elif state == "wait_for_broadcast":
            msg_id = msg["message_id"]
            send_message(chat_id, render_body_text(f"{PEM['ok']} Broadcast started..."))
            threading.Thread(target=broadcast_copymessage, args=(chat_id, msg_id)).start()
            del user_states[chat_id]
            return

        elif state == "wait_for_txt" and "document" in msg:
            doc = msg["document"]
            if not doc["file_name"].endswith(".txt"):
                send_message(chat_id, render_body_text(f"{PEM['no']} Please upload a .txt file only."))
                return
            file_id = doc["file_id"]
            file_info = requests.get(f"{BASE_URL}/getFile?file_id={file_id}").json()
            file_path = file_info["result"]["file_path"]
            file_content = requests.get(f"{FILE_URL}{file_path}").text
            
            temp_data[chat_id] = {"numbers": file_content.splitlines(), "filename": doc["file_name"]}
            user_states[chat_id] = "wait_for_service"
            send_message(chat_id, render_body_text(f"{PEM['ok']} File received.\n\n📌 Enter the service name (e.g., WHATSAPP):"), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_service" and text:
            # Store one canonical service identity so future uploads cannot
            # create WhatsApp/WHATSAPP/whatsapp duplicates.
            temp_data[chat_id]["service"] = _canonical_service(text)
            user_states[chat_id] = "wait_for_country"
            send_message(chat_id, render_body_text(f"{PEM['ok']} Service set.\n\n🌍 Enter the country name (e.g., YEMEN):"), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_country" and text:
            country_input = text.strip()
            country_name, country_flag, country_id = _parse_admin_country_input(country_input)
            # Prefer ISO internally for standard countries.  For arbitrary custom
            # countries the normalized free-form identity is the merge key.
            country = country_id.upper() if len(country_id) == 2 and country_id.isalpha() else country_id
            service = _canonical_service(temp_data[chat_id]["service"])
            raw_numbers = temp_data[chat_id]["numbers"]
            
            clean_nums = []
            for num in raw_numbers:
                num = num.strip()
                if num:
                    if not num.startswith('+'): num = '+' + num
                    clean_nums.append(num)
            
            batch_id = str(uuid.uuid4())[:8]
            number_batches[batch_id] = {
                "filename": temp_data[chat_id]["filename"],
                "service": service,
                "country": country,
                "country_name": country_name,
                "country_flag": country_flag,
                "numbers": [{"num": n, "shares": 0, "used_by": []} for n in clean_nums]
            }
            total_uploaded_stats += len(clean_nums)
            save_db()
            
            app_full_name, _ = get_service_info_html(service)
            country_name, flag_char, _iso = _country_display(country, country_name, country_flag)
            # Use one real Unicode country flag only; never prepend the old
            # Telegram globe custom emoji beside the flag.
            broadcast_txt = f"➖➖➖➖➖➖➖➖\n《 NEW NUMBERS 》\n➖➖➖➖➖➖➖➖\n{flag_char + ' ' if flag_char else ''}{country_name} {service}\n➖➖➖➖➖➖➖➖\n📤 Total Added: <b>{len(clean_nums)}</b>\n➖➖➖➖➖➖➖➖\nUse /start to get your numbers!"
            broadcast_txt = render_body_text(broadcast_txt)
            
            send_message(chat_id, render_body_text(f"{PEM['ok']} Numbers added to local stock! Starting broadcast..."))
            
            def simple_broadcast(txt):
                b_session = requests.Session()
                url = f"{BASE_URL}/sendMessage"
                for u_id in list(all_known_users):
                    try:
                        b_session.post(url, json={"chat_id": u_id, "text": txt, "parse_mode": "HTML", "disable_web_page_preview": True}, timeout=5)
                    except: pass
                    time.sleep(0.035)
            threading.Thread(target=simple_broadcast, args=(broadcast_txt,)).start()
            
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_stex_key" and text:
            bot_settings["stex_keys"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ StexSMS API Key Added! Total Keys: {len(bot_settings.get('stex_keys', []))}"), reply_markup=stex_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_voltx_key" and text:
            bot_settings["voltx_keys"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ Voltx API Key Added! Total Keys: {len(bot_settings.get('voltx_keys', []))}"), reply_markup=voltx_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_sc" and text:
            code = text.strip().replace("+", "")
            if "search_countries" not in bot_settings: bot_settings["search_countries"] = []
            bot_settings["search_countries"].append(code)
            save_db()
            delete_message(chat_id, msg["message_id"])
            kb = []
            for idx, c in enumerate(bot_settings.get("search_countries", [])):
                kb.append([{"text": f"❌ Delete {c}", "callback_data": f"del_sc_{idx}", "style": "danger"}])
            kb.append([{"text": "➕ Add Country Code", "callback_data": "add_search_country", "style": "success"}])
            kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "primary"}])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🌍 <b>Allowed Search Countries:</b>\nOnly these country codes will be allowed in Search Number."), reply_markup={"inline_keyboard": kb})
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_vsc" and text:
            code = text.strip().replace("+", "")
            if "voltx_search_countries" not in bot_settings: bot_settings["voltx_search_countries"] = []
            bot_settings["voltx_search_countries"].append(code)
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "voltx_search_country", "id": "internal"})
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_nx_srv_name" and text:
            srv = text.strip().upper()
            if "stex_services" not in bot_settings: bot_settings["stex_services"] = {}
            if srv not in bot_settings["stex_services"]: bot_settings["stex_services"][srv] = {}
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "manage_stex_srv", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_nx_cnt_name" and text:
            cnt = text.strip()
            srv = temp_data[chat_id]["srv"]
            if cnt not in bot_settings["stex_services"][srv]: bot_settings["stex_services"][srv][cnt] = []
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"nx_srv_{srv}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_nx_addr" and text:
            srv, cnt = temp_data[chat_id]["srv"], temp_data[chat_id]["cnt"]
            new_range = text.strip().replace("+", "")
            
            if new_range not in bot_settings["stex_services"][srv][cnt]:
                bot_settings["stex_services"][srv][cnt].append(new_range)
                
                if "search_countries" not in bot_settings:
                    bot_settings["search_countries"] = []
                if new_range not in bot_settings["search_countries"]:
                    bot_settings["search_countries"].append(new_range)
                    
                save_db()
                
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"nx_cnt_{srv}_{cnt}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_vx_srv_name" and text:
            srv = text.strip().upper()
            if "voltx_services" not in bot_settings: bot_settings["voltx_services"] = {}
            if srv not in bot_settings["voltx_services"]: bot_settings["voltx_services"][srv] = {}
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "manage_voltx_srv", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_vx_cnt_name" and text:
            cnt = text.strip()
            srv = temp_data[chat_id]["srv"]
            if cnt not in bot_settings["voltx_services"][srv]: bot_settings["voltx_services"][srv][cnt] = []
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"vx_srv_{srv}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_vx_addr" and text:
            srv, cnt = temp_data[chat_id]["srv"], temp_data[chat_id]["cnt"]
            new_range = text.strip().replace("+", "")
            
            if new_range not in bot_settings["voltx_services"][srv][cnt]:
                bot_settings["voltx_services"][srv][cnt].append(new_range)
                
                if "voltx_search_countries" not in bot_settings:
                    bot_settings["voltx_search_countries"] = []
                if new_range not in bot_settings["voltx_search_countries"]:
                    bot_settings["voltx_search_countries"].append(new_range)
                    
                save_db()
                
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"vx_cnt_{srv}_{cnt}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_for_add_wm" and text:
            bot_settings["w_methods"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("💳 <b>WITHDRAWAL METHODS</b>\n\nManage your withdrawal methods below:"), reply_markup=w_methods_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_fj" and text:
            fj_entry = parse_force_join_entry(text)
            if not fj_entry:
                send_message(
                    chat_id,
                    render_body_text(
                        "❌ <b>Invalid channel format.</b>\n\n"
                        "Public: <code>@channelusername</code>\n"
                        "Private: <code>-1001234567890 | https://t.me/+InviteHash</code>\n\n"
                        "For private channels, the bot must be an administrator."
                    )
                )
                return

            # Avoid duplicate entries.
            existing_ids = {_fj_chat_id(x) for x in bot_settings.get("fj_channels", [])}
            if fj_entry["chat_id"] not in existing_ids:
                bot_settings["fj_channels"].append(fj_entry)
                save_db()

            delete_message(chat_id, msg["message_id"])
            edit_message(
                chat_id,
                temp_data[chat_id]["msg_id"],
                render_body_text(
                    "🔗 <b>FORCE JOIN SYSTEM</b>\n"
                    "Manage channels below:\n"
                    "<i>Public: @username\n"
                    "Private: -100... | invite link</i>"
                ),
                reply_markup=fj_settings_keyboard()
            )
            del user_states[chat_id]
            del temp_data[chat_id]
            return
            
        elif state == "wait_for_add_adm" and text:
            if text.isdigit():
                bot_settings["admins"].append(int(text))
                save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("👥 <b>ADMIN MANAGEMENT</b>\nManage your bot admins below:"), reply_markup=admin_settings_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_fw_id" and text:
            bot_settings["fw_groups"].append({"chat_id": text.strip(), "buttons": []})
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return
            
        elif state == "wait_for_add_fw_btn" and text:
            fw_idx = temp_data[chat_id]["fw_idx"]
            if "-" in text:
                parts = text.split("-", 1)
                btn_text = parts[0].strip()
                btn_url = parts[1].strip()
                
                emoji_id = None
                emoji_char = ""
                for ent in msg.get("entities", []):
                    if ent.get("type") == "custom_emoji":
                        emoji_id = ent.get("custom_emoji_id")
                        offset = ent.get("offset", 0)
                        length = ent.get("length", 0)
                        b_text = text.encode('utf-16-le')
                        emoji_char = b_text[offset*2:(offset+length)*2].decode('utf-16-le')
                        break
                
                if emoji_char:
                    btn_text = btn_text.replace(emoji_char, "").strip()
                    
                btn_data = {"text": btn_text, "url": btn_url}
                if emoji_id:
                    btn_data["icon_custom_emoji_id"] = emoji_id
                    
                bot_settings["fw_groups"][fw_idx]["buttons"].append(btn_data)
                save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"🛡 <b>Manage Group:</b> {bot_settings['fw_groups'][fw_idx]['chat_id']}"), reply_markup=specific_fw_group_keyboard(fw_idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return
            
        elif state == "wait_for_otp_channel_link" and text:
            bot_settings["otp_channel_url"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_otp_btn_name" and text:
            btn_text = text.strip()
            if not btn_text:
                send_message(chat_id, "❌ Button name cannot be empty.")
                return
            temp_data[chat_id]["btn_text"] = btn_text
            user_states[chat_id] = "wait_for_otp_btn_link"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🔗 <b>Enter Button Link</b>\n\nSend the button link (example: https://t.me/example):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "danger"}]]})
            delete_message(chat_id, msg["message_id"])
            return

        elif state == "wait_for_otp_btn_link" and text:
            btn_url = text.strip()
            if not re.match(r"^https?://\S+$", btn_url, re.I):
                send_message(chat_id, "❌ Please send a valid link starting with http:// or https://")
                return
            btn_text = temp_data[chat_id].get("btn_text", "Button")
            bot_settings.setdefault("otp_extra_buttons", []).append({
                "text": btn_text,
                "url": btn_url,
                "icon_custom_emoji_id": "5420517437885943844"
            })
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("⚙️ <b>BUTTON MANAGEMENT</b>\nSelect a button to manage:"), reply_markup=otp_button_management_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_otp_edit_btn" and text:
            if "-" not in text:
                send_message(chat_id, "❌ Use format: <code>Button Text - https://link.com</code>")
                return
            btn_text, btn_url = [x.strip() for x in text.split("-", 1)]
            if not btn_text or not btn_url:
                send_message(chat_id, "❌ Invalid button format.")
                return
            idx = temp_data[chat_id].get("btn_idx", -1)
            if 0 <= idx < len(bot_settings.get("otp_extra_buttons", [])):
                old_emoji = bot_settings["otp_extra_buttons"][idx].get("icon_custom_emoji_id")
                bot_settings["otp_extra_buttons"][idx] = {"text": btn_text, "url": btn_url}
                if old_emoji:
                    bot_settings["otp_extra_buttons"][idx]["icon_custom_emoji_id"] = old_emoji
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("⚙️ <b>BUTTON MANAGEMENT</b>\nSelect a button to manage:"), reply_markup=otp_button_management_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_otp_button_emoji" and (text or msg.get("entities") or msg.get("caption_entities")):
            idx = temp_data[chat_id].get("btn_idx", -1)
            emoji_id = get_custom_emoji_id_from_message(msg)
            if not emoji_id and text and text.strip().isdigit():
                emoji_id = text.strip()
            if not emoji_id:
                send_message(chat_id, "❌ Please send a Telegram Premium/custom emoji, or its custom emoji ID.")
                return
            if 0 <= idx < len(bot_settings.get("otp_extra_buttons", [])):
                bot_settings["otp_extra_buttons"][idx]["icon_custom_emoji_id"] = str(emoji_id)
                save_db()
                delete_message(chat_id, msg["message_id"])
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("⚙️ <b>BUTTON MANAGEMENT</b>\nSelect a button to manage:"), reply_markup=otp_button_management_keyboard())
                del user_states[chat_id]
                del temp_data[chat_id]
            return

        elif state == "wait_for_otp_link" and text:
            bot_settings["otp_link"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_panel_name" and text:
            p_name = text.strip()
            t_key = temp_data[chat_id].get("add_type", "api")
            msg_id = temp_data[chat_id]["msg_id"]
            delete_message(chat_id, msg["message_id"])
            
            if t_key == "logc":
                user_states[chat_id] = "wait_for_cpanel_url"
                temp_data[chat_id] = {"msg_id": msg_id, "p_data": {
                    "name": p_name, "type": "Auto Captcha Panel", "status": "ON", "records": 0, "login_status": "⏳ Pending First Login"
                }}
                edit_message(chat_id, msg_id, render_body_text("1️⃣ <b>Login URL</b>\n➡️ Panel এর Login Link দিন:"), reply_markup=get_cancel_kb())
                return
            else:
                bot_settings["panels"].append({
                    "name": p_name, "type": "API Panel", "status": "OFF", "api_url": "", "token": "", "records": 0
                })
                save_db()
                handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_api_panels", "id": "internal"})
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
                return

        elif state == "wait_for_p_api" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["api_url"] = text.strip()
            bot_settings["panels"][idx].pop("api_status", None)
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_p_tok" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["token"] = text.strip()
            bot_settings["panels"][idx].pop("api_status", None)
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_p_fapi" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["full_api_url"] = text.strip()
            bot_settings["panels"][idx].pop("api_status", None)
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Full API URL:</b> <code>{p.get('full_api_url', 'None')}</code>"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_p_rec" and text:
            if text.isdigit():
                idx = temp_data[chat_id]["p_idx"]
                bot_settings["panels"][idx]["records"] = int(text)
                save_db()
                delete_message(chat_id, msg["message_id"])
                p = bot_settings["panels"][idx]
                
                ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            else:
                send_message(chat_id, render_body_text("❌ Please enter a valid number! Try again."), reply_markup=get_cancel_kb())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "set_dxa":
            msg_id = temp_data[chat_id]["msg_id"]
            key = temp_data[chat_id]["key"]
            try:
                value = text.strip()
                if key in ["min_withdraw", "otp_reward", "refer_reward"]:
                    bot_settings[key] = float(value)
                elif key in ["cooldown", "num_req", "num_share"]:
                    bot_settings[key] = int(value)
                elif key == "w_group":
                    # Accept: numeric chat ID, @username, public t.me/telegram.me link,
                    # and Telegram /c/<internal_id>/<message_id> links.
                    # Private + invite links cannot be resolved by the Bot API.
                    if not value or value.upper() in ("OFF", "NONE", "DISABLE"):
                        bot_settings[key] = ""
                    elif re.fullmatch(r"-?\d+", value):
                        bot_settings[key] = value
                    else:
                        from urllib.parse import urlparse
                        v = value.strip()
                        if v.startswith("@") and re.fullmatch(r"@[A-Za-z0-9_]{5,}", v):
                            bot_settings[key] = v
                        else:
                            raw = v
                            if not re.match(r"^https?://", raw, re.I):
                                raw = "https://" + raw
                            parsed = urlparse(raw)
                            host = (parsed.netloc or "").lower().split(":")[0]
                            path = (parsed.path or "").strip("/")
                            if host not in ("t.me", "www.t.me", "telegram.me", "www.telegram.me"):
                                raise ValueError("Use a Telegram chat ID, @username, or a Telegram link.")

                            parts = [x for x in path.split("/") if x]
                            if parts and parts[0].lower() == "c" and len(parts) >= 2 and parts[1].isdigit():
                                # Telegram private/internal channel-group message link:
                                # internal ID 123... maps to chat ID -100123...
                                bot_settings[key] = "-100" + parts[1]
                            elif parts and parts[0].startswith("+"):
                                raise ValueError("Private invite links (+...) cannot be converted to a chat ID by the Telegram Bot API. Use the group's numeric chat ID instead.")
                            elif parts and re.fullmatch(r"[A-Za-z0-9_]{5,}", parts[0]):
                                bot_settings[key] = "@" + parts[0]
                            else:
                                raise ValueError("Invalid Telegram link. Example: https://t.me/MyGroup")
                else:
                    bot_settings[key] = value
                save_db()
                delete_message(chat_id, msg["message_id"])

                # Immediately test the withdrawal group after changing W. GROUP.
                if key == "w_group" and bot_settings.get("w_group"):
                    test_text = (
                        "🧪 <b>W. GROUP TEST NOTIFICATION</b>\n\n"
                        "✅ <b>Withdrawal notification group is connected.</b>\n"
                        "👥 This test message contains NO Approve/Reject buttons.\n"
                        f"🎯 <b>DESTINATION:</b> <code>{html.escape(str(bot_settings['w_group']))}</code>\n"
                        f"🕒 <code>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code>"
                    )
                    test_res = send_message(bot_settings["w_group"], render_body_text(test_text))
                    if test_res.get("ok"):
                        result_note = "\n\n✅ <b>W. GROUP TEST: SUCCESS</b>"
                    else:
                        result_note = f"\n\n❌ <b>W. GROUP TEST FAILED</b>\n<code>{html.escape(str(test_res.get('description', 'Unknown Telegram API error')))}</code>"
                else:
                    result_note = ""

                edit_message(chat_id, msg_id, render_body_text("🕹 <b>DXA CONTROL PANEL</b>" + result_note), reply_markup=dxa_control_keyboard())
            except Exception as e:
                delete_message(chat_id, msg["message_id"])
                edit_message(chat_id, msg_id, render_body_text(f"🕹 <b>DXA CONTROL PANEL</b>\n\n❌ {html.escape(str(e))}"), reply_markup=dxa_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_search" and text:
            query = text.strip().replace("+", "")
            if not query.isdigit() or len(query) < 3 or len(query) > 9:
                send_message(chat_id, render_body_text("❌ Please enter a valid 3 to 9 digit number!"))
                return
                
            wait_msg = send_message(chat_id, render_body_text("⌛ <i>Processing... Finding Number...</i>"))
            wait_msg_id = wait_msg.get("result", {}).get("message_id")
            
            # 🌟 ১. প্রথমে Local থেকে নাম্বার খুঁজবে (যে কোনো দেশের জন্য)
            found_indices = []
            active_prefix = re.sub(r"\D", "", str(user_prefixes.get(chat_id, "")).strip())
            for b_id, b_data in number_batches.items():
                for idx, n_obj in enumerate(b_data["numbers"]):
                    clean_num = re.sub(r"\D", "", str(n_obj.get("num", "")))
                    prefix_ok = (not active_prefix) or clean_num.startswith(active_prefix)
                    if clean_num.startswith(query) and prefix_ok and chat_id not in n_obj.get("used_by", []):
                        found_indices.append((b_id, idx))
            
            fetched_nums = []
            if not found_indices:
                # 🌟 ২. যদি Local এ না পায়, তখন চেক করবে Voltx বা StexSMS থেকে আনা যাবে কি না
                stex_allowed = bot_settings.get("search_countries", [])
                voltx_allowed = bot_settings.get("voltx_search_countries", [])
                
                # ফিক্স: অ্যাডমিন প্যানেলে দেশ এড না থাকলে অটোমেটিক Block করে দেবে
                is_stex_allowed = any(query.startswith(c) for c in stex_allowed) if stex_allowed else False
                is_voltx_allowed = any(query.startswith(c) for c in voltx_allowed) if voltx_allowed else False
                
                if not is_stex_allowed and not is_voltx_allowed:
                    if wait_msg_id: delete_message(chat_id, wait_msg_id)
                    send_message(chat_id, render_body_text("❌ This country code is not allowed!"), reply_markup=main_menu(chat_id))
                    del user_states[chat_id]
                    return
                    
                if wait_msg_id: edit_message(chat_id, wait_msg_id, render_body_text("⌛ <i>Processing... Finding Number via API...</i>"))
                
                is_voltx_used = False
                req_count = bot_settings.get("num_req", 1)
                
                # 🌟 প্রথমে Voltx চেক করবে
                if is_voltx_allowed:
                    voltx_keys = bot_settings.get("voltx_keys", [])
                    _voltx_search_attempts = (req_count * 10) if active_prefix else req_count
                    for _ in range(max(req_count, _voltx_search_attempts)):
                        if len(fetched_nums) >= req_count: break
                        for api_key in voltx_keys:
                            try:
                                headers = {"mauthapi": api_key}
                                res = requests.post(f"{VOLTX_BASE_URL}/getnum", json={"rid": query}, headers=headers, timeout=10)
                                resp_data = res.json()
                                if resp_data.get("meta", {}).get("code") == 200 and resp_data.get("data"):
                                    api_num = resp_data.get("data", {}) or {}
                                    # Accept the number field names commonly returned by the panel.
                                    num_str = ""
                                    for nk in ("no_plus_number", "national_number", "number", "phone", "msisdn", "mobile", "mobile_number"):
                                        candidate = str(api_num.get(nk, "") or "").strip()
                                        candidate_digits = re.sub(r"\D", "", candidate)
                                        if 5 <= len(candidate_digits) <= 18:
                                            num_str = candidate_digits
                                            break
                                    if not num_str:
                                        continue
                                    if active_prefix and not num_str.startswith(active_prefix):
                                        continue
                                    fetched_nums.append(num_str)
                                    voltx_assigned_numbers[num_str] = chat_id 
                                    is_voltx_used = True
                                    global total_assigned_stats
                                    total_assigned_stats += 1
                                    increment_numbers_used(chat_id)
                                    break # শুধু api_key লুপ ব্রেক করবে, যাতে পরের নাম্বার আনতে পারে
                            except: continue

                # 🌟 Voltx এ না পেলে বা আরও নাম্বার লাগলে StexSMS তে চেক করবে
                if len(fetched_nums) < req_count and is_stex_allowed:
                    stex_keys = bot_settings.get("stex_keys", [])
                    
                    for _ in range(req_count - len(fetched_nums)): 
                        for api_key in stex_keys:
                            try:
                                headers = {"mauthapi": api_key}
                                res = requests.post(f"{STEX_BASE_URL}/getnum", json={"rid": query}, headers=headers, timeout=10)
                                data = res.json()
                                if data.get("meta", {}).get("code") == 200 and data.get("data"):
                                    num_str = str(data["data"].get("no_plus_number", "")).replace("+", "")
                                    if not num_str: num_str = str(data["data"].get("national_number", ""))
                                    num_str = re.sub(r"\D", "", str(num_str))
                                    if active_prefix and not num_str.startswith(active_prefix):
                                        continue
                                    fetched_nums.append(num_str)
                                    stex_assigned_numbers[num_str] = chat_id 
                                    total_assigned_stats += 1
                                    increment_numbers_used(chat_id)
                                    break 
                            except: continue
                        
                if not fetched_nums:
                    if wait_msg_id: delete_message(chat_id, wait_msg_id)
                    if active_prefix:
                        send_message(chat_id, render_body_text("⚠️ <b>এই Prefix-এর কোনো নাম্বার বর্তমানে স্টকে Available নেই।</b>\n\n🔄 <b>দয়া করে অন্য Prefix দিয়ে চেষ্টা করুন অথবা Prefix OFF করুন।</b>"), reply_markup=main_menu(chat_id))
                    else:
                        send_message(chat_id, render_body_text("❌ Number out of stock!"), reply_markup=main_menu(chat_id))
                    del user_states[chat_id]
                    return
                save_db()
            else:
                random.shuffle(found_indices)
                for b_id, idx in found_indices:
                    if len(fetched_nums) >= bot_settings.get("num_req", 1): break
                    n_obj = number_batches[b_id]["numbers"][idx]
                    num_str = n_obj["num"]
                    
                    fetched_nums.append(num_str)
                    
                    n_obj["shares"] += 1
                    n_obj["used_by"].append(chat_id)
                    total_assigned_stats += 1
                    increment_numbers_used(chat_id)
                    if n_obj["shares"] >= bot_settings.get("num_share", 1):
                        n_obj["to_remove"] = True
                        used_numbers_list.append(num_str)
                
                for b_id in number_batches:
                    number_batches[b_id]["numbers"] = [n for n in number_batches[b_id]["numbers"] if not n.get("to_remove")]
                save_db()
                
            if wait_msg_id: edit_message(chat_id, wait_msg_id, render_body_text("✅ Number Found!"))
            kb = []
            flags_db = bot_settings.get("premium_flags", {})
            for num in fetched_nums:
                _, iso = get_flag_and_code(num)
                display_num = f"+{num}" if not num.startswith("+") else num
                
                emoji_id = "5780471598922337683" # Default Flag
                for flag_code, flag_data in flags_db.items():
                    if iso == flag_data.get("iso"):
                        if "id" in flag_data: emoji_id = flag_data["id"]
                        break
                kb.append([{"text": f"{display_num}", "icon_custom_emoji_id": emoji_id, "copy_text": {"text": display_num}, "style": "primary"}])
                
            vtx_ext = "_vtx" if 'is_voltx_used' in locals() and is_voltx_used else ""
            kb.append([{"text": "Change Number", "icon_custom_emoji_id": "5465368548702446780", "callback_data": f"c_n_s_{query}{vtx_ext}", "style": "danger"},
                       {"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}])
            
            c_btns = bot_settings["custom_messages"].get("search_number", {}).get("buttons", [])
            for c_b in c_btns: 
                b_copy = c_b.copy()
                if "style" not in b_copy: b_copy["style"] = "primary"
                kb.append([b_copy])
            
            kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
            
            if wait_msg_id:
                edit_message(chat_id, wait_msg_id, "NEW NUMBER\n", reply_markup={"inline_keyboard": kb})
                user_active_sessions[chat_id] = {"msg_id": wait_msg_id, "nums": fetched_nums, "service": service_from_cb if "service_from_cb" in locals() and service_from_cb else (service if "service" in locals() else "")}
            else:
                msg_res = send_message(chat_id, "NEW NUMBER\n", reply_markup={"inline_keyboard": kb})
                if msg_res and "result" in msg_res:
                    user_active_sessions[chat_id] = {"msg_id": msg_res["result"]["message_id"], "nums": fetched_nums, "service": service_from_cb if "service_from_cb" in locals() and service_from_cb else (service if "service" in locals() else "")}
            return
            
        elif state == "wait_for_withdraw_amount" and text:
            msg_id_to_edit = temp_data[chat_id].get("msg_id")
            try:
                amount = float(text.strip())
                bal = temp_data[chat_id]["balance"]
                min_w = bot_settings['min_withdraw']
                
                if amount < min_w:
                    if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text(f"❌ Minimum withdrawal is {min_w} ৳!\n💰 Balance: {bal} ৳\n\n📝 Enter again:"), reply_markup=get_cancel_kb())
                    return
                if amount > bal:
                    if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text(f"❌ You don't have enough balance!\n💰 Balance: {bal} ৳\n\n📝 Enter again:"), reply_markup=get_cancel_kb())
                    return
                    
                temp_data[chat_id]["amount"] = amount
                user_states[chat_id] = "wait_for_withdraw_number"
                if msg_id_to_edit:
                    edit_message(chat_id, msg_id_to_edit, render_body_text(f"✅ Amount: {amount} ৳\n\n📱 Now send your <b>{temp_data[chat_id]['method']}</b> account number:"), reply_markup=get_cancel_kb())
            except ValueError:
                if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text("❌ Invalid amount!\n\n📝 Please send a valid number:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_2fa_key" and text:
            msg_id_to_edit = temp_data.get(chat_id, {}).get("msg_id")
            delete_message(chat_id, msg.get("message_id")) # ইউজারের মেসেজ ডিলিট

            if not msg_id_to_edit:
                send_message(chat_id, render_body_text("❌ Error: Message not found. Try again."))
                del user_states[chat_id]
                return

            try:
                secret = text.strip().replace(" ", "")
                totp = pyotp.TOTP(secret)
                code = totp.now()
                remaining_time = 30 - (int(time.time()) % 30)
                
                success_txt = (
                    f"━━━━━━━━━━━━━━━\n"
                    f"《 🔐 <b>2FA CODE</b> 》\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"🔐 <b>CODE:</b> <code>{code}</code>\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"🕓 <b>EXPIRES IN:</b> {remaining_time}s\n"
                    f"━━━━━━━━━━━━━━━"
                )
                kb = [[{"text": f"Click to copy {code}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": code}, "style": "success"}],
                      [{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"ref_2fa_{secret}", "style": "primary"},
                       {"text": "New Code", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "gen_2fa", "style": "danger"}],
                      [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
                
                edit_message(chat_id, msg_id_to_edit, render_body_text(success_txt), reply_markup={"inline_keyboard": kb})
                del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            except Exception:
                error_txt = "━━━━━━━━━━━━━━━\n《 🔑 <b>ENTER 2FA KEY</b> 》\n━━━━━━━━━━━━━━━\n📝 <b>SEND YOUR 2FA SECRET KEY</b>\n━━━━━━━━━━━━━━━\n❌ <b>Invalid Secret Key! Try again.</b>\n━━━━━━━━━━━━━━━"
                cancel_kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_2fa", "style": "danger"}]]}
                edit_message(chat_id, msg_id_to_edit, render_body_text(error_txt), reply_markup=cancel_kb)
            return

        elif state == "wait_for_withdraw_number":
            msg_id_to_edit = temp_data[chat_id].get("msg_id")
            
            method = temp_data[chat_id]["method"]
            amount = temp_data[chat_id]["amount"]
            number = text
            req_id = f"W_{str(uuid.uuid4())[:6].upper()}"
            
            first_name = msg.get("from", {}).get("first_name", "User")
            last_name = msg.get("from", {}).get("last_name", "")
            full_name = f"{first_name} {last_name}".strip()
            
            # Deduct only after a confirmed balance update. Never create a withdrawal
            # request when the balance write itself failed.
            bal_ok, old_bal, new_bal, bal_err = update_balance(chat_id, -amount)
            if not bal_ok:
                send_message(chat_id, render_body_text(
                    f"❌ <b>Withdrawal could not be submitted.</b>\n\n⚠️ Balance update failed: {html.escape(str(bal_err))}"
                ))
                del user_states[chat_id]
                del temp_data[chat_id]
                return
            pending_withdrawals[req_id] = {"user_id": chat_id, "amount": amount, "method": method, "number": number, "full_name": full_name, "status": "pending", "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            _save_local_withdrawals()
            
            # Save to Firestore for History
            if db:
                try:
                    db.collection('withdrawals').document(req_id).set({
                        "user_id": str(chat_id),
                        "amount": amount,
                        "method": method,
                        "status": "pending",
                        "number": str(number),
                        "full_name": full_name,
                        "timestamp": firestore.SERVER_TIMESTAMP
                    })
                except: pass
                
            admin_msg = f"🎙 <b>NEW WITHDRAWAL REQUEST</b>\n\n👤 <b>USER:</b> <a href='tg://user?id={chat_id}'>{full_name}</a>\n🆔 <b>USER ID:</b> <code>{chat_id}</code>\n💳 <b>WITHDRAWAL:</b> {amount} TK\n🍏 <b>NUMBER:</b> <code>{number}</code>\n🏦 <b>METHOD:</b> {method}\n\n🧾 <b>REQ ID:</b> <code>{req_id}</code>\n⏳ <b>STATUS:</b> PENDING"
            kb = {"inline_keyboard": [[{"text": "APPROVE", "icon_custom_emoji_id": "5352694861990501856", "callback_data": f"wapp_{req_id}", "style": "success"}, {"text": "REJECT", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"wrej_{req_id}", "style": "danger"}]]}
            # W. GROUP is notification-only: members see the request, but NO Approve/Reject buttons.
            # Approve/Reject controls are sent only to bot admins in their private chat.
            group_result = None
            if bot_settings.get("w_group"):
                group_result = send_message(bot_settings["w_group"], render_body_text(admin_msg))
                if not group_result.get("ok", False):
                    err = group_result.get("description", "Unknown Telegram API error")
                    print(f"[WITHDRAWAL] Group notification failed for {bot_settings['w_group']}: {err}")
            admin_notice = admin_msg
            if bot_settings.get("w_group") and group_result is not None and not group_result.get("ok", False):
                admin_notice += f"\n\n⚠️ <b>W. GROUP DELIVERY FAILED:</b> <code>{html.escape(str(group_result.get('description', 'Unknown error')))}</code>"
            for admin_id in list(bot_settings.get("admins", [])):
                try:
                    send_message(admin_id, render_body_text(admin_notice), reply_markup=kb)
                except Exception as e:
                    print(f"[WITHDRAWAL] Admin notification error {admin_id}: {e}")
            
            kb = {"inline_keyboard": [[{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]}
            success_text = f"{PEM['ok']} Your withdrawal request has been submitted!\n\n🧾 <b>Req ID:</b> {req_id}\n💰 <b>Amount:</b> {amount} ৳\n🏦 <b>Method:</b> {method}\n📱 <b>Number:</b> <code>{number}</code>"
            
            if msg_id_to_edit:
                edit_message(chat_id, msg_id_to_edit, render_body_text(success_text), reply_markup=kb)
            else:
                send_message(chat_id, render_body_text(success_text), reply_markup=kb)
                
            del user_states[chat_id]
            del temp_data[chat_id]
            return

    # --- Regular Commands ---
    if text.startswith("/start"):
        get_user(chat_id)
        
        # --- PROCESS PENDING REFERRAL ---
        if db:
            doc = db.collection('users').document(str(chat_id)).get()
            if doc.exists:
                u_data = doc.to_dict()
                if u_data.get("referred_by") and not u_data.get("ref_paid"):
                    inviter = u_data["referred_by"]
                    db.collection('users').document(str(chat_id)).update({"ref_paid": True})
                    reward = bot_settings.get("refer_reward", 0.2)
                    update_balance(inviter, reward)
                    db.collection('users').document(str(inviter)).update({"total_refers": firestore.Increment(1)})
                    ref_msg = (
                        f"{PEM['gift']} <b>New Referral !</b>\n"
                        f"------------------\n"
                        f"🔥 <b>You Received {reward} TK</b>\n"
                        f"------------------\n"
                        f"{PEM['user']} <b>From User ID:</b> <code>{chat_id}</code>"
                    )
                    send_message(inviter, render_body_text(ref_msg))
                    
        c_msg = bot_settings["custom_messages"].get("start", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['hi']} Welcome!"))
        kb = []
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        
        if kb:
            send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})
            send_message(chat_id, render_body_text(f"{PEM['gear']} Navigation Menu:"), reply_markup=main_menu(chat_id))
        else:
            send_message(chat_id, txt, reply_markup=main_menu(chat_id))
            
    elif text == "TRAFFIC":
        txt, markup = build_traffic_ui()
        send_message(chat_id, txt, reply_markup=markup)
        
    elif text == "Refer":
        u_data = get_user(chat_id)
        ref_link = f"https://t.me/{BOT_USERNAME}?start={chat_id}"
        c_msg = bot_settings["custom_messages"].get("refer", {})
        
        raw_txt = c_msg.get("text", f"{PEM['gift']} Refer").replace("{ref_link}", ref_link).replace("{total_ref}", str(u_data.get('total_refers', 0))).replace("{ref_reward}", str(bot_settings['refer_reward']))
        txt = render_body_text(raw_txt)
        
        kb = [[{"text": "COPY LINK", "icon_custom_emoji_id": "5192739271886282680", "copy_text": {"text": ref_link}, "style": "success"}]]
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        kb.append([{"text": "CLOSE", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "WITHDRAWAL":
        if not bot_settings["withdraw_on"]:
            send_message(chat_id, render_body_text(f"{PEM['no']} Withdrawals are currently disabled."))
            return
        
        u_data = get_user(chat_id)
        bal = u_data.get('balance', 0.0)
        
        c_msg = bot_settings["custom_messages"].get("withdrawal", {})
        raw_txt = c_msg.get("text", "Withdrawal").replace("{bal}", str(bal)).replace("{total_otp}", str(u_data.get('total_otps', 0))).replace("{total_ref}", str(u_data.get('total_refers', 0))).replace("{min_w}", str(bot_settings['min_withdraw']))
        txt = render_body_text(raw_txt)
        
        kb = []
        for m in bot_settings["w_methods"]:
            kb.append([{"text": m.strip(), "icon_custom_emoji_id": "5190899075968441286", "callback_data": f"sel_wm_{m.strip()}", "style": "primary"}])
        
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        kb.append([{"text": "Cancel", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "Admin Panel" and is_admin(chat_id):
        send_message(chat_id, get_admin_text(), reply_markup=admin_panel_keyboard())

    elif text == "GET NUMBER":
        service_catalog = _merged_get_number_catalog()
        all_services = set(service_catalog.keys())
        
        if not all_services:
            send_message(chat_id, render_body_text(f"{PEM['no']} No numbers or services available!"))
        else:
            c_msg = bot_settings["custom_messages"].get("get_number", {})
            txt = render_body_text(c_msg.get("text", f"{PEM['pin']} Select Service"))
            
            apps_db = bot_settings.get("premium_apps", {})
            kb = []
            for s in all_services:
                emoji_id = "5352694861990501856" # Default icon
                for app_key, app_data in apps_db.items():
                    if s.upper() == app_key or s.upper() in app_key or app_key in s.upper():
                        if "id" in app_data:
                            emoji_id = app_data["id"]
                            break
                kb.append([{"text": f"{str(s).upper()}", "icon_custom_emoji_id": emoji_id, "callback_data": f"g_s_{s}", "style": "primary"}])
            
            service_names = {_canonical_service(x) for x in all_services if _canonical_service(x)}
            for b in c_msg.get("buttons", []):
                b_copy = b.copy()
                # A custom Menu Design button that has the same text as a real
                # service is only a duplicate of the dynamic service button.
                # Keep unrelated custom buttons exactly as configured.
                custom_name = _canonical_service(b_copy.get("text", ""))
                if custom_name and custom_name in service_names:
                    continue
                if "style" not in b_copy: b_copy["style"] = "primary"
                kb.append([b_copy])
            kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_main", "style": "danger"}])
            
            send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "Search Number":
        user_states[chat_id] = "wait_for_search"
        c_msg = bot_settings["custom_messages"].get("search_number", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['num']} Search Number"))
        kb = [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_state", "style": "danger"}]]
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "2FA ONLINE" or text == "🔐 2FA ONLINE":
        txt = "━━━━━━━━━━━━━━━\n《 🔐 <b>2FA ONLINE</b> 》\n━━━━━━━━━━━━━━━\n<i>Generate your 2FA security code instantly using your secret key.</i>\n━━━━━━━━━━━━━━━"
        kb = [[{"text": "Generate 2fa code", "icon_custom_emoji_id": "5353022963132174959", "callback_data": "gen_2fa", "style": "success"}],
              [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
        send_message(chat_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif text == "SUPPORT":
        c_msg = bot_settings["custom_messages"].get("support", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['msg']} Support"))
        if not txt.strip(): txt = render_body_text(f"{PEM['msg']} Support")
        kb = []
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
            
        sup_link = bot_settings.get("support_link", "")
        if sup_link:
            kb.insert(0, [{"text": "Contact Support", "icon_custom_emoji_id": "5337302974806922068", "url": sup_link, "style": "success"}])
            
        kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb} if kb else None)

def expire_previous_number(chat_id):
    if chat_id in user_active_sessions:
        prev_data = user_active_sessions[chat_id]
        prev_msg_id = prev_data["msg_id"]
        nums = prev_data["nums"]
        
        # StexSMS সিস্টেম থেকে রিমুভ করা যাতে ইনবক্সে আর মেসেজ না যায়
        for num in nums:
            if num in stex_assigned_numbers:
                del stex_assigned_numbers[num]
        save_db()
        
        # আগের মেসেজ ইডিট করে Expired বাটন বসানো
        kb = [[{"text": "Number Expired", "icon_custom_emoji_id": "5336997731481193790", "callback_data": "ignore", "style": "danger"}]]
        try:
            edit_message(chat_id, prev_msg_id, "NEW NUMBER\n", reply_markup={"inline_keyboard": kb})
        except:
            pass
        del user_active_sessions[chat_id]

# ==========================================
# Admin User List System
# ==========================================
def hydrate_user_identity_from_telegram(user_id, current_data=None):
    """Backfill missing name/username directly from Telegram when possible."""
    current_data = current_data or {}
    name_value = str(current_data.get("full_name") or current_data.get("name") or "").strip()
    username_value = str(current_data.get("username") or "").strip()
    # Treat placeholder values as missing so the real Telegram identity is
    # refreshed instead of leaving "Unknown User"/blank identity behind.
    has_name = bool(name_value and name_value.lower() not in {"unknown user", "user"})
    has_username = bool(username_value and username_value.lower() not in {"not set", "none"})
    if has_name and has_username:
        return current_data
    try:
        res = api_call("getChat", {"chat_id": int(user_id)})
        if res and res.get("ok") and isinstance(res.get("result"), dict):
            chat = res["result"]
            first = str(chat.get("first_name") or "").strip()
            last = str(chat.get("last_name") or "").strip()
            username = str(chat.get("username") or "").strip().lstrip("@")
            full_name = (first + " " + last).strip() or username
            patch = {}
            if full_name:
                patch["full_name"] = full_name
            if username:
                patch["username"] = username
            if patch:
                patch["user_id"] = int(user_id) if str(user_id).isdigit() else user_id
                current_data.update(patch)
                try:
                    if db:
                        db.collection("users").document(str(user_id)).set(patch, merge=True)
                    uid_key = int(user_id) if str(user_id).isdigit() else user_id
                    if uid_key in user_cache:
                        user_cache[uid_key].update(patch)
                except Exception:
                    pass
    except Exception:
        pass
    return current_data

def get_all_users_for_admin():
    """Read User List statistics directly from Firestore so cached/stale values are not shown."""
    users = []
    if db:
        try:
            # Always read the canonical Firestore document for the admin list.
            # This deliberately bypasses user_cache, so Balance/OTP/Number/Referral
            # values shown here are the latest stored values.
            for doc in db.collection('users').stream():
                data = doc.to_dict() or {}
                # Firestore document ID is the authoritative fallback. Never
                # allow a blank/invalid user ID into the admin views.
                stored_uid = data.get("user_id")
                data["user_id"] = str(stored_uid).strip() if stored_uid is not None and str(stored_uid).strip() else str(doc.id)
                data["balance"] = data.get("balance", 0.0)
                data["total_refers"] = data.get("total_refers", 0)
                data["total_otps"] = data.get("total_otps", 0)
                data["numbers_used"] = data.get("numbers_used", 0)

                # Normalize numeric Firestore values before sorting/displaying.
                for field in ("total_refers", "total_otps", "numbers_used"):
                    try:
                        data[field] = int(float(data[field] or 0))
                    except Exception:
                        data[field] = 0
                try:
                    data["balance"] = float(data["balance"] or 0)
                except Exception:
                    data["balance"] = 0.0

                # If a counter write was temporarily unavailable, use the
                # persistent local counter rather than displaying a false zero.
                local_uid = str(data.get("user_id", doc.id))
                data["numbers_used"] = max(
                    int(data.get("numbers_used", 0) or 0),
                    _local_counter_value(local_uid, "numbers_used")
                )
                data["total_otps"] = max(
                    int(data.get("total_otps", 0) or 0),
                    _local_counter_value(local_uid, "total_otps")
                )
                try:
                    hydrate_user_identity_from_telegram(data["user_id"], data)
                except Exception:
                    pass
                # Never allow a blank/missing ID in the admin list.
                data["user_id"] = str(data.get("user_id") or doc.id)
                users.append(data)
        except Exception as e:
            print(f"[USER LIST] Firestore read error: {e}")

    # Only use local cache as a fallback when Firestore is unavailable.
    if not users:
        for uid in list(all_known_users):
            try:
                data = get_user(int(uid)).copy()
                data["user_id"] = str(data.get("user_id") or uid)
                try:
                    hydrate_user_identity_from_telegram(data["user_id"], data)
                except Exception:
                    pass
                data.setdefault("balance", 0.0)
                data.setdefault("total_refers", 0)
                data.setdefault("total_otps", 0)
                data.setdefault("numbers_used", 0)
                users.append(data)
            except Exception:
                pass

    # Highest activity first: OTP, then numbers used, then referrals.
    users.sort(key=lambda u: (u.get("total_otps", 0), u.get("numbers_used", 0), u.get("total_refers", 0)), reverse=True)
    return users

def _user_info_lines(u, serial, html_mode=True):
    def num(v):
        try:
            return float(v or 0)
        except Exception:
            return 0.0
    name = str(u.get("full_name") or u.get("name") or "Unknown User").strip()
    if not name or name.lower() in {"unknown user", "user"}:
        name = "Unknown User"
    username = str(u.get("username") or "").strip().lstrip("@")
    username_text = "@" + username if username else "Not Set"
    uid = str(u.get("user_id") or "Unknown")
    try:
        balance = float(u.get("balance", 0) or 0)
    except Exception:
        balance = 0.0
    safe_name = html.escape(name) if html_mode else name
    safe_username = html.escape(username_text) if html_mode else username_text
    serial_text = f"<b>{serial}.</b>" if html_mode else f"{serial}."
    uid_text = f"<code>{uid}</code>" if html_mode else uid
    return [
        serial_text,
        f"⫷𓊈 <b>{safe_name}</b> 𓊉⫸" if html_mode else f"⫷𓊈 {safe_name} 𓊉⫸",
        f"👤 Username: {safe_username}",
        f"🆔 User ID: {uid_text}",
        f"🔐 Received OTP: {int(num(u.get('total_otps')))}",
        f"📱 Numbers Used: {int(num(u.get('numbers_used')))}",
        f"👥 Referrals: {int(num(u.get('total_refers')))}",
        f"💰 Balance: {balance:.2f} TK",
        "━━━━━━━━━━━━━━━━━━"
    ]

def get_user_list_page(page=0, per_page=10):
    users = get_all_users_for_admin()
    total = len(users)
    max_page = max(0, (total - 1) // per_page) if total else 0
    page = max(0, min(int(page), max_page))
    chunk = users[page * per_page:(page + 1) * per_page]
    # Existing users created before identity tracking are repaired on-demand.
    for u in chunk:
        try:
            hydrate_user_identity_from_telegram(u.get("user_id"), u)
        except Exception:
            pass

    lines = ["👥 <b>USERS ALL INFO</b>", f"📄 Page: {page + 1}", f"👥 Total Users: {total}", "━━━━━━━━━━━━━━━━━━"]
    if not chunk:
        lines.append("<i>No users found.</i>")
    for i, u in enumerate(chunk, start=page * per_page + 1):
        lines.extend(_user_info_lines(u, i, html_mode=True))
    return render_body_text("\n".join(lines)), page, max_page, total

def build_all_users_txt():
    users = get_all_users_for_admin()
    lines = ["ALL USERS LIST", f"Total Users: {len(users)}", "", "━━━━━━━━━━━━━━━━━━"]
    for i, u in enumerate(users, start=1):
        lines.extend(_user_info_lines(u, i, html_mode=False))
    return "\n".join(lines).encode("utf-8")

def user_list_keyboard(page, max_page):
    nav = [
        {"text": "Download TXT", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "download_all_users_txt", "style": "success"}
    ]
    if page < max_page:
        nav.append({"text": "Next", "icon_custom_emoji_id": "5337132498965010628", "callback_data": f"user_list_{page+1}", "style": "primary"})
    return {"inline_keyboard": [nav, [{"text": "Back to Admin Panel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]}

# ==========================================
# Callback Query Handler
# ==========================================
def handle_callback(call):
    global total_assigned_stats
    chat_id = call["message"]["chat"]["id"]
    chat_type = call["message"]["chat"].get("type", "private")
    data = call.get("data", "")

    # Save the latest Telegram identity even when the user only presses buttons.
    if chat_type == "private":
        register_user_local(chat_id)
        update_user_identity(chat_id, call.get("from", {}))

    # 🌟 Button Loading Fix: বাটন চাপার সাথে সাথেই টেলিগ্রামকে Response দিয়ে দেওয়া, যাতে বাটন আটকে না থাকে!
    if not data.startswith("test_p_conn_") and not data.startswith("c_n_") and not data.startswith("g_c_"):
        try: threading.Thread(target=answer_callback, args=(call["id"],)).start()
        except: pass

    if chat_type != "private" and not (data.startswith("wapp_") or data.startswith("wrej_")):
        return

    msg_id = call["message"]["message_id"]

    if chat_type == "private":
        if is_user_banned(chat_id):
            answer_callback(call["id"], "🚫 You are banned from using this bot!", show_alert=True)
            return

        if not check_force_join(chat_id) and data not in ("check_fj", "back_to_get_number", "back_to_main"):
            send_force_join_msg(chat_id)
            return

    if data == "fj_link_missing":
        answer_callback(call["id"], "⚠️ Admin must configure the private channel invite link.", show_alert=True)
        return

    if data == "check_fj":
        if check_force_join(chat_id):
            delete_message(chat_id, msg_id)
            send_message(chat_id, render_body_text(f"{PEM['ok']} Thanks for joining! You can now use the bot."), reply_markup=main_menu(chat_id))
            
            # --- PROCESS PENDING REFERRAL ---
            if db:
                doc = db.collection('users').document(str(chat_id)).get()
                if doc.exists:
                    u_data = doc.to_dict()
                    if u_data.get("referred_by") and not u_data.get("ref_paid"):
                        inviter = u_data["referred_by"]
                        db.collection('users').document(str(chat_id)).update({"ref_paid": True})
                        reward = bot_settings.get("refer_reward", 0.2)
                        update_balance(inviter, reward)
                        db.collection('users').document(str(inviter)).update({"total_refers": firestore.Increment(1)})
                        ref_msg = (
                            f"{PEM['gift']} <b>New Referral !</b>\n"
                            f"------------------\n"
                            f"🔥 <b>You Received {reward} TK</b>\n"
                            f"------------------\n"
                            f"{PEM['user']} <b>From User ID:</b> <code>{chat_id}</code>"
                        )
                        send_message(inviter, render_body_text(ref_msg))
        else:
            answer_callback(call["id"], "❌ You haven't joined all channels yet!", show_alert=True)
        return

    if data == "back_to_get_number":
        # Return from country selection to the GET NUMBER service list.
        service_catalog = _merged_get_number_catalog()
        all_services = set(service_catalog.keys())
        c_msg = bot_settings["custom_messages"].get("get_number", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['pin']} Select Service"))
        apps_db = bot_settings.get("premium_apps", {})
        kb = []
        for srv in all_services:
            emoji_id = "5352694861990501856"
            for app_key, app_data in apps_db.items():
                if srv.upper() == app_key or srv.upper() in app_key or app_key in srv.upper():
                    if "id" in app_data:
                        emoji_id = app_data["id"]
                        break
            kb.append([{"text": f"{str(srv).upper()}", "icon_custom_emoji_id": emoji_id, "callback_data": f"g_s_{srv}", "style": "primary"}])
        service_names = {_canonical_service(x) for x in all_services if _canonical_service(x)}
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            custom_name = _canonical_service(b_copy.get("text", ""))
            if custom_name and custom_name in service_names:
                continue
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_main", "style": "danger"}])
        edit_message(chat_id, msg_id, txt, reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])
        return

    elif data == "back_to_main":
        # Return to the main menu using a new message because main_menu() is a reply keyboard.
        if chat_id in user_active_sessions:
            del user_active_sessions[chat_id]
        delete_message(chat_id, msg_id)
        send_message(chat_id, render_body_text(bot_settings["custom_messages"].get("start", {}).get("text", "")), reply_markup=main_menu(chat_id))
        answer_callback(call["id"])
        return

    elif data == "back_to_number_page":
        # Prefix/no-stock Back must restore the Number page in the CURRENT
        # message. On repeated Get Number -> Country -> no-stock attempts,
        # the saved Number page can have a different Telegram message ID.
        snap = number_page_snapshots.get(chat_id)
        if snap:
            try:
                markup = {"inline_keyboard": [[dict(btn) for btn in row] for row in snap.get("reply_markup", {}).get("inline_keyboard", [])]}
                active_prefix = str(user_prefixes.get(chat_id, "")).strip()
                for row in markup["inline_keyboard"]:
                    for btn in row:
                        if btn.get("callback_data") == "set_prefix":
                            btn["text"] = f"🔢 Prefix ON • {active_prefix}" if active_prefix else "🔢 Set Prefix"
                restore_res = edit_message(chat_id, msg_id, snap.get("text", "NEW NUMBER\n"), reply_markup=markup)
                if restore_res and restore_res.get("ok"):
                    number_page_snapshots[chat_id] = {"msg_id": msg_id, "text": snap.get("text", "NEW NUMBER\n"), "reply_markup": markup}
                    answer_callback(call["id"])
                    return
                old_msg_id = snap.get("msg_id")
                if old_msg_id and old_msg_id != msg_id:
                    old_res = edit_message(chat_id, old_msg_id, snap.get("text", "NEW NUMBER\n"), reply_markup=markup)
                    if old_res and old_res.get("ok"):
                        answer_callback(call["id"])
                        return
            except Exception:
                pass

        # Never show an error alert for Prefix/no-stock Back.
        session = user_active_sessions.get(chat_id, {})
        service = session.get("service", "")
        country = session.get("country", "")
        if service and country:
            fallback_kb = [
                [{"text": "Change Number", "callback_data": f"c_n_{service}_{country}", "style": "danger"}],
                [{"text": f"🔢 Prefix ON • {str(user_prefixes.get(chat_id, '')).strip()}", "callback_data": "set_prefix", "style": "success"}],
                [{"text": "Back", "callback_data": "back_to_country", "style": "danger"}]
            ]
            edit_message(chat_id, msg_id, "NEW NUMBER\n", reply_markup={"inline_keyboard": fallback_kb})
        answer_callback(call["id"])
        return

    elif data == "back_to_country":
        # Step back from Number -> Country selection, preserving the current service.
        session = user_active_sessions.get(chat_id, {})
        service = session.get("service")
        if not service:
            delete_message(chat_id, msg_id)
            send_message(chat_id, render_body_text(bot_settings["custom_messages"].get("start", {}).get("text", "")), reply_markup=main_menu(chat_id))
            answer_callback(call["id"])
            return

        local_cnts = set([_country_identity(b.get("country")) for b in number_batches.values() if isinstance(b, dict) and _canonical_service(b.get("service")) == _canonical_service(service) and b.get("numbers")])
        stex_cnts = set(_country_identity(x) for x in bot_settings.get("stex_services", {}).get(service, {}).keys())
        voltx_active = get_voltx_active_catalog(120)
        voltx_cnts = set()
        for _srv, _countries in voltx_active.items():
            if _canonical_service(_srv) == _canonical_service(service):
                voltx_cnts.update(_country_identity(x) for x in _countries.keys())
        all_countries = local_cnts.union(stex_cnts).union(voltx_cnts)
        c_msg = bot_settings["custom_messages"].get("select_country", {})
        raw_txt = c_msg.get("text", "📌 Select a country for {service}:").replace("{service}", service)
        kb = []
        for c in sorted(all_countries, key=lambda x: str(x).lower()):
            canonical_c = _country_identity(c)
            country_name, flag_char, _iso = _batch_country_display(service, canonical_c)
            kb.append([{"text": f"{flag_char + ' ' if flag_char else ''}{country_name}", "callback_data": f"g_c_{service}_{canonical_c or c}", "style": "success"}])
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_get_number", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text(raw_txt), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])
        return

    if data == "close_msg":
        delete_message(chat_id, msg_id)
        
    elif data == "cancel_state":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        delete_message(chat_id, msg_id)

    elif data == "cancel_2fa":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        txt = "━━━━━━━━━━━━━━━\n《 🔐 <b>2FA ONLINE</b> 》\n━━━━━━━━━━━━━━━\n<i>Generate your 2FA security code instantly using your secret key.</i>\n━━━━━━━━━━━━━━━"
        kb = [[{"text": "Generate 2fa code", "icon_custom_emoji_id": "5353022963132174959", "callback_data": "gen_2fa", "style": "success"}],
              [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data == "gen_2fa":
        user_states[chat_id] = "wait_for_2fa_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        txt = "━━━━━━━━━━━━━━━\n《 🔑 <b>ENTER 2FA KEY</b> 》\n━━━━━━━━━━━━━━━\n📝 <b>SEND YOUR 2FA SECRET KEY</b>\n━━━━━━━━━━━━━━━"
        kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_2fa", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup=kb)
        answer_callback(call["id"])

    elif data.startswith("ref_2fa_"):
        secret = data.replace("ref_2fa_", "")
        try:
            totp = pyotp.TOTP(secret)
            code = totp.now()
            remaining_time = 30 - (int(time.time()) % 30)
            
            success_txt = (
                f"━━━━━━━━━━━━━━━\n"
                f"《 🔐 <b>2FA CODE</b> 》\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🔐 <b>CODE:</b> <code>{code}</code>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🕓 <b>EXPIRES IN:</b> {remaining_time}s\n"
                f"━━━━━━━━━━━━━━━"
            )
            kb = [[{"text": f"Click to copy {code}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": code}, "style": "success"}],
                  [{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"ref_2fa_{secret}", "style": "primary"},
                   {"text": "New Code", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "gen_2fa", "style": "danger"}],
                  [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
            
            edit_message(chat_id, msg_id, render_body_text(success_txt), reply_markup={"inline_keyboard": kb})
        except:
            answer_callback(call["id"], "❌ Error refreshing code!", show_alert=True)

    elif data == "cancel_dxa_edit":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>DXA CONTROL PANEL</b>"), reply_markup=dxa_control_keyboard())
        
    elif data == "dummy_alert":
        answer_callback(call["id"], "This feature will be added later!", show_alert=True)
        
    elif data == "refresh_traffic":
        txt, markup = build_traffic_ui()
        edit_message(chat_id, msg_id, txt, reply_markup=markup)
        answer_callback(call["id"], "✅ Traffic Refreshed!", show_alert=False)

    elif data.startswith("exp_rng_"):
        srv_query = data.replace("exp_rng_", "")
        
        country_stats = {}
        current_time = time.time()
        for t in recent_traffic:
            if current_time - t.get("time", 0) <= LIVE_ACCESS_DISPLAY_WINDOW:
                if t.get("service", "").startswith(srv_query):
                    iso = t.get("iso", "XX")
                    flag = t.get("flag", "🌍")
                    if iso not in country_stats:
                        country_stats[iso] = {"count": 0, "flag": flag}
                    country_stats[iso]["count"] += 1
        
        if not country_stats:
            answer_callback(call["id"], "❌ No recent traffic found for this service!", show_alert=True)
            return
            
        kb = []
        for iso, c_data in sorted(country_stats.items(), key=lambda x: x[1]["count"], reverse=True):
            count = c_data["count"]
            c_name = iso
            emoji_id = "5780471598922337683"
            for code, fdata in bot_settings.get("premium_flags", {}).items():
                if fdata.get("iso") == iso:
                    c_name = fdata.get("name", iso)
                    if "id" in fdata: emoji_id = fdata["id"]
                    break
            
            unicode_flag = ISO_TO_FLAG.get(str(iso).upper(), "🌍")
            btn_text = f"{unicode_flag} {c_name} ({iso}) - {count} OTP"
            kb.append([{"text": btn_text, "icon_custom_emoji_id": emoji_id, "callback_data": f"exp_c_{srv_query}_{iso}", "style": "primary"}])
            
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "refresh_traffic", "style": "danger"}])
        
        app_full_name, prem_app_html = get_service_info_html(srv_query)
        edit_message(chat_id, msg_id, render_body_text(f"📊 <b>Explore Service: {prem_app_html} {app_full_name}</b>\n\nSelect a country to view available ranges:"), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data.startswith("exp_c_"):
        parts = data.split("_")
        srv_query = parts[2]
        iso_query = parts[3]
        
        nums = []
        current_time = time.time()
        for t in recent_traffic:
            if current_time - t.get("time", 0) <= LIVE_ACCESS_DISPLAY_WINDOW:
                if t.get("service", "").startswith(srv_query) and t.get("iso") == iso_query:
                    # 🌟 X রিমুভ করে ক্লিন রেঞ্জ নেওয়া হলো
                    num = t.get("real_range", t.get("number", "").replace("X", "").replace("x", "")).replace("+", "").strip()
                    if num: nums.append(num)
        
        if not nums:
            answer_callback(call["id"], "❌ No recent numbers found for this country!", show_alert=True)
            return
            
        # Use both configured StexSMS ranges and live Voltx traffic ranges.
        # This prevents Traffic -> Service -> Country from showing a stale/preprocessed range.
        known_ranges = set()
        for s_name, c_dict in bot_settings.get("stex_services", {}).items():
            for c_name, r_list in c_dict.items():
                for r in r_list:
                    known_ranges.add(str(r).replace("X", "").replace("x", ""))
        active_vx = get_voltx_active_catalog(LIVE_ACCESS_DISPLAY_WINDOW)
        for s_name, c_dict in active_vx.items():
            if str(s_name).upper() != str(srv_query).upper():
                continue
            for c_name, r_set in c_dict.items():
                for r in r_set:
                    known_ranges.add(str(r).replace("X", "").replace("x", ""))
                    
        sorted_known = sorted(list(known_ranges), key=len, reverse=True)
        
        r_counts = Counter()
        for num in nums:
            matched = False
            for r in sorted_known:
                if num.startswith(r):
                    r_counts[r] += 1
                    matched = True
                    break
            if not matched:
                if len(num) >= 7:
                    r_counts[num[:7]] += 1
                else:
                    r_counts[num] += 1
                    
        r_list = r_counts.most_common(12)
        
        kb = []
        temp_row = []
        for r, count in r_list:
            # 🌟 বাটনে এবং কলব্যাকে যাতে কোনো X না থাকে তা নিশ্চিত করা হলো
            clean_r = str(r).replace("X", "").replace("x", "")
            temp_row.append({"text": f"{clean_r} ({count})", "icon_custom_emoji_id": "5352862640592949843", "callback_data": f"tr_rng_{clean_r}|{srv_query}|{iso_query}", "style": "primary"})
            if len(temp_row) == 2:
                kb.append(temp_row)
                temp_row = []
        if temp_row:
            kb.append(temp_row)
            
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"exp_rng_{srv_query}", "style": "danger"}])
        
        app_full_name, prem_app_html = get_service_info_html(srv_query)
        prem_flag_html = get_flag_info_html(iso_query)
        
        unicode_flag = ISO_TO_FLAG.get(str(iso_query).upper(), "🌍")
        country_full_name = get_flag_info_html(iso_query, return_full_name=True)
        edit_message(chat_id, msg_id, render_body_text(f"📊 <b>Ranges for {prem_app_html} {app_full_name} - {unicode_flag} {prem_flag_html} {country_full_name} ({iso_query})</b>\n\nClick on any range to copy it."), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    # --- User Management Flows Integration ---
    elif data == "user_management":
        edit_message(chat_id, msg_id, get_user_management_text(), reply_markup=user_management_keyboard())

    elif data == "um_manage_balance":
        user_states[chat_id] = "wait_for_um_bal_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID to Manage Balance:"), reply_markup=get_cancel_kb())
        
    elif data == "um_ban_unban":
        user_states[chat_id] = "wait_for_um_ban_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID to Ban or Unban:"), reply_markup=get_cancel_kb())

    elif data == "um_user_profile":
        user_states[chat_id] = "wait_for_um_prof_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID to View Profile:"), reply_markup=get_cancel_kb())

    # --- Menu Design Integration ---
    elif data == "menu_design_list":
        edit_message(chat_id, msg_id, render_body_text(f"🎨 <b>Menu Design Editor</b>\n\nSelect a menu block to edit its Body Text and Inline Buttons. You can use Premium Emojis too!"), reply_markup=menu_design_list_keyboard())

    elif data == "md_reset_defaults":
        bot_settings["custom_messages"] = DEFAULT_CUSTOM_MESSAGES.copy()
        save_db()
        answer_callback(call["id"], "✅ Resetted to Premium Defaults!", show_alert=True)

    elif data.startswith("md_edit_"):
        answer_callback(call["id"])
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        key = data.replace("md_edit_", "")
        cm_text = render_body_text(bot_settings["custom_messages"].get(key, {}).get("text", "..."))
        try:
            edit_message(chat_id, msg_id, render_body_text(f"🎨 <b>Editing: {key.upper()}</b>\n\nPreview of current Text:\n{cm_text}"), reply_markup=menu_edit_options_keyboard(key))
        except: pass

    elif data.startswith("md_text_"):
        key = data.replace("md_text_", "")
        user_states[chat_id] = "wait_for_menu_text"
        temp_data[chat_id] = {"msg_id": msg_id, "menu_key": key}
        edit_message(chat_id, msg_id, render_body_text(f"📝 <b>Edit Body: {key.upper()}</b>\n\nSend the new text. You can use Premium Emojis directly here.\n(Use standard HTML like <b>bold</b>, <i>italic</i> for formatting)"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_edit_{key}", "style": "danger"}]]})

    elif data.startswith("md_btns_"):
        answer_callback(call["id"]) 
        if chat_id in user_states: del user_states[chat_id] 
        if chat_id in temp_data: del temp_data[chat_id]
        key = data.replace("md_btns_", "")
        try:
            edit_message(chat_id, msg_id, render_body_text(f"⚙️ <b>Edit Inline Buttons: {key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(key))
        except: pass

    elif data.startswith("md_addbtn_"):
        key = data.replace("md_addbtn_", "")
        user_states[chat_id] = "wait_for_menu_btn"
        temp_data[chat_id] = {"msg_id": msg_id, "menu_key": key}
        edit_message(chat_id, msg_id, render_body_text(f"➕ <b>Add Button: {key.upper()}</b>\n\nSend custom button in this format:\n<code>Button Text - https://link.com</code>\n\n<i>(Only normal Emojis supported here!)</i>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_btns_{key}", "style": "danger"}]]})

    elif data.startswith("md_delbtn_"):
        parts = data.split("_")
        key = parts[2]
        b_idx = int(parts[3])
        if b_idx < len(bot_settings["custom_messages"][key]["buttons"]):
            del bot_settings["custom_messages"][key]["buttons"][b_idx]
            save_db()
            answer_callback(call["id"], "✅ Button Deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text(f"⚙️ <b>Edit Inline Buttons: {key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(key))

    elif data.startswith("sel_wm_"):
        method = data.replace("sel_wm_", "")
        bal = get_user(chat_id).get('balance', 0.0)
        min_w = bot_settings['min_withdraw']
        
        if bal < min_w:
            answer_callback(call["id"], f"❌ আপনার ব্যালেন্স অপর্যাপ্ত! মিনিমাম {min_w} ৳ প্রয়োজন।", show_alert=True)
            return
            
        temp_data[chat_id] = {"method": method, "balance": bal, "msg_id": msg_id}
        user_states[chat_id] = "wait_for_withdraw_amount"
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['ok']} Method: {method}\n💰 Available Balance: {bal} ৳\n\n📝 Enter the amount you want to withdraw (Min: {min_w} ৳):"), reply_markup=get_cancel_kb())
        answer_callback(call["id"])

    elif data == "test_message_flow":
        user_states[chat_id] = "wait_for_test_service"
        temp_data[chat_id] = {}
        edit_message(chat_id, msg_id, render_body_text("🧪 <b>Test Mode</b>\n\n📝 Send the Service Name (e.g., IG):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]]})

    elif data == "manage_emojis":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['star']} <b>Premium Emoji Management</b>\n\nUpload your TXT files or manually add them below:"), reply_markup=emoji_settings_keyboard())

    elif data == "up_flags_txt":
        user_states[chat_id] = "wait_for_flag_txt"
        edit_message(chat_id, msg_id, render_body_text("📂 Please upload the <b>Flag Emojis</b> <code>.txt</code> file."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})

    elif data == "up_apps_txt":
        user_states[chat_id] = "wait_for_app_txt"
        edit_message(chat_id, msg_id, render_body_text("📂 Please upload the <b>Service Apps</b> <code>.txt</code> file."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})

    elif data == "add_single_emoji":
        user_states[chat_id] = "wait_for_emoji_extract"
        edit_message(chat_id, msg_id, render_body_text("📝 যেকোনো একটি Premium Emoji সেন্ড করুন (যেমন: 🇧🇩 বা 🚫):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})

    elif data == "dl_flags_txt":
        content = generate_emoji_txt("flags")
        if content:
            send_document(chat_id, "Flag_Emojis.txt", content)
            answer_callback(call["id"], "✅ Downloaded!")
        else:
            answer_callback(call["id"], "❌ No Flag Emojis found!", show_alert=True)

    elif data == "dl_apps_txt":
        content = generate_emoji_txt("apps")
        if content:
            send_document(chat_id, "Service_Apps.txt", content)
            answer_callback(call["id"], "✅ Downloaded!")
        else:
            answer_callback(call["id"], "❌ No App Emojis found!", show_alert=True)

    elif data == "del_all_flags":
        bot_settings["premium_flags"] = {}
        save_db()
        answer_callback(call["id"], "✅ All Premium Flags Deleted Successfully!", show_alert=True)

    elif data == "broadcast_msg":
        user_states[chat_id] = "wait_for_broadcast"
        edit_message(chat_id, msg_id, render_body_text("📢 <b>Broadcast Mode</b>\n\nSend the message you want to broadcast (Text, Photo, Video, File etc)."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]})

    elif data == "upload_num":
        user_states[chat_id] = "wait_for_txt"
        edit_message(chat_id, msg_id, render_body_text("📂 Please upload the numbers in a <b>.txt</b> file."), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]})

    elif data == "delete_files":
        kb = []
        for b_id, b_data in number_batches.items():
            kb.append([{"text": f"{b_data['filename']} ({len(b_data['numbers'])})", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"del_b_{b_id}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "primary"}])
        txt = "🗑 Select a file to delete:" if len(kb) > 1 else f"{PEM['no']} No files found."
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_b_"):
        b_id = data.split("del_b_")[1]
        if b_id in number_batches:
            del number_batches[b_id]
            save_db()
            answer_callback(call["id"], "✅ File deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "delete_files", "id": call["id"]})

    elif data == "show_used":
        kb = {"inline_keyboard": [[{"text": "Download TXT", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_used", "style": "primary"}], [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['ok']} <b>Total Used Numbers:</b> {len(used_numbers_list)}"), reply_markup=kb)

    elif data == "show_unused":
        unused_count = sum(len(b["numbers"]) for b in number_batches.values())
        kb = {"inline_keyboard": [[{"text": "Download TXT", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_unused", "style": "primary"}], [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['rocket']} <b>Total Unused Numbers:</b> {unused_count}"), reply_markup=kb)

    elif data == "dl_used":
        if not used_numbers_list:
            answer_callback(call["id"], "❌ No used numbers found!", show_alert=True)
            return
        content = "\n".join(used_numbers_list).encode('utf-8')
        send_document(chat_id, "used_numbers.txt", content)
        answer_callback(call["id"])

    elif data == "dl_unused":
        unused_list = [n["num"] for b in number_batches.values() for n in b["numbers"]]
        if not unused_list:
            answer_callback(call["id"], "❌ No unused numbers found!", show_alert=True)
            return
        content = "\n".join(unused_list).encode('utf-8')
        send_document(chat_id, "unused_numbers.txt", content)
        answer_callback(call["id"])

    elif data == "lb_main":
        txt = f"━━━━━━━━━━━━━━━\n《 {PEM['admin']} <b>LEADER BOARD MENU</b> 》\n━━━━━━━━━━━━━━━\n<i>Select a category to view the top performers or history.</i>\n━━━━━━━━━━━━━━━"
        kb = [
            [{"text": "Top Referrers", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "lb_top_refs", "style": "primary"}],
            [{"text": "Top OTP Receivers", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "lb_top_otps", "style": "primary"}],
            [{"text": "Withdrawal History", "icon_custom_emoji_id": "5348469219761626211", "callback_data": "lb_w_history", "style": "success"}],
            [{"text": "Back to Admin", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
        ]
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("lb_"):
        sub = data.replace("lb_", "")
        edit_message(chat_id, msg_id, render_body_text("⌛ <i>Fetching Data...</i>"))
        
        num_map = {"1": "1️⃣", "2": "2️⃣", "3": "3️⃣", "4": "4️⃣", "5": "5️⃣", "6": "6️⃣", "7": "7️⃣", "8": "8️⃣", "9": "9️⃣", "0": "0️⃣"}
        def get_p_num(n): return "".join([num_map.get(c, c) for c in str(n)])
        
        try:
            if sub == "top_refs":
                title, field, limit, icon = "TOP 5 REFERRERS", "total_refers", 5, PEM.get('user', '👥')
                users = get_all_users_for_admin()
                users.sort(key=lambda u: int(float(u.get(field, 0) or 0)), reverse=True)
                res_txt = ""
                ranked = [u for u in users if int(float(u.get(field, 0) or 0)) > 0][:limit]
                for count, d in enumerate(ranked, 1):
                    uid = str(d.get("user_id") or "Unknown")
                    name = str(d.get("full_name") or d.get("name") or "Unknown User")
                    username = str(d.get("username") or "").strip().lstrip("@")
                    username_text = f"@{username}" if username else "Not Set"
                    p = "└" if count == len(ranked) else "├"
                    res_txt += (
                        f"{p} {get_p_num(count)} <b>{html.escape(name)}</b>\n"
                        f"   👤 Username: {html.escape(username_text)}\n"
                        f"   🆔 User ID: <code>{html.escape(uid)}</code>\n"
                        f"   👥 Referrals: <b>{int(float(d.get(field, 0) or 0))}</b>\n"
                    )
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "top_otps":
                title, field, limit, icon = "TOP 5 OTP RECEIVERS", "total_otps", 5, PEM.get('msg', '📩')
                users = get_all_users_for_admin()
                users.sort(key=lambda u: int(float(u.get(field, 0) or 0)), reverse=True)
                res_txt = ""
                ranked = [u for u in users if int(float(u.get(field, 0) or 0)) > 0][:limit]
                for count, d in enumerate(ranked, 1):
                    uid = str(d.get("user_id") or "Unknown")
                    name = str(d.get("full_name") or d.get("name") or "Unknown User")
                    username = str(d.get("username") or "").strip().lstrip("@")
                    username_text = f"@{username}" if username else "Not Set"
                    otp_number = str(d.get("last_otp_number") or "Not Available")
                    p = "└" if count == len(ranked) else "├"
                    res_txt += (
                        f"{p} {get_p_num(count)} <b>{html.escape(name)}</b>\n"
                        f"   👤 Username: {html.escape(username_text)}\n"
                        f"   🆔 User ID: <code>{html.escape(uid)}</code>\n"
                        f"   📱 OTP Number: <code>{html.escape(otp_number)}</code>\n"
                        f"   🔐 Received OTP: <b>{int(float(d.get(field, 0) or 0))}</b>\n"
                    )
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "w_history" or sub.startswith("wh_p_") or sub == "wh_txt":
                # Withdrawal History: 10 records per page + admin-only approve/reject + full TXT export.
                try:
                    if sub == "wh_txt":
                        page = 1
                    elif sub.startswith("wh_p_"):
                        try:
                            page = max(1, int(sub.split("_p_", 1)[1]))
                        except Exception:
                            page = 1
                    else:
                        page = 1

                    all_rows = []
                    if db:
                        try:
                            ws = db.collection('withdrawals').order_by('timestamp', direction="DESCENDING").stream()
                            for w in ws:
                                d = w.to_dict()
                                d["req_id"] = w.id
                                all_rows.append(d)
                        except Exception as e:
                            print(f"[WITHDRAWAL] History Firestore read error: {e}")

                    # Local persistence fallback / merge.
                    local_rows = []
                    try:
                        if os.path.exists(WITHDRAWALS_LOCAL_FILE):
                            with open(WITHDRAWALS_LOCAL_FILE, "r", encoding="utf-8") as f:
                                local_map = json.load(f)
                            for rid, item in local_map.items():
                                d = dict(item)
                                d["req_id"] = rid
                                local_rows.append(d)
                    except Exception as e:
                        print(f"[WITHDRAWAL] Local history read error: {e}")

                    # Merge by request ID so local-only records are not lost and duplicates are removed.
                    merged = {}
                    for d in all_rows + local_rows:
                        rid = str(d.get("req_id") or d.get("id") or "")
                        if rid:
                            if rid not in merged:
                                merged[rid] = d
                            else:
                                # Prefer the record that contains more complete user/request details.
                                old = merged[rid]
                                for key in ("user_id", "full_name", "amount", "method", "number", "status", "created_at", "processed_at"):
                                    if (not old.get(key)) and d.get(key):
                                        old[key] = d[key]
                    rows = list(merged.values())
                    rows.sort(key=lambda x: str(x.get("created_at") or x.get("timestamp") or ""), reverse=True)

                    # TXT export contains the complete history, not only the current 10-record page.
                    if sub == "wh_txt":
                        if not rows:
                            answer_callback(call["id"], "❌ No withdrawal history found!", show_alert=True)
                            return
                        txt_lines = ["A H R VIP BOT - WITHDRAWAL HISTORY", "=" * 55, ""]
                        for idx, d in enumerate(rows, 1):
                            txt_lines.extend([
                                f"#{idx}",
                                f"USER: {d.get('full_name') or d.get('name') or 'User'}",
                                f"USER ID: {d.get('user_id', 'Unknown')}",
                                f"AMOUNT: {d.get('amount', 0)} TK",
                                f"METHOD: {d.get('method', 'N/A')}",
                                f"NUMBER: {d.get('number', 'N/A')}",
                                f"REQ ID: {d.get('req_id') or d.get('id') or 'N/A'}",
                                f"STATUS: {str(d.get('status', 'pending')).upper()}",
                                f"TIME: {d.get('created_at') or d.get('timestamp') or 'N/A'}",
                                f"PROCESSED AT: {d.get('processed_at') or 'N/A'}",
                                "-" * 55,
                            ])
                        content = "\n".join(txt_lines).encode("utf-8")
                        send_document(chat_id, "withdrawal_history.txt", content)
                        answer_callback(call["id"], "✅ Complete withdrawal history TXT sent!")
                        return

                    limit = 10
                    total = len(rows)
                    max_page = max(1, (total + limit - 1) // limit)
                    page = min(page, max_page)
                    start_idx = (page - 1) * limit
                    page_rows = rows[start_idx:start_idx + limit]

                    title, icon = "WITHDRAWAL HISTORY", PEM.get('money', '💸')
                    res_txt = ""
                    history_kb = []
                    for local_idx, d in enumerate(page_rows, start_idx + 1):
                        status = str(d.get('status', 'pending')).lower()
                        stat_icon = PEM.get('ok','✅') if status in ["approved", "success"] else PEM.get('no','❌') if status == "rejected" else "⏳"
                        uid = str(d.get('user_id', 'Unknown'))
                        full_name = str(d.get('full_name') or d.get('name') or 'User')
                        amount = d.get('amount', 0)
                        method = str(d.get('method', 'N/A'))
                        number = str(d.get('number', 'N/A'))
                        req_id = str(d.get('req_id') or d.get('id') or 'N/A')
                        created = str(d.get('created_at') or d.get('timestamp') or '')
                        res_txt += (
                            f"<b>{get_p_num(local_idx)}. {html.escape(full_name)}</b> {stat_icon} <code>{html.escape(status.upper())}</code>\n"
                            f"🆔 <b>USER ID:</b> <code>{html.escape(uid)}</code>\n"
                            f"💳 <b>AMOUNT:</b> <b>{html.escape(str(amount))}৳</b>\n"
                            f"🏦 <b>METHOD:</b> {html.escape(method)}\n"
                            f"📱 <b>NUMBER:</b> <code>{html.escape(number)}</code>\n"
                            f"🧾 <b>REQ ID:</b> <code>{html.escape(req_id)}</code>\n"
                            + (f"🕒 <b>TIME:</b> <code>{html.escape(created)}</code>\n" if created else "")
                            + "━━━━━━━━━━━━━━━\n"
                        )
                        if status == "pending" and req_id != "N/A":
                            history_kb.append([
                                {"text": f"✅ APPROVE #{local_idx}", "icon_custom_emoji_id": "5352694861990501856", "callback_data": f"wapp_{req_id}", "style": "success"},
                                {"text": f"❌ REJECT #{local_idx}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"wrej_{req_id}", "style": "danger"}
                            ])

                    if not res_txt:
                        res_txt = "└ <i>No withdrawal history found.</i>\n"

                    nav_row = []
                    if page > 1:
                        nav_row.append({"text": "⬅️ Previous", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"lb_wh_p_{page - 1}", "style": "primary"})
                    if page < max_page:
                        nav_row.append({"text": "Next ➡️", "icon_custom_emoji_id": "5420145051336485498", "callback_data": f"lb_wh_p_{page + 1}", "style": "primary"})
                    if nav_row:
                        history_kb.append(nav_row)

                    history_kb.append([
                        {"text": "📥 Download All TXT", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "lb_wh_txt", "style": "success"}
                    ])
                    history_kb.append([
                        {"text": f"📄 Page {page}/{max_page} • Total {total}", "callback_data": "ignore", "style": "primary"}
                    ])
                    history_kb.append([
                        {"text": "🔄 Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"lb_wh_p_{page}", "style": "success"},
                        {"text": "↩️ Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}
                    ])

                    final_msg = f"━━━━━━━━━━━━━━━\n{icon} <b>{title}</b>\n━━━━━━━━━━━━━━━\n<b>Showing {start_idx + 1 if total else 0}-{min(start_idx + limit, total)} of {total}</b>\n━━━━━━━━━━━━━━━\n{res_txt}━━━━━━━━━━━━━━━"
                    edit_message(chat_id, msg_id, render_body_text(final_msg), reply_markup={"inline_keyboard": history_kb})
                    answer_callback(call["id"])
                    return
                except Exception as e:
                    print(f"[WITHDRAWAL] History pagination error: {e}")
                    edit_message(chat_id, msg_id, render_body_text(f"❌ <b>Withdrawal History Error:</b> {html.escape(str(e))}"), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]})
                    answer_callback(call["id"], "❌ Could not load history", show_alert=True)
                    return

            final_msg = f"━━━━━━━━━━━━━━━\n{icon} <b>{title}</b>\n━━━━━━━━━━━━━━━\n{res_txt}━━━━━━━━━━━━━━━"
            kb = [[{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": data, "style": "success"}, {"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]
            edit_message(chat_id, msg_id, render_body_text(final_msg), reply_markup={"inline_keyboard": kb})

        except Exception as e:
            edit_message(chat_id, msg_id, render_body_text(f"❌ Error: {e}"), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]})

    elif data == "lb_main":
        txt = f"━━━━━━━━━━━━━━━\n《 {PEM['admin']} <b>LEADER BOARD MENU</b> 》\n━━━━━━━━━━━━━━━\n<i>Select a category to view the top performers or history.</i>\n━━━━━━━━━━━━━━━"
        kb = [
            [{"text": "Top Referrers", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "lb_top_refs", "style": "primary"}],
            [{"text": "Top OTP Receivers", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "lb_top_otps", "style": "primary"}],
            [{"text": "Withdrawal History", "icon_custom_emoji_id": "5348469219761626211", "callback_data": "lb_w_history", "style": "success"}],
            [{"text": "Back to Admin", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
        ]
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("lb_"):
        sub = data.replace("lb_", "")
        edit_message(chat_id, msg_id, render_body_text("⌛ <i>Fetching Data...</i>"))
        
        num_map = {"1": "1️⃣", "2": "2️⃣", "3": "3️⃣", "4": "4️⃣", "5": "5️⃣", "6": "6️⃣", "7": "7️⃣", "8": "8️⃣", "9": "9️⃣", "0": "0️⃣"}
        def get_p_num(n): return "".join([num_map.get(c, c) for c in str(n)])
        
        try:
            if sub == "top_refs":
                title, field, limit, icon = "TOP 5 REFERRERS", "total_refers", 5, PEM.get('user', '👥')
                users = db.collection('users').order_by(field, direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for u in users:
                    d = u.to_dict()
                    if d.get(field, 0) > 0:
                        p = "└" if count == limit else "├"
                        res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={u.id}'>{u.id}</a> ➔ <b>{d.get(field,0)}</b>\n"
                        count += 1
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "top_otps":
                title, field, limit, icon = "TOP 5 OTP RECEIVERS", "total_otps", 5, PEM.get('msg', '📩')
                users = db.collection('users').order_by(field, direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for u in users:
                    d = u.to_dict()
                    if d.get(field, 0) > 0:
                        p = "└" if count == limit else "├"
                        res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={u.id}'>{u.id}</a> ➔ <b>{d.get(field,0)}</b>\n"
                        count += 1
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "w_history":
                title, limit, icon = "LAST 10 WITHDRAWALS", 10, PEM.get('money', '💸')
                ws = db.collection('withdrawals').order_by('timestamp', direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for w in ws:
                    d = w.to_dict()
                    s = str(d.get('status','Pending')).lower()
                    stat_icon = PEM.get('ok','✅') if s in ["approved","success"] else PEM.get('no','❌') if s=="rejected" else "⏳"
                    uid = d.get('user_id','User')
                    p = "└" if count == limit else "├"
                    res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={uid}'>{uid}</a> ➔ <b>{d.get('amount',0)}৳</b> {stat_icon}\n"
                    count += 1
                if not res_txt: res_txt = "└ <i>No history found.</i>\n"

            final_msg = f"━━━━━━━━━━━━━━━\n{icon} <b>{title}</b>\n━━━━━━━━━━━━━━━\n{res_txt}━━━━━━━━━━━━━━━"
            kb = [[{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": data, "style": "success"}, {"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]
            edit_message(chat_id, msg_id, render_body_text(final_msg), reply_markup={"inline_keyboard": kb})

        except Exception as e:
            edit_message(chat_id, msg_id, render_body_text(f"❌ Error: {e}"), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]})

    elif data.startswith("user_list_"):
        if not is_admin(chat_id):
            answer_callback(call["id"], "🚫 Admin only!", show_alert=True)
            return
        try:
            page = int(data.rsplit("_", 1)[1])
        except Exception:
            page = 0
        text, page, max_page, total = get_user_list_page(page)
        edit_message(chat_id, msg_id, text, reply_markup=user_list_keyboard(page, max_page))

    elif data == "download_all_users_txt":
        if not is_admin(chat_id):
            answer_callback(call["id"], "🚫 Admin only!", show_alert=True)
            return
        try:
            content = build_all_users_txt()
            send_document(chat_id, "all_users_list.txt", content)
            answer_callback(call["id"], "✅ User list file sent successfully!")
        except Exception:
            answer_callback(call["id"], "❌ Failed to generate user list file!", show_alert=True)

    elif data == "back_to_admin":
        if chat_id in user_states: del user_states[chat_id]
        edit_message(chat_id, msg_id, get_admin_text(), reply_markup=admin_panel_keyboard())
        
    elif data == "system_settings":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['gear']} <b>System Settings</b>\nManage advanced bot configurations below:"), reply_markup=system_settings_keyboard())

    elif data == "custom_otp":
        if not is_admin(chat_id):
            answer_callback(call["id"], "🚫 Admin only!", show_alert=True)
            return
        edit_message(chat_id, msg_id, custom_otp_text(), reply_markup=custom_otp_keyboard())

    elif data == "cotp_add_service":
        user_states[chat_id] = "wait_for_cotp_service"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("🧩 <b>ADD SERVICE</b>\nSend one or more service names separated by commas.\nExample: <code>Facebook, WhatsApp, TikTok, Telegram</code>"), reply_markup={"inline_keyboard":[[{"text":"Cancel","callback_data":"custom_otp","style":"danger"}]]})

    elif data == "cotp_services":
        custom_otp_services_view(chat_id, msg_id)

    elif data.startswith("cotp_service_"):
        idx = int(data.rsplit("_", 1)[1])
        custom_otp_service_view(chat_id, msg_id, idx)

    elif data.startswith("cotp_set_digit_"):
        idx = int(data.rsplit("_", 1)[1])
        services, _ = custom_otp_normalize_services()
        if 0 <= idx < len(services):
            user_states[chat_id] = "wait_for_cotp_digit"
            temp_data[chat_id] = {"msg_id": msg_id, "service_idx": idx}
            edit_message(chat_id, msg_id, render_body_text(f"✏️ <b>{services[idx]} — SET CODE DIGIT</b>\n\nSend only the number of digits.\nExample: <code>6</code>\n\n1–12 digits are supported."), reply_markup={"inline_keyboard":[[{"text":"Cancel","callback_data":f"cotp_service_{idx}","style":"danger"}]]})
        else:
            custom_otp_services_view(chat_id, msg_id)

    elif data == "cotp_numbers":
        custom_otp_numbers_view(chat_id, msg_id)

    elif data == "cotp_add_number":
        user_states[chat_id] = "wait_for_cotp_number"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text(
            "📝 <b>ADD NUMBER CONFIG</b>\n\n"
            "এই exact format-এ দিন:\n"
            "<code>NUMBER-SERVICE-SECONDSs</code>\n\n"
            "📌 <b>Copy & paste examples:</b>\n"
            "<code>263772266797-Facebook-4s</code>\n"
            "<code>417262252552-Telegram-8s</code>\n"
            "<code>528228282672-WhatsApp-10s</code>\n"
            "<code>275234522681-Imo-1s</code>\n\n"
            "⚠️ <b>Quantity/otp লিখবেন না।</b>\n"
            "⚠️ <b>+ চিহ্ন না দিলেই হবে।</b>\n"
            "একাধিক number হলে প্রতিটি আলাদা লাইনে দিন।"
        ), reply_markup={"inline_keyboard":[
            [{"text":"⬅️ Back to Numbers","callback_data":"cotp_numbers","style":"primary"}],
            [{"text":"Cancel","callback_data":"custom_otp","style":"danger"}]
        ]})

    elif data.startswith("cotp_del_service_"):
        idx = int(data.rsplit("_", 1)[1])
        services = bot_settings.get("custom_otp_services", [])
        if 0 <= idx < len(services):
            srv = str(services[idx])
            del services[idx]
            digits_map = bot_settings.get("custom_otp_service_digits", {})
            for k in list(digits_map.keys()):
                if str(k).lower() == srv.lower():
                    del digits_map[k]
            bot_settings["custom_otp_configs"] = [
                c for c in bot_settings.get("custom_otp_configs", [])
                if str(c.get("service", "")).lower() != srv.lower()
            ]
            save_db()
        answer_callback(call["id"], f"Service deleted: {srv}", show_alert=True)
        custom_otp_services_view(chat_id, msg_id)

    elif data.startswith("cotp_del_number_"):
        idx = int(data.rsplit("_", 1)[1])
        configs = bot_settings.get("custom_otp_configs", []) or []
        if 0 <= idx < len(configs):
            del configs[idx]
            save_db()
            answer_callback(call["id"], "Number deleted", show_alert=True)
        custom_otp_numbers_view(chat_id, msg_id)

    elif data.startswith("cotp_del_"):
        idx = int(data.rsplit("_", 1)[1])
        configs = bot_settings.get("custom_otp_configs", [])
        if 0 <= idx < len(configs):
            del configs[idx]
            save_db()
        edit_message(chat_id, msg_id, custom_otp_text(), reply_markup=custom_otp_keyboard())

    elif data == "cotp_start":
        ok, message = custom_otp_start()
        answer_callback(call["id"], message, show_alert=True)
        edit_message(chat_id, msg_id, custom_otp_text(), reply_markup=custom_otp_keyboard())

    elif data == "cotp_stop":
        message = custom_otp_stop()
        answer_callback(call["id"], message, show_alert=True)
        edit_message(chat_id, msg_id, custom_otp_text(), reply_markup=custom_otp_keyboard())

    elif data == "stex_control":
        edit_message(chat_id, msg_id, render_body_text(f"🌐 <b>StexSMS Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('stex_keys', []))}\nManage your StexSMS API Keys below:"), reply_markup=stex_control_keyboard())

    elif data == "add_stex_key":
        user_states[chat_id] = "wait_for_add_stex_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new StexSMS API Key (e.g. nxa_...):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "danger"}]]})

    elif data == "view_stex_keys":
        kb = []
        for idx, key in enumerate(bot_settings.get("stex_keys", [])):
            safe_name = key[:10] + "..." if len(key)>10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_nxa_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select StexSMS Key to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_nxa_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("stex_keys", [])):
            del bot_settings["stex_keys"][idx]
            save_db()
            answer_callback(call["id"], "✅ StexSMS Key Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "view_stex_keys", "id": call["id"]})

    elif data == "stex_search_country":
        kb = []
        for idx, c in enumerate(bot_settings.get("search_countries", [])):
            kb.append([{"text": f"Delete {c}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_sc_{idx}", "style": "danger"}])
        kb.append([{"text": "Add Country Code", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_search_country", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🌍 <b>Allowed Search Countries:</b>\nOnly these country codes will be allowed in Search Number."), reply_markup={"inline_keyboard": kb})

    elif data == "add_search_country":
        user_states[chat_id] = "wait_for_add_sc"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Country Code (e.g. 880 or 92):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_search_country", "style": "danger"}]]})

    elif data.startswith("del_sc_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("search_countries", [])):
            del bot_settings["search_countries"][idx]
            save_db()
            answer_callback(call["id"], "✅ Country Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "stex_search_country", "id": call["id"]})

    elif data == "manage_stex_srv":
        kb = []
        srvs = bot_settings.get("stex_services", {})
        apps_db = bot_settings.get("premium_apps", {})
        for srv in srvs:
            emoji_id = "5257969839313526622"
            for app_key, app_data in apps_db.items():
                if srv.upper() == app_key or srv.upper() in app_key or app_key in srv.upper():
                    if "id" in app_data:
                        emoji_id = app_data["id"]
                        break
            kb.append([{"text": f"{srv}", "icon_custom_emoji_id": emoji_id, "callback_data": f"nx_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Add New Service", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "nx_add_srv", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("📦 <b>StexSMS Services Manager</b>\nManage your API-based dynamic services below:"), reply_markup={"inline_keyboard": kb})

    elif data == "nx_add_srv":
        user_states[chat_id] = "wait_nx_srv_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Enter Service Name (e.g. TELEGRAM):"), reply_markup=get_cancel_kb())

    elif data.startswith("nx_srv_"):
        srv = data.replace("nx_srv_", "")
        kb = []
        countries = bot_settings["stex_services"].get(srv, {})
        flags_db = bot_settings.get("premium_flags", {})
        for c in countries:
            emoji_id = "5780471598922337683"
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper()
                name = flag_data.get("name", "").upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in flag_data:
                        emoji_id = flag_data["id"]
                        break
            kb.append([{"text": f"{c} ({len(countries[c])} Ranges)", "icon_custom_emoji_id": emoji_id, "callback_data": f"nx_cnt_{srv}_{c}", "style": "primary"}])
        kb.append([{"text": "Add Country", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"nx_add_cnt_{srv}", "style": "success"}])
        kb.append([{"text": "Delete Service", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"nx_del_srv_{srv}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_stex_srv", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📂 <b>Service: {srv}</b>\nManage countries for this service:"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("nx_add_cnt_"):
        srv = data.replace("nx_add_cnt_", "")
        user_states[chat_id] = "wait_nx_cnt_name"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv}
        edit_message(chat_id, msg_id, render_body_text(f"🌍 Enter Country Name for <b>{srv}</b> (e.g. BD, INDIA):"), reply_markup=get_cancel_kb())

    elif data.startswith("nx_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        ranges = bot_settings["stex_services"][srv].get(cnt, [])
        
        kb = []
        row = []
        for r in ranges:
            row.append({"text": f"Delete {r}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"nx_dr_{srv}_{cnt}_{r}", "style": "danger"})
            if len(row) == 2:
                kb.append(row)
                row = []
        if row: kb.append(row)
        
        kb.append([{"text": "Add Range", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"nx_addr_{srv}_{cnt}", "style": "success"}])
        kb.append([{"text": "Delete Entire Country", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"nx_del_cnt_{srv}_{cnt}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"nx_srv_{srv}", "style": "primary"}])
        
        txt = f"📍 <b>Service: {srv} | Country: {cnt}</b>\n\n<b>Total Ranges:</b> {len(ranges)}\n<i>Click on a range below to delete it, or add a new one.</i>"
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("nx_addr_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        user_states[chat_id] = "wait_nx_addr"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        edit_message(chat_id, msg_id, render_body_text(f"📝 Send the new Range for <b>{cnt}</b> (e.g. 88017):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"nx_cnt_{srv}_{cnt}", "style": "danger"}]]})

    elif data.startswith("nx_dr_"):
        parts = data.split("_")
        srv, cnt, rng = parts[2], parts[3], parts[4]
        if rng in bot_settings["stex_services"].get(srv, {}).get(cnt, []):
            bot_settings["stex_services"][srv][cnt].remove(rng)
            save_db()
            answer_callback(call["id"], f"✅ Range {rng} deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"nx_cnt_{srv}_{cnt}", "id": call["id"]})

    elif data.startswith("nx_del_srv_"):
        srv = data.replace("nx_del_srv_", "")
        if srv in bot_settings["stex_services"]: del bot_settings["stex_services"][srv]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_stex_srv", "id": call["id"]})

    elif data.startswith("nx_del_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[3], parts[4]
        if cnt in bot_settings["stex_services"].get(srv, {}): del bot_settings["stex_services"][srv][cnt]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"nx_srv_{srv}", "id": call["id"]})

    elif data == "voltx_control":
        edit_message(chat_id, msg_id, render_body_text(f"⚡ <b>Voltx Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('voltx_keys', []))}\nManage your Voltx API Keys below:"), reply_markup=voltx_control_keyboard())

    elif data == "add_voltx_key":
        user_states[chat_id] = "wait_for_add_voltx_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new Voltx API Key:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "danger"}]]})

    elif data == "view_voltx_keys":
        kb = []
        for idx, key in enumerate(bot_settings.get("voltx_keys", [])):
            safe_name = key[:10] + "..." if len(key)>10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_vtx_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select Voltx Key to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_vtx_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("voltx_keys", [])):
            del bot_settings["voltx_keys"][idx]
            save_db()
            answer_callback(call["id"], "✅ Voltx Key Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "view_voltx_keys", "id": call["id"]})

    elif data == "voltx_search_country":
        kb = []
        for idx, c in enumerate(bot_settings.get("voltx_search_countries", [])):
            kb.append([{"text": f"Delete {c}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_vsc_{idx}", "style": "danger"}])
        kb.append([{"text": "Add Country Code", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_voltx_search_country", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🌍 <b>Voltx Allowed Ranges:</b>\nOnly these ranges/codes will be allowed in Voltx Search Number."), reply_markup={"inline_keyboard": kb})

    elif data == "add_voltx_search_country":
        user_states[chat_id] = "wait_for_add_vsc"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Voltx Range Code (e.g. 26134):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_search_country", "style": "danger"}]]})

    elif data.startswith("del_vsc_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("voltx_search_countries", [])):
            del bot_settings["voltx_search_countries"][idx]
            save_db()
            answer_callback(call["id"], "✅ Voltx Range Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "voltx_search_country", "id": call["id"]})

    elif data == "manage_voltx_srv":
        kb = []
        srvs = bot_settings.get("voltx_services", {})
        apps_db = bot_settings.get("premium_apps", {})
        for srv in srvs:
            emoji_id = "5257969839313526622"
            for app_key, app_data in apps_db.items():
                if srv.upper() == app_key or srv.upper() in app_key or app_key in srv.upper():
                    if "id" in app_data: emoji_id = app_data["id"]; break
            kb.append([{"text": f"{srv}", "icon_custom_emoji_id": emoji_id, "callback_data": f"vx_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Add New Service", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "vx_add_srv", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("⚡ <b>Voltx Services Manager</b>\nManage your API-based dynamic services below:"), reply_markup={"inline_keyboard": kb})

    elif data == "vx_add_srv":
        user_states[chat_id] = "wait_vx_srv_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Enter Service Name (e.g. TELEGRAM):"), reply_markup=get_cancel_kb())

    elif data.startswith("vx_srv_"):
        srv = data.replace("vx_srv_", "")
        kb = []
        countries = bot_settings["voltx_services"].get(srv, {})
        flags_db = bot_settings.get("premium_flags", {})
        for c in countries:
            emoji_id = "5780471598922337683"
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper()
                name = flag_data.get("name", "").upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in flag_data: emoji_id = flag_data["id"]; break
            kb.append([{"text": f"{c} ({len(countries[c])} Ranges)", "icon_custom_emoji_id": emoji_id, "callback_data": f"vx_cnt_{srv}_{c}", "style": "primary"}])
        kb.append([{"text": "Add Country", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"vx_add_cnt_{srv}", "style": "success"}])
        kb.append([{"text": "Delete Service", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"vx_del_srv_{srv}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_voltx_srv", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📂 <b>Service: {srv}</b>\nManage countries for this service:"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("vx_add_cnt_"):
        srv = data.replace("vx_add_cnt_", "")
        user_states[chat_id] = "wait_vx_cnt_name"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv}
        edit_message(chat_id, msg_id, render_body_text(f"🌍 Enter Country Name for <b>{srv}</b> (e.g. BD, INDIA):"), reply_markup=get_cancel_kb())

    elif data.startswith("vx_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        ranges = bot_settings["voltx_services"][srv].get(cnt, [])
        kb = []
        row = []
        for r in ranges:
            row.append({"text": f"Delete {r}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"vx_dr_{srv}_{cnt}_{r}", "style": "danger"})
            if len(row) == 2:
                kb.append(row)
                row = []
        if row: kb.append(row)
        kb.append([{"text": "Add Range", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"vx_addr_{srv}_{cnt}", "style": "success"}])
        kb.append([{"text": "Delete Entire Country", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"vx_del_cnt_{srv}_{cnt}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"vx_srv_{srv}", "style": "primary"}])
        txt = f"📍 <b>Service: {srv} | Country: {cnt}</b>\n\n<b>Total Ranges:</b> {len(ranges)}\n<i>Click on a range below to delete it, or add a new one.</i>"
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("vx_addr_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        user_states[chat_id] = "wait_vx_addr"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        edit_message(chat_id, msg_id, render_body_text(f"📝 Send the new Range for <b>{cnt}</b> (e.g. 26134):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"vx_cnt_{srv}_{cnt}", "style": "danger"}]]})

    elif data.startswith("vx_dr_"):
        parts = data.split("_")
        srv, cnt, rng = parts[2], parts[3], parts[4]
        if rng in bot_settings["voltx_services"].get(srv, {}).get(cnt, []):
            bot_settings["voltx_services"][srv][cnt].remove(rng)
            save_db()
            answer_callback(call["id"], f"✅ Range {rng} deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"vx_cnt_{srv}_{cnt}", "id": call["id"]})

    elif data.startswith("vx_del_srv_"):
        srv = data.replace("vx_del_srv_", "")
        if srv in bot_settings["voltx_services"]: del bot_settings["voltx_services"][srv]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_voltx_srv", "id": call["id"]})

    elif data.startswith("vx_del_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[3], parts[4]
        if cnt in bot_settings["voltx_services"].get(srv, {}): del bot_settings["voltx_services"][srv][cnt]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"vx_srv_{srv}", "id": call["id"]})

    elif data == "manage_fj":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN SYSTEM</b>\nManage channels below:"), reply_markup=fj_settings_keyboard())

    elif data == "toggle_fj":
        bot_settings["fj_on"] = not bot_settings["fj_on"]
        save_db()
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN SYSTEM</b>\nManage channels below:"), reply_markup=fj_settings_keyboard())

    elif data == "add_fj":
        user_states[chat_id] = "wait_for_add_fj"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send Channel Username or Invite Link:\n<i>(Note: For private channels, use the numeric ID like -100...)</i>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_fj", "style": "danger"}]]})

    elif data.startswith("del_fj_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fj_channels"]):
            del bot_settings["fj_channels"][idx]
            save_db()
            answer_callback(call["id"], "✅ Channel deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN SYSTEM</b>\nManage channels below:"), reply_markup=fj_settings_keyboard())

    elif data == "manage_admins":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['user']} <b>ADMIN MANAGEMENT</b>\nManage your bot admins below:"), reply_markup=admin_settings_keyboard())

    elif data == "add_adm":
        user_states[chat_id] = "wait_for_add_adm"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID of the new Admin:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_admins", "style": "danger"}]]})

    elif data.startswith("del_adm_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["admins"]):
            del bot_settings["admins"][idx]
            save_db()
            answer_callback(call["id"], "✅ Admin deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text(f"{PEM['user']} <b>ADMIN MANAGEMENT</b>\nManage your bot admins below:"), reply_markup=admin_settings_keyboard())

    elif data == "manage_otp_groups":
        edit_message(chat_id, msg_id, render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())

    elif data == "add_fw":
        user_states[chat_id] = "wait_for_add_fw_id"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Group ID/Username to forward messages to:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "danger"}]]})

    elif data.startswith("manage_fw_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            grp_id = bot_settings["fw_groups"][idx]["chat_id"]
            edit_message(chat_id, msg_id, render_body_text(f"🛡 <b>Manage Group:</b> {grp_id}"), reply_markup=specific_fw_group_keyboard(idx))

    elif data.startswith("add_fwbtn_"):
        idx = int(data.split("_")[2])
        user_states[chat_id] = "wait_for_add_fw_btn"
        temp_data[chat_id] = {"msg_id": msg_id, "fw_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send Custom Inline Button format:\n<code>Button Text - https://link.com</code>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"manage_fw_{idx}", "style": "danger"}]]})

    elif data.startswith("del_fwbtn_"):
        parts = data.split("_")
        idx, b_idx = int(parts[2]), int(parts[3])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            if 0 <= b_idx < len(bot_settings["fw_groups"][idx]["buttons"]):
                del bot_settings["fw_groups"][idx]["buttons"][b_idx]
                save_db()
                answer_callback(call["id"], "✅ Button deleted!", show_alert=True)
                edit_message(chat_id, msg_id, render_body_text(f"🛡 <b>Manage Group:</b> {bot_settings['fw_groups'][idx]['chat_id']}"), reply_markup=specific_fw_group_keyboard(idx))

    elif data.startswith("del_fw_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            del bot_settings["fw_groups"][idx]
            save_db()
            answer_callback(call["id"], "✅ Group deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())

    elif data == "set_otp_channel_link":
        user_states[chat_id] = "wait_for_otp_channel_link"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Channel Link:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "danger"}]]})

    elif data == "otp_add_button":
        user_states[chat_id] = "wait_for_otp_btn_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("➕ <b>Add New Button</b>\n\nFirst, send the <b>button name</b> you want to display:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "danger"}]]})

    elif data == "otp_button_management":
        edit_message(chat_id, msg_id, render_body_text("⚙️ <b>BUTTON MANAGEMENT</b>\nSelect a button to manage:"), reply_markup=otp_button_management_keyboard())

    elif data.startswith("otp_manage_btn_"):
        idx = int(data.rsplit("_", 1)[1])
        if 0 <= idx < len(bot_settings.get("otp_extra_buttons", [])):
            btn = bot_settings["otp_extra_buttons"][idx]
            edit_message(chat_id, msg_id, render_body_text(f"⚙️ <b>BUTTON MANAGEMENT</b>\n\nButton: <b>{btn.get('text', '')}</b>\nLink: <code>{btn.get('url', '')}</code>"), reply_markup=otp_single_button_keyboard(idx))

    elif data.startswith("otp_edit_btn_"):
        idx = int(data.rsplit("_", 1)[1])
        if 0 <= idx < len(bot_settings.get("otp_extra_buttons", [])):
            user_states[chat_id] = "wait_for_otp_edit_btn"
            temp_data[chat_id] = {"msg_id": msg_id, "btn_idx": idx}
            edit_message(chat_id, msg_id, render_body_text("✏️ <b>Edit Button</b>\n\nSend new format:\n<code>Button Text - https://link.com</code>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"otp_manage_btn_{idx}", "style": "danger"}]]})

    elif data.startswith("otp_customize_emoji_"):
        idx = int(data.rsplit("_", 1)[1])
        if 0 <= idx < len(bot_settings.get("otp_extra_buttons", [])):
            user_states[chat_id] = "wait_for_otp_button_emoji"
            temp_data[chat_id] = {"msg_id": msg_id, "btn_idx": idx}
            edit_message(chat_id, msg_id, render_body_text("✨ <b>Customize Emoji</b>\n\nSend the Telegram Premium/custom emoji you want to use for this button.\n\nYou may also send the custom emoji ID."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"otp_manage_btn_{idx}", "style": "danger"}]]})

    elif data.startswith("otp_delete_btn_"):
        idx = int(data.rsplit("_", 1)[1])
        if 0 <= idx < len(bot_settings.get("otp_extra_buttons", [])):
            del bot_settings["otp_extra_buttons"][idx]
            save_db()
            answer_callback(call["id"], "✅ Button deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text("⚙️ <b>BUTTON MANAGEMENT</b>\nSelect a button to manage:"), reply_markup=otp_button_management_keyboard())

    elif data == "otp_channel_not_set":
        answer_callback(call["id"], "Channel link is not configured yet.", show_alert=True)

    elif data == "edit_otp_link":
        user_states[chat_id] = "wait_for_otp_link"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new OTP Group Link:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "danger"}]]})

    elif data == "manage_panels":
        api_count = len([p for p in bot_settings["panels"] if p.get("type") == "API Panel"])
        cpt_count = len([p for p in bot_settings["panels"] if p.get("type", "API Panel") == "Auto Captcha Panel"])
        text = f"{PEM['gear']} <b>Panel Management</b>\n\nSelect which type of panel system you want to manage:"
        kb = {"inline_keyboard": [
            [{"text": f"Manage API Panels ({api_count})", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "manage_api_panels", "style": "primary"}],
            [{"text": f"Manage Auto Captcha Panels ({cpt_count})", "icon_custom_emoji_id": "5353022963132174959", "callback_data": "manage_cpt_panels", "style": "success"}],
            [{"text": "Back to System", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
        ]}
        edit_message(chat_id, msg_id, render_body_text(text), reply_markup=kb)

    elif data in ["manage_api_panels", "manage_cpt_panels"]:
        p_type = "API Panel" if data == "manage_api_panels" else "Auto Captcha Panel"
        p_list = [p for p in bot_settings["panels"] if p.get("type", "API Panel") == p_type]
        icon = f"{PEM['world']} API" if p_type == 'API Panel' else f"{PEM['lock']} Auto Captcha"
        
        active_count = sum(1 for p in p_list if p.get("status") == "ON")
        text = f"{icon} <b>{p_type}s Management</b>\n\n👀 <b>Active Monitors:</b> {active_count}\n\n🟢 <b>Available Providers:</b>\n"
        for p in p_list:
            status = "Monitoring" if p['status'] == 'ON' else "Stopped"
            login_state = p.get('login_status', '')
            if p['type'] == 'Auto Captcha Panel':
                conf = f" {login_state}" if login_state else f"{PEM['ok']} Configured"
            else:
                api_state = p.get("api_status", "")
                if api_state:
                    conf = api_state
                else:
                    conf = f"{PEM['ok']} Configured" if api_panel_is_configured(p) else f"{PEM['no']} Not Configured"
            text += f"• {p['name']}: {PEM['ok'] if p['status']=='ON' else PEM['no']} {status} | {conf}\n"
        edit_message(chat_id, msg_id, render_body_text(text), reply_markup=typed_panels_list_keyboard(p_type))

    elif data in ["add_api_panel", "add_cpt_panel"]:
        user_states[chat_id] = "wait_for_panel_name"
        p_type = "api" if data == "add_api_panel" else "logc"
        temp_data[chat_id] = {"msg_id": msg_id, "add_type": p_type}
        edit_message(chat_id, msg_id, render_body_text("📝 Please send the name of the New Provider:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"manage_{'api' if p_type=='api' else 'cpt'}_panels", "style": "danger"}]]})

    elif data.startswith("add_ptype_"):
        pass

    elif data in ["list_del_api", "list_del_cpt"]:
        p_type = "API Panel" if data == "list_del_api" else "Auto Captcha Panel"
        kb = []
        for idx, p in enumerate(bot_settings["panels"]):
            if p.get("type", "API Panel") == p_type:
                kb.append([{"text": f"Delete {p['name']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"do_del_pnl_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"manage_{'api' if p_type=='API Panel' else 'cpt'}_panels", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['trash']} <b>Select a Provider to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("do_del_pnl_"):
        idx = int(data.split("_")[3])
        if 0 <= idx < len(bot_settings["panels"]):
            p_type = bot_settings["panels"][idx].get("type", "API Panel")
            del bot_settings["panels"][idx]
            save_db()
            answer_callback(call["id"], "✅ Provider Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"manage_{'api' if p_type=='API Panel' else 'cpt'}_panels", "id": "internal"})

    elif data.startswith("tog_pnl_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["panels"]):
            p = bot_settings["panels"][idx]
            
            p["status"] = "ON" if p["status"] == "OFF" else "OFF"
            save_db()
            
            if p["type"] == "Auto Captcha Panel":
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>Login Status:</b> {p.get('login_status', 'Unknown')}\n<b>Login URL:</b> <code>{p.get('login_url', 'None')}</code>\n<b>User:</b> <code>{p.get('username', 'None')}</code>"
            else:
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
            edit_message(chat_id, msg_id, render_body_text(text), reply_markup=panel_config_keyboard(idx))

    elif data.startswith("conf_pnl_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["panels"]):
            p = bot_settings["panels"][idx]
            if p["type"] == "Auto Captcha Panel":
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>Login Status:</b> {p.get('login_status', 'Unknown')}\n<b>Login URL:</b> <code>{p.get('login_url', 'None')}</code>\n<b>User:</b> <code>{p.get('username', 'None')}</code>\n<b>Num Col:</b> {p.get('num_col_name')} (Idx: {p.get('num_col_idx')})\n<b>Msg Col:</b> {p.get('msg_col_name')} (Idx: {p.get('msg_col_idx')})"
            else:
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>\n<b>Full API URL:</b> <code>{p.get('full_api_url', 'None')}</code>"
            edit_message(chat_id, msg_id, render_body_text(text), reply_markup=panel_config_keyboard(idx))

    elif data.startswith("set_p_api_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_api"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the API URL for this provider:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_tok_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_tok"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Token for this provider:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_fapi_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_fapi"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the FULL API URL (Example: http://api.com/get?key=YOUR_TOKEN&start=0):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_rec_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_rec"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the number of records to fetch (e.g. 10).\nType <code>0</code> for Unlimited:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("test_p_conn_"):
        idx = int(data.split("_")[3])
        p = bot_settings["panels"][idx]
        wait_msg = send_message(chat_id, render_body_text("⏳ Testing connection. Please wait..."))
        wait_msg_id = wait_msg.get("result", {}).get("message_id") if wait_msg else None
        answer_callback(call["id"])
        
        try:
            parsed = []
            raw_text = ""
            
            if p["type"] == "Auto Captcha Panel":
                sess = panel_sessions.get(idx)
                if not sess:
                    success = attempt_auto_login(p, idx)
                    if not success:
                        if wait_msg_id: delete_message(chat_id, wait_msg_id)
                        send_message(chat_id, render_body_text(f"❌ <b>Auto Login Failed!</b>\nReason: {html.escape(str(p.get('login_status', 'Unknown')))}"))
                        return
                    sess = panel_sessions.get(idx)
                    
                login_url = p.get("login_url", "").strip()
                if not login_url.startswith("http"): login_url = "http://" + login_url
                msg_link = p.get("msg_link", "").strip()
                if not msg_link.startswith("http") and msg_link != "": msg_link = "http://" + msg_link
                check_url = msg_link if msg_link else f"{login_url.split('/login')[0]}/client/SMSCDRStats"
                
                # 🌟 test connection supports sAjaxSource & HTML table parser
                parsed, raw_text = fetch_cpt_panel_cdrs(p, sess, check_url)
                
            else:
                full_url = p.get("full_api_url", "").strip()
                url = p.get("api_url", "").strip()
                token = p.get("token", "").strip()
                if not full_url and not url:
                    if wait_msg_id: delete_message(chat_id, wait_msg_id)
                    send_message(chat_id, render_body_text("❌ Please Set API URL or Full API URL first!"))
                    return
                
                urls_to_try = []
                if full_url:
                    urls_to_try.append(full_url)
                else:
                    if "{token}" in url or "{key}" in url:
                        urls_to_try.append(url.replace("{token}", token).replace("{key}", token))
                    elif "token=" in url or "key=" in url:
                        urls_to_try.append(url)
                    else:
                        sep = '&' if '?' in url else '?'
                        urls_to_try.append(f"{url}{sep}token={token}")
                        urls_to_try.append(f"{url}{sep}key={token}&start=0")
                        urls_to_try.append(f"{url}{sep}key={token}")
                    
                parsed = []
                raw_text = ""
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                for try_url in urls_to_try:
                    try:
                        res = requests.get(try_url, headers=headers, timeout=10)
                        raw_text = res.text
                        parsed = parse_panel_response(raw_text, p)
                        if parsed:
                            if not full_url and try_url != url and token:
                                p["api_url"] = try_url.replace(token, "{token}")
                                save_db()
                            break
                    except: pass
                 
            if wait_msg_id: delete_message(chat_id, wait_msg_id)
                 
            if parsed:
                txt = f"✅ <b>Connection Successful!</b>\n\n🎯 <b>Parsed Data Sample (Max 3):</b>\n\n"
                
                for i, sample in enumerate(parsed[:3]):
                    num = sample['number']
                    msg = sample['message']
                    otp = sample['otp']
                    
                    app_name = str(sample.get("service", "") or detect_service(msg) or "").strip()
                    app_full_name, prem_app_html = get_service_info_html(app_name, msg)
                    
                    txt += f"<b>{i+1}.</b> {prem_app_html} <b>{app_full_name}</b>\n"
                    txt += f"📱 Number: <code>{num}</code>\n"
                    txt += f"📝 Full Msg: <code>{html.escape(msg)}</code>\n"
                    txt += f"🔐 OTP: <code>{otp}</code>\n"
                    txt += "➖" * 12 + "\n"
                    
                send_message(chat_id, render_body_text(txt))
            else:
                if p["type"] == "Auto Captcha Panel":
                    try:
                        soup = BeautifulSoup(raw_text, 'html.parser')
                        tables = soup.find_all('table')
                        if tables:
                            full_table_data = "🔍 FULL TABLE DATA (A-Z)\n" + "="*50 + "\n\n"
                            for t_idx, table in enumerate(tables):
                                full_table_data += f"--- Table {t_idx+1} ---\n"
                                rows = table.find_all('tr')
                                for r_idx, row in enumerate(rows):
                                    cols = row.find_all(['th', 'td'])
                                    col_texts = [f"[{c_idx+1}] {c.get_text(separator=' ', strip=True)}" for c_idx, c in enumerate(cols)]
                                    full_table_data += f"Row {r_idx+1}: {' | '.join(col_texts)}\n"
                                full_table_data += "\n" + "="*50 + "\n"
                            
                            send_document(chat_id, f"Full_Panel_Data_{idx}.txt", full_table_data.encode('utf-8'))
                            fail_txt = f"⚠️ <b>Connected, but couldn't parse OTP data!</b>\n\n<i>আমি ওই লিংকের সম্পূর্ণ (A-Z) ডাটা একটি Text File এ পাঠিয়েছি। ফাইলটি ওপেন করে সঠিক Column Number (যেমন: [1], [3]) চেক করে প্যানেলে আপডেট করে নাও।</i>"
                            send_message(chat_id, render_body_text(fail_txt))
                        else:
                            send_message(chat_id, render_body_text(f"⚠️ <b>Connected, but no HTML Table found!</b>\nMake sure the message link is correct."))
                    except Exception as e:
                        send_message(chat_id, render_body_text(f"❌ <b>Error parsing HTML:</b> {html.escape(str(e))}"))
                else:
                    safe_html = html.escape(str(raw_text)[:300])
                    send_message(chat_id, render_body_text(f"⚠️ <b>Connected, but couldn't find/parse OTP data.</b>\n\n<i>Make sure your API config is correct.</i>\n\nRaw HTML/Data (excerpt):\n<code>{safe_html}...</code>"))
        except Exception as e:
            if wait_msg_id: delete_message(chat_id, wait_msg_id)
            send_message(chat_id, render_body_text(f"❌ <b>Connection Failed!</b>\nError: {html.escape(str(e))}"))

    elif data == "dxa_control":
        if chat_id in user_states: del user_states[chat_id]
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>DXA CONTROL PANEL</b>"), reply_markup=dxa_control_keyboard())

    elif data == "dxa_toggle_w":
        bot_settings["withdraw_on"] = not bot_settings["withdraw_on"]
        save_db()
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>DXA CONTROL PANEL</b>"), reply_markup=dxa_control_keyboard())

    elif data == "manage_w_methods":
        edit_message(chat_id, msg_id, render_body_text("💳 <b>WITHDRAWAL METHODS</b>\n\nManage your withdrawal methods below:"), reply_markup=w_methods_keyboard())

    elif data == "add_wm":
        user_states[chat_id] = "wait_for_add_wm"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the name of the new Withdrawal Method:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_w_methods", "style": "danger"}]]})

    elif data.startswith("del_wm_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["w_methods"]):
            del bot_settings["w_methods"][idx]
            save_db()
            answer_callback(call["id"], "✅ Method deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text("💳 <b>WITHDRAWAL METHODS</b>\n\nManage your withdrawal methods below:"), reply_markup=w_methods_keyboard())

    elif data.startswith("dxa_"):
        key = data.replace("dxa_", "")
        key_map = {"min_w": "min_withdraw", "otp_r": "otp_reward", "ref_r": "refer_reward", "cool": "cooldown", "num_req": "num_req", "num_share": "num_share", "sup_link": "support_link", "w_group": "w_group"}
        if key in key_map:
            temp_data[chat_id] = {"msg_id": msg_id, "key": key_map[key]}
            user_states[chat_id] = "set_dxa"
            cancel_kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_dxa_edit", "style": "danger"}]]}
            edit_message(chat_id, msg_id, render_body_text(f"📝 Please send the new value for <code>{key_map[key]}</code>:"), reply_markup=cancel_kb)
            answer_callback(call["id"])

    elif data.startswith("g_s_"):
        service = _canonical_service(data[len("g_s_"):])
        service_catalog = _merged_get_number_catalog()
        service_entry = service_catalog.get(service) or {}
        countries = set(service_entry.get("countries", {}).keys())
        display_db = service_entry.get("country_display", {}) or {}
        c_msg = bot_settings["custom_messages"].get("select_country", {})
        txt = render_body_text(c_msg.get("text", "📌 Select a country for {service}:").replace("{service}", service))
        kb = []
        for country_id in sorted(countries):
            meta = display_db.get(country_id, {}) if isinstance(display_db, dict) else {}
            country_name, flag_char, _iso = _country_display(
                country_id, meta.get("name", ""), meta.get("flag", "")
            )
            kb.append([{"text": f"{flag_char + ' ' if flag_char else ''}{country_name}", "callback_data": f"g_c_{service}_{country_id}", "style": "success"}])
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_get_number", "style": "danger"}])
        edit_message(chat_id, msg_id, txt, reply_markup={"inline_keyboard": kb})

    elif data == "set_prefix":
        current_prefix = str(user_prefixes.get(chat_id, "")).strip()

        # Prefix button is a true ON/OFF toggle. If already ON, turn it OFF
        # instantly and keep the user on the exact same Number page.
        if current_prefix:
            user_prefixes.pop(chat_id, None)
            user_states.pop(chat_id, None)
            temp_data.pop(chat_id, None)
            number_page_snapshots.pop(chat_id, None)

            # Prefix OFF must immediately return to the normal Country number
            # flow. Use the user's configured num_req count (for example 3)
            # and let the existing GET NUMBER allocation flow fetch the next
            # active numbers serial/order-wise without any Prefix filter.
            off_session = user_active_sessions.get(chat_id, {})
            off_service = str(off_session.get("service", "")).strip()
            off_country = str(off_session.get("country", "")).strip()

            if off_service and off_country:
                handle_callback({
                    "message": call["message"],
                    "data": f"g_c_{off_service}_{off_country}",
                    "id": call["id"]
                })
            else:
                try:
                    markup = {"inline_keyboard": [list(row) for row in call["message"].get("reply_markup", {}).get("inline_keyboard", [])]}
                    for row in markup["inline_keyboard"]:
                        for btn in row:
                            if btn.get("callback_data") == "set_prefix":
                                btn["text"] = "🔢 Set Prefix"
                    current_text = call["message"].get("text", "NEW NUMBER\n")
                    edit_message(chat_id, msg_id, current_text, reply_markup=markup)
                except Exception:
                    pass
                answer_callback(call["id"])
            return

        # Save the current Number page so it can be restored after the user
        # sends a new prefix, without creating a separate confirmation message.
        original_markup = call["message"].get("reply_markup", {})
        number_page_snapshots[chat_id] = {
            "msg_id": msg_id,
            "reply_markup": {"inline_keyboard": [dict(btn) for row in original_markup.get("inline_keyboard", []) for btn in row] }
        }
        # Preserve the original row structure separately.
        number_page_snapshots[chat_id]["reply_markup"] = {
            "inline_keyboard": [[dict(btn) for btn in row] for row in original_markup.get("inline_keyboard", [])]
        }
        number_page_snapshots[chat_id]["text"] = call["message"].get("text", "NEW NUMBER\n")
        temp_data[chat_id] = {
            "msg_id": msg_id,
            "reply_markup": {"inline_keyboard": [[dict(btn) for btn in row] for row in original_markup.get("inline_keyboard", [])]},
            "text": call["message"].get("text", "NEW NUMBER\n")
        }
        user_states[chat_id] = "wait_for_prefix"
        if current_prefix:
            prompt = (
                "🔢 <b>SET PREFIX</b>\n\n"
                f"Current Prefix: <code>{current_prefix}</code>\n\n"
                "নতুন Prefix পাঠান। <b>5 থেকে 10 digit</b> হতে হবে।\n"
                "উদাহরণ: <code>26138234</code>"
            )
        else:
            prompt = (
                "🔢 <b>SET PREFIX</b>\n\n"
                "আপনার Prefix পাঠান। <b>5 থেকে 10 digit</b> হতে হবে।\n"
                "উদাহরণ: <code>26138234</code>"
            )
        edit_message(chat_id, msg_id, render_body_text(prompt), reply_markup=get_cancel_kb())
        answer_callback(call["id"])
        return

    elif data.startswith("tr_rng_"):
        # TRAFFIC ONLY: allocate directly from the exact range the user clicked.
        # This is intentionally separate from the generic c_n_s_ search path so
        # the Traffic Range flow uses the same working VOLTX allocator as GET NUMBER.
        try:
            traffic_payload = data[len("tr_rng_"):]
            parts = traffic_payload.split("|", 2)
            traffic_range = str(parts[0]).strip() if len(parts) > 0 else ""
            traffic_service = str(parts[1]).strip() if len(parts) > 1 else ""
            traffic_country = str(parts[2]).strip() if len(parts) > 2 else ""
            traffic_range_clean = traffic_range.replace("X", "").replace("x", "").strip()
        except Exception:
            traffic_range = traffic_range_clean = traffic_service = traffic_country = ""

        if not traffic_range_clean or not traffic_service or not traffic_country:
            answer_callback(call["id"], "❌ Invalid Traffic range!", show_alert=True)
            return

        edit_message(chat_id, msg_id, render_body_text("⌛ <i>Processing... Finding Number...</i>"))
        wait_msg_id = msg_id

        # Use the exact same successful VOLTX allocation function used by
        # GET NUMBER. The clicked Traffic range is passed as the range hint.
        req_count = max(1, int(bot_settings.get("num_req", 3) or 3))
        fetched_nums = []
        assigned_infos = []
        active_prefix = re.sub(r"\D", "", str(user_prefixes.get(chat_id, "")).strip())
        _traffic_attempt_limit = (req_count * 10) if active_prefix else req_count
        for _ in range(max(req_count, _traffic_attempt_limit)):
            num_str, err, info = voltx_allocate_number(traffic_range_clean)
            if not num_str:
                continue
            _clean_allocated = re.sub(r"\D", "", str(num_str))
            if active_prefix and not _clean_allocated.startswith(active_prefix):
                continue
            returned_range = str((info or {}).get("range", "")).replace("X", "").replace("x", "").strip()
            if returned_range and not (returned_range.startswith(traffic_range_clean) or traffic_range_clean.startswith(returned_range)):
                continue
            fetched_nums.append(num_str)
            assigned_infos.append(info or {})
            voltx_assigned_numbers[num_str] = chat_id
            total_assigned_stats += 1
            increment_numbers_used(chat_id)

        if not fetched_nums:
            if active_prefix:
                no_stock_text = (
                    "⚠️ <b>এই Prefix-এর কোনো নাম্বার বর্তমানে স্টকে Available নেই।</b>\n\n"
                    "🔄 <b>দয়া করে অন্য Prefix দিয়ে চেষ্টা করুন অথবা Prefix OFF করুন।</b>"
                )
                edit_message(chat_id, wait_msg_id, render_body_text(no_stock_text), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"exp_c_{traffic_service}_{traffic_country}", "style": "danger"}]]})
                answer_callback(call["id"])
            else:
                edit_message(chat_id, wait_msg_id, render_body_text("❌ Number out of stock!"))
                answer_callback(call["id"], "❌ Number out of stock!", show_alert=True)
            return

        save_db()

        app_full_name, _ = get_service_info_html(traffic_service)
        service_label = str(app_full_name or traffic_service).strip()
        country_raw = traffic_country
        country_iso = country_raw.upper() if len(country_raw) == 2 and country_raw.isalpha() else ""
        if not country_iso:
            for _iso, _name in COUNTRY_NAME_BY_ISO.items():
                if str(_name).strip().casefold() == country_raw.casefold():
                    country_iso = _iso
                    break
        country_label = str(COUNTRY_NAME_BY_ISO.get(country_iso, country_raw)).strip().title()
        flag_label = ISO_TO_FLAG.get(country_iso, "🌍")
        for _fd in bot_settings.get("premium_flags", {}).values():
            if str(_fd.get("iso", "")).strip().upper() == country_iso:
                flag_label = _fd.get("char") or flag_label
                break

        header = f"📱 <b>{html.escape(service_label)} Number</b>"
        if country_label:
            header += f"\n{flag_label} <b>{html.escape(country_label)}</b>"

        kb = []
        flags_db = bot_settings.get("premium_flags", {})
        for num in fetched_nums:
            _, iso = get_flag_and_code(num)
            display_num = f"+{num}" if not str(num).startswith("+") else str(num)
            emoji_id = "5780471598922337683"
            for flag_data in flags_db.values():
                if str(iso).upper() == str(flag_data.get("iso", "")).upper():
                    if "id" in flag_data:
                        emoji_id = flag_data["id"]
                    break
            kb.append([{"text": display_num, "icon_custom_emoji_id": emoji_id, "copy_text": {"text": display_num}, "style": "primary"}])

        kb.append([
            {"text": "Change Number", "icon_custom_emoji_id": "5465368548702446780", "callback_data": f"tr_rng_{traffic_range_clean}|{traffic_service}|{traffic_country}", "style": "danger"},
            {"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}
        ])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"exp_c_{traffic_service}_{traffic_country}", "style": "danger"}])

        edit_message(chat_id, wait_msg_id, render_body_text(header), reply_markup={"inline_keyboard": kb})
        user_active_sessions[chat_id] = {"msg_id": wait_msg_id, "nums": fetched_nums, "service": traffic_service, "country": traffic_country}
        user_cooldowns[chat_id] = 0
        answer_callback(call["id"])
        return

    elif data.startswith("g_c_") or data.startswith("c_n_"):
        if data.startswith("g_c_"):
            # Service -> Country: every manually uploaded number is immediately ACTIVE.
            payload = data[len("g_c_"):].strip()
            if "_" in payload:
                service_raw, country_raw = payload.rsplit("_", 1)
            else:
                service_raw, country_raw = payload, ""
            service = _canonical_service(service_raw)
            country = country_raw.strip()
            country_id = _country_identity(country)
            req_count = max(1, int(bot_settings.get("num_req", 3) or 3))
            active_prefix = re.sub(r"\D", "", str(user_prefixes.get(chat_id, "")).strip())
            fetched_nums = []

            # LOCAL/MANUAL STOCK FIRST. This does not depend on VOLTX live traffic.
            found = _find_local_numbers(service, country, chat_id, req_count)
            for b_id, idx in found:
                if len(fetched_nums) >= req_count:
                    break
                n_obj = number_batches[b_id]["numbers"][idx]
                num_str = str(n_obj.get("num", "")).strip()
                if not num_str:
                    continue
                fetched_nums.append(num_str)
                _remember_local_assignment(num_str, chat_id, service, country_id)
                n_obj["shares"] = int(n_obj.get("shares", 0) or 0) + 1
                n_obj.setdefault("used_by", []).append(chat_id)
                total_assigned_stats += 1
                increment_numbers_used(chat_id)
                if n_obj["shares"] >= bot_settings.get("num_share", 1):
                    n_obj["to_remove"] = True
                    used_numbers_list.append(num_str)

            for b_id in list(number_batches):
                number_batches[b_id]["numbers"] = [n for n in number_batches[b_id].get("numbers", []) if not n.get("to_remove")]

            # If local stock is short, fall back to configured live API sources.
            if len(fetched_nums) < req_count:
                voltx_ranges = []
                try:
                    live_catalog = get_voltx_active_catalog(LIVE_ACCESS_DISPLAY_WINDOW)
                    for live_srv, live_countries in live_catalog.items():
                        if _canonical_service(live_srv) != service:
                            continue
                        for live_country, ranges in live_countries.items():
                            if _country_identity(live_country) == country_id:
                                for r in ranges or []:
                                    clean = str(r).replace("X", "").replace("x", "").strip()
                                    if clean and clean not in voltx_ranges:
                                        voltx_ranges.append(clean)
                except Exception:
                    pass

                if voltx_ranges and bot_settings.get("voltx_keys"):
                    for rng in voltx_ranges:
                        _range_attempts = 0
                        _range_attempt_limit = (max(1, req_count) * 10) if active_prefix else max(1, req_count)
                        while len(fetched_nums) < req_count and _range_attempts < _range_attempt_limit:
                            _range_attempts += 1
                            num_str, _err, _info = voltx_allocate_number(rng)
                            if not num_str:
                                break
                            _clean_allocated = re.sub(r"\D", "", str(num_str))
                            if active_prefix and not _clean_allocated.startswith(active_prefix):
                                continue
                            fetched_nums.append(num_str)
                            voltx_assigned_numbers[num_str] = chat_id
                            total_assigned_stats += 1
                            increment_numbers_used(chat_id)
                        if len(fetched_nums) >= req_count:
                            break

                if len(fetched_nums) < req_count and bot_settings.get("stex_keys"):
                    for rng in _normalized_stex_ranges(service, country):
                        while len(fetched_nums) < req_count:
                            got = False
                            for api_key in bot_settings.get("stex_keys", []):
                                try:
                                    res = requests.post(f"{STEX_BASE_URL}/getnum", json={"rid": rng}, headers={"mauthapi": api_key}, timeout=10)
                                    data = res.json()
                                    if data.get("meta", {}).get("code") == 200 and data.get("data"):
                                        api_num = data.get("data") or {}
                                        num_str = ""
                                        for nk in ("no_plus_number", "national_number", "number", "phone", "msisdn", "mobile", "mobile_number"):
                                            candidate = re.sub(r"\D", "", str(api_num.get(nk, "") or ""))
                                            if 5 <= len(candidate) <= 18:
                                                num_str = candidate
                                                break
                                        if num_str:
                                            if active_prefix and not num_str.startswith(active_prefix):
                                                continue
                                            fetched_nums.append(num_str)
                                            stex_assigned_numbers[num_str] = chat_id
                                            total_assigned_stats += 1
                                            increment_numbers_used(chat_id)
                                            got = True
                                            break
                                except Exception:
                                    continue
                            if not got:
                                break
                        if len(fetched_nums) >= req_count:
                            break

            if not fetched_nums:
                # PREFIX FLOW FIX ONLY:
                # Do not block the user at Country -> Get Number when the
                # currently active Prefix has no matching stock. Keep the
                # user on the Country/Number page so the Prefix can be
                # switched OFF (or changed) before trying again.
                if active_prefix:
                    app_full_name, _ = get_service_info_html(service)
                    country_name, flag_char, _iso = _batch_country_display(service, country_id)
                    header = f"📱 <b>{html.escape(str(app_full_name or service).upper())} Number</b>"
                    if country_name:
                        header += f"\n{flag_char + ' ' if flag_char else ''}<b>{html.escape(country_name)}</b>"
                    no_stock_text = (
                        "⚠️ <b>এই Prefix-এর কোনো নাম্বার বর্তমানে স্টকে Available নেই।</b>\n\n"
                        "🔄 <b>Prefix OFF করুন অথবা অন্য Prefix দিয়ে চেষ্টা করুন।</b>"
                    )
                    prefix_button = {
                        "text": f"🔢 Prefix ON • {active_prefix}",
                        "icon_custom_emoji_id": "5352862640592949843",
                        "callback_data": "set_prefix",
                        "style": "success"
                    }
                    # Prefix no-stock page: keep only the controls needed to
                    # turn Prefix OFF/change it or go back. The service-title
                    # and Change Number buttons are intentionally omitted here.
                    no_stock_kb = {
                        "inline_keyboard": [
                            [prefix_button],
                            [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_country", "style": "danger"}]
                        ]
                    }
                    edit_message(chat_id, msg_id, render_body_text(header + "\n\n" + no_stock_text), reply_markup=no_stock_kb)
                    user_active_sessions[chat_id] = {"msg_id": msg_id, "nums": [], "service": service, "country": country_id}
                    user_cooldowns[chat_id] = 0
                    answer_callback(call["id"])
                else:
                    answer_callback(call["id"], "❌ No active number is available for this country!", show_alert=True)
                return

            save_db()
            app_full_name, _ = get_service_info_html(service)
            country_name, flag_char, _iso = _batch_country_display(service, country_id)
            header = f"📱 <b>{html.escape(str(app_full_name or service).upper())} Number</b>"
            if country_name:
                header += f"\n{flag_char + ' ' if flag_char else ''}<b>{html.escape(country_name)}</b>"

            kb = []
            # Service name is shown exactly once.
            kb.append([{"text": str(app_full_name or service).upper(), "callback_data": "ignore", "style": "success"}])
            flags_db = bot_settings.get("premium_flags", {})
            for num in fetched_nums:
                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                _, iso = get_flag_and_code(num)
                btn = {"text": display_num, "copy_text": {"text": display_num}, "style": "primary"}
                for fd in flags_db.values():
                    if str(iso).upper() == str(fd.get("iso", "")).upper() and fd.get("id"):
                        btn["icon_custom_emoji_id"] = fd["id"]
                        break
                kb.append([btn])

            # Reuse this same working flow for Change Number.
            kb.append([
                {"text": "Change Number", "icon_custom_emoji_id": "5465368548702446780", "callback_data": f"g_c_{service}_{country_id}", "style": "danger"},
                {"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}
            ])
            prefix = str(user_prefixes.get(chat_id, "")).strip()
            kb.append([{"text": f"🔢 Prefix ON • {prefix}" if prefix else "🔢 Set Prefix", "icon_custom_emoji_id": "5352862640592949843", "callback_data": "set_prefix", "style": "success"}])
            kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_country", "style": "danger"}])

            edit_message(chat_id, msg_id, render_body_text(header), reply_markup={"inline_keyboard": kb})
            user_active_sessions[chat_id] = {"msg_id": msg_id, "nums": fetched_nums, "service": service, "country": country_id}
            user_cooldowns[chat_id] = 0
            answer_callback(call["id"])
            return

        # ১. গ্লোবাল কুলডাউন চেক (সকল নাম্বার মেথডের জন্য)
        now = time.time()
        if now - user_cooldowns.get(chat_id, 0) < bot_settings["cooldown"]:
            answer_callback(call["id"], f"⌛ Please wait {int(bot_settings['cooldown'] - (now - user_cooldowns.get(chat_id, 0)))}s.", show_alert=True)
            return
        
        # কুলডাউন আপডেট
        user_cooldowns[chat_id] = now
        
        # Prefix active থাকলে Number page snapshot আগে সংরক্ষণ করি।
        # Country page দিয়ে snapshot overwrite করা যাবে না।
        if str(user_prefixes.get(chat_id, "")).strip():
            current_msg = call.get("message", {}) or {}
            current_markup = current_msg.get("reply_markup", {}) or {}
            current_buttons = [
                btn.get("callback_data", "")
                for row in current_markup.get("inline_keyboard", [])
                if isinstance(row, list)
                for btn in row
                if isinstance(btn, dict)
            ]
            if "set_prefix" in current_buttons:
                number_page_snapshots[chat_id] = {
                    "msg_id": msg_id,
                    "text": current_msg.get("text", "NEW NUMBER\n") or "NEW NUMBER\n",
                    "reply_markup": {"inline_keyboard": [[dict(btn) for btn in row] for row in current_markup.get("inline_keyboard", [])]}
                }

        # আগের নাম্বার এক্সপায়ার করা
        expire_previous_number(chat_id)

        # যদি সার্চ নাম্বার থেকে আসে
        if data.startswith("c_n_s_"):
            is_voltx_req = data.endswith("_vtx")
            clean_data = data[:-4] if is_voltx_req else data
            payload_part = clean_data[len("c_n_s_"):] if clean_data.startswith("c_n_s_") else ""
            if "|" in payload_part:
                cb_parts = payload_part.split("|", 2)
                query = cb_parts[0].strip() if len(cb_parts) > 0 else ""
                service_from_cb = cb_parts[1].strip() if len(cb_parts) > 1 else None
                country_from_cb = cb_parts[2].strip() if len(cb_parts) > 2 else None
            else:
                parts_s = clean_data.split("_", 4)
                query = parts_s[3] if len(parts_s) > 3 else ""
                service_from_cb = parts_s[4] if len(parts_s) > 4 else None
                country_from_cb = None
            
            allowed_countries = bot_settings.get("search_countries", [])
            voltx_allowed = bot_settings.get("voltx_search_countries", [])
            
            is_stex_allowed = any(query.startswith(c) for c in allowed_countries) if allowed_countries else False
            is_voltx_allowed = any(query.startswith(c) for c in voltx_allowed) if voltx_allowed else False
            
            # A Traffic/Active-Range callback is already backed by the live Voltx
            # catalog, so it must not be rejected by the older search-country allow-list.
            if not is_voltx_req and not is_stex_allowed and not is_voltx_allowed:
                try:
                    live_catalog = get_voltx_active_catalog(120)
                    live_match = False
                    for _srv, _countries in live_catalog.items():
                        if str(_srv).strip().upper() != str(service_from_cb or '').strip().upper():
                            continue
                        for _country, _ranges in _countries.items():
                            country_ok = (str(_country).strip().upper() == str(country_from_cb or '').strip().upper())
                            if not country_ok:
                                iso_try = str(country_from_cb or '').strip().upper()
                                country_ok = (COUNTRY_NAME_BY_ISO.get(iso_try, '').strip().upper() == str(_country).strip().upper())
                            if country_ok and any(str(query).replace('X','').strip().startswith(str(r).replace('X','').strip()) or str(r).replace('X','').strip().startswith(str(query).replace('X','').strip()) for r in _ranges):
                                live_match = True
                                break
                        if live_match:
                            break
                    if live_match:
                        is_voltx_req = True
                except Exception:
                    pass

            if not is_voltx_req and not is_stex_allowed and not is_voltx_allowed:
                answer_callback(call["id"], "❌ This country code is not allowed for search!", show_alert=True)
                return
                
            edit_message(chat_id, msg_id, render_body_text("⌛ <i>Processing... Finding Number...</i>"))
            wait_msg_id = msg_id
            
            active_prefix = re.sub(r"\D", "", str(user_prefixes.get(chat_id, "")).strip())
            found_indices = []
            for b_id, b_data in number_batches.items():
                for idx, n_obj in enumerate(b_data["numbers"]):
                    clean_num = re.sub(r"\D", "", str(n_obj.get("num", "")))
                    prefix_ok = (not active_prefix) or clean_num.startswith(active_prefix)
                    if clean_num.startswith(query) and prefix_ok and chat_id not in n_obj.get("used_by", []):
                        found_indices.append((b_id, idx))
            
            fetched_nums = []
            if not found_indices:
                api_found = False
                req_count = bot_settings.get("num_req", 1)
                
                # VOLTX: use the same known-working allocator used by the
                # successful 3-number flow. The clicked range is the backend rid.
                if is_voltx_allowed or is_voltx_req:
                    _voltx_attempt_limit = (req_count * 10) if active_prefix else req_count
                    for _ in range(max(req_count, _voltx_attempt_limit)):
                        if len(fetched_nums) >= req_count:
                            break
                        num_str, err, info = voltx_allocate_number(query)
                        if not num_str:
                            continue
                        _clean_allocated = re.sub(r"\D", "", str(num_str))
                        if active_prefix and not _clean_allocated.startswith(active_prefix):
                            continue
                        fetched_nums.append(num_str)
                        voltx_assigned_numbers[num_str] = chat_id
                        api_found = True
                        total_assigned_stats += 1
                        increment_numbers_used(chat_id)
                        is_voltx_req = True

                # Voltx এ না পেলে বা আরও নাম্বার লাগলে StexSMS তে চেক করবে
                if len(fetched_nums) < req_count and (is_stex_allowed and not is_voltx_req):
                    stex_keys = bot_settings.get("stex_keys", [])
                    for _ in range(req_count - len(fetched_nums)):
                        for api_key in stex_keys:
                            try:
                                headers = {"mauthapi": api_key}
                                res = requests.post(f"{STEX_BASE_URL}/getnum", json={"rid": query}, headers=headers, timeout=10)
                                resp_data = res.json()
                                if resp_data.get("meta", {}).get("code") == 200 and resp_data.get("data"):
                                    num_str = str(resp_data["data"].get("no_plus_number", "")).replace("+", "")
                                    if not num_str: num_str = str(resp_data["data"].get("national_number", ""))
                                    _clean_stex_allocated = re.sub(r"\D", "", str(num_str))
                                    if active_prefix and not _clean_stex_allocated.startswith(active_prefix):
                                        continue
                                    fetched_nums.append(num_str)
                                    stex_assigned_numbers[num_str] = chat_id 
                                    api_found = True
                                    total_assigned_stats += 1
                                    increment_numbers_used(chat_id)
                                    break
                            except: continue
                        
                if not api_found:
                    if active_prefix:
                        no_stock_text = (
                            "⚠️ <b>এই Prefix-এর কোনো নাম্বার বর্তমানে স্টকে Available নেই।</b>\n\n"
                            "🔄 <b>দয়া করে অন্য Prefix দিয়ে চেষ্টা করুন অথবা Prefix OFF করুন।</b>"
                        )
                        edit_message(chat_id, wait_msg_id, render_body_text(no_stock_text), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_number_page", "style": "danger"}]]})
                        answer_callback(call["id"])
                    else:
                        answer_callback(call["id"], "❌ Number out of stock!", show_alert=True)
                        delete_message(chat_id, wait_msg_id)
                    return
                save_db()
            else:
                random.shuffle(found_indices)
                for b_id, idx in found_indices:
                    if len(fetched_nums) >= bot_settings.get("num_req", 1): break
                    n_obj = number_batches[b_id]["numbers"][idx]
                    num_str = n_obj["num"]
                    fetched_nums.append(num_str)
                    n_obj["shares"] += 1
                    n_obj["used_by"].append(chat_id)
                    total_assigned_stats += 1
                    increment_numbers_used(chat_id)
                    if n_obj["shares"] >= bot_settings.get("num_share", 1):
                        n_obj["to_remove"] = True
                        used_numbers_list.append(num_str)
                for b_id in number_batches:
                    number_batches[b_id]["numbers"] = [n for n in number_batches[b_id]["numbers"] if not n.get("to_remove")]
                save_db()
                
            kb = []
            if service_from_cb:
                app_full_name, _ = get_service_info_html(service_from_cb)
                emoji_id_srv = "5337302974806922068"
                for app_key, app_data in bot_settings.get("premium_apps", {}).items():
                    if service_from_cb.upper() == app_key or service_from_cb.upper() in app_key or app_key in service_from_cb.upper():
                        if "id" in app_data: emoji_id_srv = app_data["id"]; break
                kb.append([{"text": f"{app_full_name}", "icon_custom_emoji_id": emoji_id_srv, "callback_data": "ignore", "style": "success"}])

            flags_db = bot_settings.get("premium_flags", {})
            for num in fetched_nums:
                _, iso = get_flag_and_code(num)
                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                emoji_id = "5780471598922337683"
                for flag_code, flag_data in flags_db.items():
                    if iso == flag_data.get("iso"):
                        if "id" in flag_data: emoji_id = flag_data["id"]; break
                kb.append([{"text": f"{display_num}", "icon_custom_emoji_id": emoji_id, "copy_text": {"text": display_num}, "style": "primary"}])
            
            vtx_ext = "_vtx" if is_voltx_req else ""
            traffic_payload = f"{query}|{service_from_cb or ''}|{country_from_cb or ''}" if service_from_cb else query
            kb.append([{"text": "Change Number", "icon_custom_emoji_id": "5465368548702446780", "callback_data": f"c_n_s_{traffic_payload}{vtx_ext}", "style": "danger"},
                       {"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}])
            prefix_label = f"🔢 Prefix ON • {active_prefix}" if active_prefix else "🔢 Set Prefix"
            kb.append([{"text": prefix_label, "icon_custom_emoji_id": "5352862640592949843", "callback_data": "set_prefix", "style": "success"}])
            
            c_btns = bot_settings["custom_messages"].get("search_number", {}).get("buttons", [])
            for c_b in c_btns: 
                b_copy = c_b.copy()
                if "style" not in b_copy: b_copy["style"] = "primary"
                kb.append([b_copy])
            kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
            
            # Show the actual assigned number in the Number page; do not leave the user stuck on a generic "NEW NUMBER" placeholder.
            assigned_country = country_from_cb or ""
            number_lines = [f"📱 <b>{str(service_from_cb or '').upper()}</b>"]
            if assigned_country:
                _country_raw = str(assigned_country).strip()
                _country_iso = _country_raw.upper() if len(_country_raw) == 2 and _country_raw.isalpha() else ""
                if not _country_iso:
                    for _iso, _name in COUNTRY_NAME_BY_ISO.items():
                        if str(_name).strip().casefold() == _country_raw.casefold():
                            _country_iso = _iso
                            break
                if not _country_iso:
                    for _fd in bot_settings.get("premium_flags", {}).values():
                        if str(_fd.get("name", "")).strip().casefold() == _country_raw.casefold():
                            _country_iso = str(_fd.get("iso", "")).strip().upper()
                            break
                cfull = COUNTRY_NAME_BY_ISO.get(_country_iso, _country_raw).title()
                _flag = ISO_TO_FLAG.get(_country_iso, "🌍")
                for _fd in bot_settings.get("premium_flags", {}).values():
                    if str(_fd.get("iso", "")).strip().upper() == _country_iso:
                        _flag = _fd.get("char") or _flag
                        break
                number_lines.append(f"{_flag} <b>{html.escape(cfull)}</b>")
            for n in fetched_nums:
                dnum = f"+{n}" if not str(n).startswith("+") else str(n)
                number_lines.append(f"📞 <code>{html.escape(dnum)}</code>")
            number_page_text = "\n".join(number_lines)
            edit_message(chat_id, wait_msg_id, render_body_text(number_page_text), reply_markup={"inline_keyboard": kb})
            user_active_sessions[chat_id] = {"msg_id": wait_msg_id, "nums": fetched_nums, "service": service_from_cb or (service if "service" in locals() else ""), "country": assigned_country}
            if str(user_prefixes.get(chat_id, "")).strip():
                number_page_snapshots[chat_id] = {"msg_id": wait_msg_id, "text": number_page_text, "reply_markup": {"inline_keyboard": [[dict(btn) for btn in row] for row in kb]}}
            return

        # যদি আপলোড করা বা সার্ভিস থেকে আসে
        parts = data.split("_")
        service = parts[2]
        country = parts[3]

        available_indices = []
        active_prefix = re.sub(r"\D", "", str(user_prefixes.get(chat_id, "")).strip())
        # Check Local Stock First. If a prefix is set, ONLY uploaded numbers
        # beginning with that complete prefix are eligible.
        for b_id, b_data in number_batches.items():
            if b_data["service"] == service and b_data["country"] == country:
                for idx, n_obj in enumerate(b_data["numbers"]):
                    clean_num = re.sub(r"\D", "", str(n_obj.get("num", "")))
                    prefix_ok = (not active_prefix) or clean_num.startswith(active_prefix)
                    if prefix_ok and chat_id not in n_obj.get("used_by", []):
                        available_indices.append((b_id, idx))

        if not available_indices:
            # Country buttons may carry either ISO (e.g. TG) or the displayed
            # full country name (e.g. Togo). Resolve both forms before looking
            # up the configured API service data, without changing the UI.
            stex_country_map = bot_settings.get("stex_services", {}).get(service, {})
            voltx_country_map = bot_settings.get("voltx_services", {}).get(service, {})

            def _resolve_country_data(country_map, selected_country):
                if not isinstance(country_map, dict):
                    return None, selected_country
                selected = str(selected_country).strip()
                if selected in country_map:
                    return country_map.get(selected), selected
                selected_upper = selected.upper()
                for key in country_map:
                    key_s = str(key).strip()
                    if key_s.upper() == selected_upper:
                        return country_map.get(key), key_s
                # Match full country names against the ISO table.
                for key in country_map:
                    key_s = str(key).strip()
                    iso_key = key_s.upper() if len(key_s) == 2 and key_s.isalpha() else ""
                    if iso_key and COUNTRY_NAME_BY_ISO.get(iso_key, "").strip().lower() == selected.lower():
                        return country_map.get(key), key_s
                return None, selected

            stex_srv_data, stex_country_key = _resolve_country_data(stex_country_map, country)
            voltx_srv_data, voltx_country_key = _resolve_country_data(voltx_country_map, country)
            
            target_range = None
            is_voltx = False

            # CHANGE NUMBER ONLY: allocate directly from the live VOLTX Console.
            # Do not route through the old c_n_s_ search callback because that
            # path can leave the Number page stuck on "Processing...".
            if data.startswith("c_n_"):
                candidate_ranges = []
                try:
                    now_live = time.time()
                    service_u = str(service).strip().upper()
                    country_u = str(country).strip().upper()
                    for _hit in reversed(recent_traffic):
                        if not isinstance(_hit, dict) or "real_range" not in _hit:
                            continue
                        try:
                            if now_live - float(_hit.get("time", 0)) > LIVE_ACCESS_DISPLAY_WINDOW:
                                continue
                        except Exception:
                            continue
                        _hs = str(_hit.get("service", "")).strip().upper()
                        _hi = str(_hit.get("iso", "")).strip().upper()
                        _hc = str(_hit.get("country", "")).strip().upper()
                        if _hs != service_u:
                            continue
                        country_ok = (_hi == country_u or _hc == country_u)
                        if not country_ok and len(country_u) == 2:
                            country_ok = (COUNTRY_NAME_BY_ISO.get(country_u, "").strip().upper() == _hc)
                        if not country_ok and len(_hi) == 2:
                            country_ok = (COUNTRY_NAME_BY_ISO.get(_hi, "").strip().upper() == country_u)
                        if not country_ok:
                            continue
                        _lr = str(_hit.get("real_range", "")).replace("X", "").replace("x", "").strip()
                        if _lr and _lr not in candidate_ranges:
                            candidate_ranges.append(_lr)
                except Exception:
                    candidate_ranges = []

                # If the newest Console range is unavailable, keep the current
                # active range(s) as fallback instead of switching provider.
                if not candidate_ranges:
                    try:
                        live_catalog = get_voltx_active_catalog(LIVE_ACCESS_DISPLAY_WINDOW)
                        service_key = next((k for k in live_catalog if str(k).strip().upper() == str(service).strip().upper()), None)
                        if service_key:
                            for _country, _ranges in live_catalog.get(service_key, {}).items():
                                c1 = str(_country).strip().upper()
                                c2 = str(country).strip().upper()
                                country_ok = c1 == c2
                                if not country_ok and len(c2) == 2:
                                    country_ok = COUNTRY_NAME_BY_ISO.get(c2, "").strip().upper() == c1
                                if not country_ok and len(c1) == 2:
                                    country_ok = COUNTRY_NAME_BY_ISO.get(c1, "").strip().upper() == c2
                                if country_ok:
                                    for _r in _ranges or []:
                                        _clean = str(_r).replace("X", "").replace("x", "").strip()
                                        if _clean and _clean not in candidate_ranges:
                                            candidate_ranges.append(_clean)
                    except Exception:
                        pass

                if not candidate_ranges and voltx_srv_data:
                    for _r in voltx_srv_data:
                        _clean = str(_r).replace("X", "").replace("x", "").strip()
                        if _clean and _clean not in candidate_ranges:
                            candidate_ranges.append(_clean)

                if candidate_ranges:
                    target_range = candidate_ranges[0]
                    is_voltx = True

                    edit_message(chat_id, msg_id, render_body_text("⌛ <i>Processing... Finding Number...</i>"))
                    wait_msg_id = msg_id
                    req_count = max(1, int(bot_settings.get("num_req", 3) or 3))
                    fetched_nums = []
                    assigned_infos = []

                    # Try newest range first, then the remaining currently-active
                    # ranges for the same service/country.
                    for _rng in candidate_ranges:
                        _range_attempts = 0
                        _range_attempt_limit = (max(1, req_count) * 10) if active_prefix else max(1, req_count)
                        while len(fetched_nums) < req_count and _range_attempts < _range_attempt_limit:
                            _range_attempts += 1
                            num_str, err, info = voltx_allocate_number(_rng)
                            if not num_str:
                                break
                            _clean_allocated = re.sub(r"\D", "", str(num_str))
                            if active_prefix and not _clean_allocated.startswith(active_prefix):
                                continue
                            fetched_nums.append(num_str)
                            assigned_infos.append(info or {})
                            voltx_assigned_numbers[num_str] = chat_id
                            total_assigned_stats += 1
                            increment_numbers_used(chat_id)
                        if len(fetched_nums) >= req_count:
                            break

                    if not fetched_nums:
                        if active_prefix:
                            no_stock_text = (
                                "⚠️ <b>এই Prefix-এর কোনো নাম্বার বর্তমানে স্টকে Available নেই।</b>\n\n"
                                "🔄 <b>দয়া করে অন্য Prefix দিয়ে চেষ্টা করুন অথবা Prefix OFF করুন।</b>"
                            )
                            no_stock_kb = {"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_number_page", "style": "danger"}]]}
                            edit_message(chat_id, wait_msg_id, render_body_text(no_stock_text), reply_markup=no_stock_kb)
                            answer_callback(call["id"])
                        else:
                            edit_message(chat_id, wait_msg_id, render_body_text("❌ Number out of stock!"))
                            answer_callback(call["id"], "❌ Number out of stock!", show_alert=True)
                        return

                    save_db()

                    # Rebuild the SAME Number page UI with the newly allocated
                    # numbers. No extra message and no range is shown.
                    app_full_name, _ = get_service_info_html(service)
                    service_label = str(app_full_name or service).strip()
                    country_raw = str(country or "").strip()
                    country_iso = country_raw.upper() if len(country_raw) == 2 and country_raw.isalpha() else ""
                    if not country_iso:
                        for _iso, _name in COUNTRY_NAME_BY_ISO.items():
                            if str(_name).strip().casefold() == country_raw.casefold():
                                country_iso = _iso
                                break
                    if not country_iso:
                        for _fd in bot_settings.get("premium_flags", {}).values():
                            if str(_fd.get("name", "")).strip().casefold() == country_raw.casefold():
                                country_iso = str(_fd.get("iso", "")).strip().upper()
                                break
                    country_label = str(COUNTRY_NAME_BY_ISO.get(country_iso, country_raw)).strip().title()
                    flag_label = ISO_TO_FLAG.get(country_iso, "🌍")
                    for _fd in bot_settings.get("premium_flags", {}).values():
                        if str(_fd.get("iso", "")).strip().upper() == country_iso:
                            flag_label = _fd.get("char") or flag_label
                            break
                    header = f"📱 <b>{html.escape(service_label)} Number</b>"
                    if country_label:
                        header += f"\n{flag_label} <b>{html.escape(country_label)}</b>"

                    kb = []
                    flags_db = bot_settings.get("premium_flags", {})
                    for num in fetched_nums:
                        _, iso = get_flag_and_code(num)
                        display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                        emoji_id = "5780471598922337683"
                        for flag_data in flags_db.values():
                            if str(iso).upper() == str(flag_data.get("iso", "")).upper():
                                if "id" in flag_data:
                                    emoji_id = flag_data["id"]
                                break
                        kb.append([{"text": display_num, "icon_custom_emoji_id": emoji_id, "copy_text": {"text": display_num}, "style": "primary"}])

                    kb.append([
                        {"text": "Change Number", "icon_custom_emoji_id": "5465368548702446780", "callback_data": f"c_n_{service}_{country}", "style": "danger"},
                        {"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}
                    ])
                    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_country", "style": "danger"}])

                    edit_message(chat_id, wait_msg_id, render_body_text(header), reply_markup={"inline_keyboard": kb})
                    user_active_sessions[chat_id] = {"msg_id": wait_msg_id, "nums": fetched_nums, "service": service, "country": country}
                    user_cooldowns[chat_id] = 0
                    answer_callback(call["id"])
                    return

                answer_callback(call["id"], "❌ No active VOLTX range found!", show_alert=True)
                return

            # Non-Change-Number callbacks keep the existing provider-selection
            # behavior unchanged.
            if target_range is None and stex_srv_data and len(stex_srv_data) > 0:
                target_range = random.choice(stex_srv_data)
            elif voltx_srv_data and len(voltx_srv_data) > 0:
                # Never use a stale/inactive Voltx service or range.
                active_catalog = get_voltx_active_catalog(120)
                active_ranges = set()
                for _srv, _countries in active_catalog.items():
                    if _srv.upper() == service.upper():
                        for _country, _ranges in _countries.items():
                            _c1 = str(_country).strip().upper()
                            _c2 = str(country).strip().upper()
                            _c3 = str(voltx_country_key).strip().upper()
                            if _c1 in {_c2, _c3} or COUNTRY_NAME_BY_ISO.get(_c1, "").strip().upper() in {_c2, _c3}:
                                active_ranges.update(_ranges)
                valid_ranges = [r for r in voltx_srv_data if any(str(r).startswith(str(ar)) or str(ar).startswith(str(r)) for ar in active_ranges)]
                if valid_ranges:
                    target_range = random.choice(valid_ranges)
                    is_voltx = True
            else:
                # GET NUMBER can expose a country from the live Voltx catalog even
                # when the saved voltx_services map has not been populated yet.
                active_catalog = get_voltx_active_catalog(120)
                for _srv, _countries in active_catalog.items():
                    if _srv.upper() != service.upper():
                        continue
                    for _country, _ranges in _countries.items():
                        _c1 = str(_country).strip().upper()
                        _c2 = str(country).strip().upper()
                        if _c1 == _c2 or COUNTRY_NAME_BY_ISO.get(_c2, '').strip().upper() == _c1:
                            if _ranges:
                                target_range = random.choice(list(_ranges))
                                is_voltx = True
                                country = _country
                                break
                    if target_range:
                        break
                
            if target_range:
                user_cooldowns[chat_id] = 0
                vtx_flag = "_vtx" if is_voltx else ""
                range_payload = f"{target_range}|{service}|{country}"
                handle_callback({"message": call["message"], "data": f"c_n_s_{range_payload}{vtx_flag}", "id": call["id"]})
                return
            else:
                answer_callback(call["id"], "❌ Number out of stock or range missing!", show_alert=True)
                if data.startswith("c_n_"): delete_message(chat_id, msg_id)
                return

        random.shuffle(available_indices)
        
        fetched_nums = []
        for b_id, idx in available_indices:
            if len(fetched_nums) >= bot_settings["num_req"]: break
            n_obj = number_batches[b_id]["numbers"][idx]
            
            fetched_nums.append(n_obj["num"])
            _remember_local_assignment(n_obj["num"], chat_id, service, country)
            n_obj["shares"] += 1
            n_obj["used_by"].append(chat_id)
            total_assigned_stats += 1
            increment_numbers_used(chat_id)
            if n_obj["shares"] >= bot_settings.get("num_share", 1):
                n_obj["to_remove"] = True
                used_numbers_list.append(n_obj["num"])

        for b_id in number_batches:
            number_batches[b_id]["numbers"] = [n for n in number_batches[b_id]["numbers"] if not n.get("to_remove")]
        save_db()

        if not fetched_nums:
            answer_callback(call["id"], "❌ You have already taken all numbers or stock is empty!", show_alert=True)
            if data.startswith("c_n_"): delete_message(chat_id, msg_id)
            return

        app_full_name, _ = get_service_info_html(service)
        emoji_id = "5337302974806922068"
        apps_db = bot_settings.get("premium_apps", {})
        for app_key, app_data in apps_db.items():
            if service.upper() == app_key or service.upper() in app_key or app_key in service.upper():
                if "id" in app_data:
                    emoji_id = app_data["id"]
                    break
        kb = [[{"text": f"{app_full_name}", "icon_custom_emoji_id": emoji_id, "callback_data": "ignore", "style": "success"}]]
        
        flags_db = bot_settings.get("premium_flags", {})
        for num in fetched_nums:
            _, iso = get_flag_and_code(num)
            display_num = f"+{num}" if not num.startswith("+") else num
            
            emoji_id = "5780471598922337683" # Default Flag
            for flag_code, flag_data in flags_db.items():
                if iso == flag_data.get("iso"):
                    if "id" in flag_data: emoji_id = flag_data["id"]
                    break
            kb.append([{"text": f"{display_num}", "icon_custom_emoji_id": emoji_id, "copy_text": {"text": display_num}, "style": "primary"}])
            
        kb.append([{"text": "Change Number", "icon_custom_emoji_id": "5465368548702446780", "callback_data": f"c_n_{service}_{country}", "style": "danger"},
                   {"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}])
        prefix_label = f"🔢 Prefix ON • {active_prefix}" if active_prefix else "🔢 Set Prefix"
        kb.append([{"text": prefix_label, "icon_custom_emoji_id": "5352862640592949843", "callback_data": "set_prefix", "style": "success"}])
                   
        c_btns = bot_settings["custom_messages"].get("get_number", {}).get("buttons", [])
        custom_button_texts = {str(b.get("text", "")).strip().lower() for b in c_btns if isinstance(b, dict)}
        for c_b in c_btns: 
            b_copy = c_b.copy()
            btn_text = str(b_copy.get("text", "")).strip().lower()
            # Keep the existing button appearance/text, but repair navigation callbacks.
            if btn_text == "back":
                b_copy["callback_data"] = "back_to_country"
                b_copy["style"] = "danger"
            elif btn_text in ("change country", "change service"):
                b_copy["text"] = "Change Service"
                b_copy["callback_data"] = "back_to_get_number"
                if "style" not in b_copy: b_copy["style"] = "primary"
            elif "style" not in b_copy:
                b_copy["style"] = "primary"
            kb.append([b_copy])

        # Add the navigation buttons if they are not already present in the custom GET NUMBER menu.
        if not ({"change country", "change service"} & custom_button_texts):
            kb.append([{"text": "Change Service", "icon_custom_emoji_id": "5318986077455795572", "callback_data": "back_to_get_number", "style": "primary"}])
        if "back" not in custom_button_texts:
            kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_country", "style": "danger"}])
        
        # Show the actual assigned numbers in the Number page instead of leaving
        # the message body as the generic "NEW NUMBER" placeholder.
        display_country, display_flag, _display_iso = _country_display(country)
        number_lines = [f"📱 <b>{str(service).upper()}</b>"]
        if display_country:
            number_lines.append(f"{display_flag + ' ' if display_flag else ''}<b>{html.escape(display_country)}</b>")
        for n in fetched_nums:
            dnum = f"+{n}" if not str(n).startswith("+") else str(n)
            number_lines.append(f"📞 <code>{html.escape(dnum)}</code>")
        text_numbers = "\n".join(number_lines)
        # সবসময় মেসেজ ইডিট করবে (Change Number করলেও নতুন মেসেজ আসবে না)
        try:
            edit_message(chat_id, msg_id, text_numbers, reply_markup={"inline_keyboard": kb})
            user_active_sessions[chat_id] = {"msg_id": msg_id, "nums": fetched_nums, "service": service, "country": country}
            if str(user_prefixes.get(chat_id, "")).strip():
                number_page_snapshots[chat_id] = {"msg_id": msg_id, "text": text_numbers, "reply_markup": {"inline_keyboard": [[dict(btn) for btn in row] for row in kb]}}
        except:
            # যদি মেসেজ ইডিট করা সম্ভব না হয় (যেমন অনেক আগের মেসেজ), তবে নতুন মেসেজ দিবে
            msg_res = send_message(chat_id, text_numbers, reply_markup={"inline_keyboard": kb})
            if msg_res and "result" in msg_res:
                user_active_sessions[chat_id] = {"msg_id": msg_res["result"]["message_id"], "nums": fetched_nums, "service": service, "country": country}
                if str(user_prefixes.get(chat_id, "")).strip():
                    number_page_snapshots[chat_id] = {"msg_id": msg_res["result"]["message_id"], "text": text_numbers, "reply_markup": {"inline_keyboard": [[dict(btn) for btn in row] for row in kb]}}

    elif data.startswith("wapp_") or data.startswith("wrej_"):
        # অ্যাডমিন চেক (User ID চেক করতে হবে)
        user_id_clicked = call["from"]["id"]
        if not is_admin(user_id_clicked):
            answer_callback(call["id"], "🚫 Only Bot Admins can process withdrawals!", show_alert=True)
            return
            
        action = "APPROVE" if data.startswith("wapp_") else "REJECT"
        req_id = data.replace("wapp_", "").replace("wrej_", "")
        
        if req_id not in pending_withdrawals:
            try:
                if os.path.exists(WITHDRAWALS_LOCAL_FILE):
                    with open(WITHDRAWALS_LOCAL_FILE, "r", encoding="utf-8") as f:
                        saved_w = json.load(f)
                    if req_id in saved_w and str(saved_w[req_id].get("status", "pending")).lower() == "pending":
                        pending_withdrawals[req_id] = saved_w[req_id]
            except Exception as e:
                print(f"[WITHDRAWAL] Request restore error: {e}")

        if req_id in pending_withdrawals:
            req_data = pending_withdrawals[req_id]
            u_id, amt = req_data["user_id"], req_data["amount"]
            num = req_data["number"]
            full_name = req_data.get("full_name", u_id)
            
            if action == "APPROVE" and len(num) >= 7:
                masked_num = f"{num[:4]}❖DXA❖{num[-3:]}"
            else:
                masked_num = num
            
            status_text = "APPROVED" if action == "APPROVE" else "REJECTED"
            emoji_icon_id = "5352694861990501856" if action == "APPROVE" else "5420130255174145507"
            new_text = f"🎙 <b>WITHDRAWAL {status_text}</b>\n\n👤 <b>USER:</b> <a href='tg://user?id={u_id}'>{full_name}</a>\n💳 <b>WITHDRAWAL:</b> {amt} TK\n🍏 <b>NUMBER:</b> <code>{masked_num}</code>\n🏦 <b>METHOD:</b> {req_data['method']}\n\n🧾 <b>REQ ID:</b> {req_id}\n👨‍⚖️ <b>PROCESSED BY ADMIN</b>"
            
            kb = {"inline_keyboard": [[{"text": status_text, "icon_custom_emoji_id": emoji_icon_id, "callback_data": "ignore", "style": "success" if action == "APPROVE" else "danger"}]]}
            edit_message(chat_id, msg_id, render_body_text(new_text), reply_markup=kb)
            
            if action == "REJECT":
                update_balance(u_id, amt) 
                send_message(u_id, render_body_text(f"❌ Your {amt} TK withdrawal request was rejected. Balance refunded."))
            else:
                send_message(u_id, render_body_text(f"{PEM['ok']} Your {amt} TK withdrawal request has been paid successfully!"))
            
            final_status = "approved" if action == "APPROVE" else "rejected"
            req_data["status"] = final_status
            req_data["processed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                with open(WITHDRAWALS_LOCAL_FILE, "r", encoding="utf-8") as f:
                    local_w = json.load(f)
            except Exception:
                local_w = {}
            local_w[req_id] = req_data
            try:
                with open(WITHDRAWALS_LOCAL_FILE, "w", encoding="utf-8") as f:
                    json.dump(local_w, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"[WITHDRAWAL] Status save error: {e}")

            if db:
                try: db.collection('withdrawals').document(req_id).update({"status": final_status, "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                except Exception as e: print(f"[WITHDRAWAL] Firestore status update error: {e}")
                
            del pending_withdrawals[req_id]
        else:
            answer_callback(call["id"], "❌ Request already processed!", show_alert=True)

# ==========================================
# Polling Loop
# ==========================================
def poll_otp_with_status(number_id, num_str, owner_id, api_key):
    headers = {"X-API-Key": api_key}
    for _ in range(150): # 150 * 4 seconds = 10 Minutes Polling
        try:
            res = requests.get(f"{STEX_BASE_URL}/api/v1/numbers/{number_id}/sms", headers=headers, timeout=10)
            data = res.json()
            if data.get("success") and data.get("otp"):
                otp = str(data["otp"])
                msg_text = data.get("message", f"Your code is {otp}")
                
                # 🌟 সম্পূর্ণ মেসেজ থেকে ড্যাশসহ বা বড় OTP খোঁজার ফিক্স
                extracted_otp = extract_otp_code(msg_text)
                if extracted_otp and len(extracted_otp) > len(otp):
                    otp = extracted_otp
                    
                # 🌟 Resolve the ACTUAL service attached to this OTP record.
                # Never use the API panel/provider name as the service.
                app_name = resolve_real_service(num_str, data.get("service", ""), msg_text)
                
                unique_id = f"POLL_{number_id}_{otp}"
                if unique_id not in processed_otps:
                    processed_otps.add(unique_id)
                    
                    char, iso = get_flag_and_code(num_str)
                    app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                    
                    global recent_traffic
                    current_time = time.time()
                    recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                    recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num_str, "time": current_time})
                    save_local_db()
                    
                    display_num = f"+{num_str}" if not str(num_str).startswith("+") else str(num_str)
                    masked = mask_number(display_num)
                    lang = detect_language(msg_text)
                    
                    display_msg = format_otp_forward_body(display_num, app_name, msg_text, language_hint)
                    
                    for fw in bot_settings.get("fw_groups", []):
                        send_message(fw["chat_id"], display_msg, reply_markup=build_otp_forward_keyboard(otp, fw))
                    
                    inbox_msg = render_body_text(f"╔═══════════════╗\n║ {prem_app_html} {get_flag_info_html(display_num)} {display_num} {lang}\n╚═══════════════╝")
                    inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
                    
                    reward = float(bot_settings.get("otp_reward", 0.0))
                    if reward > 0:
                        reward_ok, _, _, reward_err = update_balance(owner_id, reward)
                        if reward_ok:
                            inbox_msg = render_body_text(inbox_msg.replace("\n", "\n", 1) + f"\n\n💰 OTP Reward: {reward:g} TK")
                        else:
                            print(f"[OTP REWARD] Balance update failed for {owner_id}: {reward_err}")
                    
                    send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                    
                    try: increment_received_otps(owner_id, otp_number=display_num)
                    except Exception as e: print(f"[USER STATS] Poll OTP counter failed for {owner_id}: {e}")
                break
        except: pass
        time.sleep(4)

def voltx_console_listener():
    global recent_traffic, bot_settings
    seen_console_hits = set()
    last_auto_update = time.time()
    
    while True:
        try:
            if not bot_settings.get("voltx_on", True):
                time.sleep(4)
                continue
            voltx_keys = bot_settings.get("voltx_keys", [])
            if voltx_keys:
                api_key = voltx_keys[0]
                headers = {"mauthapi": api_key}
                res = requests.get(f"{VOLTX_BASE_URL}/console", headers=headers, timeout=10)
                data = res.json()
                
                if data.get("meta", {}).get("code") == 200 and data.get("data", {}).get("hits"):
                    current_time = time.time()
                    new_hits = False
                    
                    for hit in data["data"]["hits"]:
                        range_str = str(hit.get("range", "")).replace("X", "")
                        if len(range_str) > 9:
                            range_str = range_str[:9] # 9 ডিজিটের বেশি হলে প্রথম 9 ডিজিট নেবে
                        sid = str(hit.get("sid", "Unknown"))
                        msg = str(hit.get("message", ""))
                        hit_time = hit.get("time", current_time * 1000) / 1000.0
                        
                        unique_hit = f"{range_str}_{sid}_{hit.get('time', 0)}"
                        if unique_hit not in seen_console_hits and range_str:
                            seen_console_hits.add(unique_hit)
                            if len(seen_console_hits) > 2000: seen_console_hits.clear()
                            
                            char, iso = get_flag_and_code(range_str)
                            app_full_name, _ = get_service_info_html(sid, msg)
                            
                            recent_traffic.append({
                                "service": app_full_name,
                                "iso": iso,
                                "flag": char,
                                "number": f"{range_str}XXX", 
                                "time": hit_time,
                                "real_range": range_str
                            })
                            new_hits = True
                            
                    if new_hits:
                        recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= LIVE_ACCESS_DISPLAY_WINDOW]
                        save_local_db()
                        
                    # 🌟 Auto ADD and DELETE logic every 2 minutes (120 seconds)
                    if current_time - last_auto_update > 120:
                        last_auto_update = current_time
                        changed = False
                        
                        if "voltx_services" not in bot_settings: bot_settings["voltx_services"] = {}
                        if "voltx_search_countries" not in bot_settings: bot_settings["voltx_search_countries"] = []
                        
                        # --- ১. Auto ADD Logic ---
                        srv_counts = Counter(t["service"].upper() for t in recent_traffic if "real_range" in t)
                        top_srvs = [s for s, c in srv_counts.most_common(6)] # Top 6 Services
                        
                        for srv in top_srvs:
                            if srv not in bot_settings["voltx_services"]:
                                bot_settings["voltx_services"][srv] = {}
                                changed = True
                                
                            iso_counts = Counter(t["iso"] for t in recent_traffic if t.get("service", "").upper() == srv and "real_range" in t)
                            top_isos = [i for i, c in iso_counts.most_common(3)] # Top 3 Countries
                            
                            for iso in top_isos:
                                full_country_name = get_flag_info_html(iso, return_full_name=True).title()
                                if full_country_name not in bot_settings["voltx_services"][srv]:
                                    bot_settings["voltx_services"][srv][full_country_name] = []
                                    changed = True
                                    
                                rng_counts = Counter(t["real_range"] for t in recent_traffic if t.get("service", "").upper() == srv and t.get("iso") == iso and "real_range" in t)
                                top_rngs = [r for r, c in rng_counts.most_common(2)] # Top 2 Ranges
                                
                                for rng in top_rngs:
                                    if rng not in bot_settings["voltx_services"][srv][full_country_name]:
                                        bot_settings["voltx_services"][srv][full_country_name].append(rng)
                                        changed = True
                                        
                                    # 🌟 শুধুমাত্র ৩ ডিজিট কান্ট্রি কোড অ্যাড করবে
                                    country_code = rng[:3]
                                    if country_code not in bot_settings["voltx_search_countries"]:
                                        bot_settings["voltx_search_countries"].append(country_code)
                                        changed = True

                        # --- ২. Auto DELETE Logic (Only if NO traffic in the LAST 120 SECONDS) ---
                        services_to_remove = []
                        for srv, countries in list(bot_settings["voltx_services"].items()):
                            # চেক করবে গত ১২০ সেকেন্ডে কোনো ট্রাফিক আছে কি না
                            srv_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and "real_range" in t and current_time - t.get("time", 0) <= 120)
                            if srv_hit < 1:
                                services_to_remove.append(srv)
                                continue
                            
                            countries_to_remove = []
                            for country, ranges in list(countries.items()):
                                c_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and get_flag_info_html(t.get("iso"), return_full_name=True).title() == country and "real_range" in t and current_time - t.get("time", 0) <= 120)
                                if c_hit < 1:
                                    countries_to_remove.append(country)
                                    continue
                                
                                ranges_to_remove = []
                                for rng in ranges:
                                    r_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and t.get("real_range") == rng and current_time - t.get("time", 0) <= 120)
                                    if r_hit < 1: 
                                        ranges_to_remove.append(rng)
                                
                                for r in ranges_to_remove:
                                    ranges.remove(r)
                                    changed = True
                                    
                            for c in countries_to_remove:
                                del bot_settings["voltx_services"][srv][c]
                                changed = True
                                
                        for s in services_to_remove:
                            del bot_settings["voltx_services"][s]
                            changed = True
                            
                        if changed:
                            save_db()
                            
        except Exception as e:
            pass
        time.sleep(10)

def voltx_sms_listener():
    global processed_otps, recent_traffic, voltx_assigned_numbers
    while True:
        try:
            voltx_keys = bot_settings.get("voltx_keys", [])
            for api_key in voltx_keys:
                try:
                    headers = {"mauthapi": api_key}
                    res = requests.get(f"{VOLTX_BASE_URL}/success-otp", headers=headers, timeout=10)
                    resp_data = res.json()
                    
                    if resp_data.get("meta", {}).get("code") == 200 and "data" in resp_data and "otps" in resp_data["data"]:
                        for item in resp_data["data"]["otps"]:
                            num = str(item.get("number", "")).replace("+", "")
                            msg_text = str(item.get("message", ""))
                            language_hint = str(item.get("language", item.get("lang", "")) or "").strip()
                            otp = extract_otp_code(msg_text) or "CODE"
                            otp_id = str(item.get("otp_id", otp))
                            
                            # Prefer the actual service attached to the API record;
                            # SMS detection is used only as a fallback. Never show the
                            # provider/panel label such as "Voltx Service".
                            app_name = resolve_real_service(num, item.get("service", ""), msg_text)
                                
                            unique_id = f"VOLTX_{num}_{otp_id}"
                            
                            if unique_id not in processed_otps and num:
                                processed_otps.add(unique_id)
                                if len(processed_otps) > 5000: processed_otps.clear()
                                
                                char, iso = get_flag_and_code(num)
                                app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                                current_time = time.time()
                                
                                recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                                recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num, "time": current_time})
                                save_local_db()
                                
                                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                                masked = mask_number(display_num)
                                lang = detect_language(msg_text)
                                
                                lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
                                display_msg = format_otp_forward_body(display_num, app_name, msg_text, language_hint)
                                
                                for fw in bot_settings.get("fw_groups", []):
                                    send_message(fw["chat_id"], display_msg, reply_markup=build_otp_forward_keyboard(otp, fw))
                                    
                                owner_id = None
                                clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                
                                for uid, session_data in user_active_sessions.items():
                                    for act_num in session_data.get("nums", []):
                                        act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                            owner_id = uid
                                            break
                                    if owner_id: break
                                    
                                if not owner_id:
                                    local_assignment = _local_assignment_for_number(num)
                                    if local_assignment:
                                        local_owners = local_assignment.get("owners", []) or []
                                        owner_id = local_owners[0] if local_owners else None

                                if not owner_id:
                                    for vtx_n, n_owner in voltx_assigned_numbers.items():
                                        clean_vtx = str(vtx_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if clean_vtx == clean_api_num or (len(clean_vtx) >= 8 and clean_vtx.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_vtx[-8:])):
                                            owner_id = n_owner
                                            break
                                        
                                if owner_id:
                                    lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
                                    reward = float(bot_settings.get("otp_reward", 0.0))
                                    if reward > 0:
                                        reward_ok, _, _, reward_err = update_balance(owner_id, reward)
                                        reward_line = f"\n\n💰 OTP Reward: {reward:g} TK" if reward_ok else ""
                                        if not reward_ok:
                                            print(f"[OTP REWARD] Balance update failed for {owner_id}: {reward_err}")
                                    else:
                                        reward_line = ""
                                    inbox_msg = render_body_text(f"{get_flag_info_html(display_num)} {iso} | {prem_app_html} {display_num} | 💬 {lang_name}{reward_line}")
                                    inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
                                    
                                    send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                                    
                                    try: increment_received_otps(owner_id, otp_number=display_num)
                                    except: pass
                except: pass
        except: pass
        time.sleep(5)

def global_sms_listener():
    global processed_otps, recent_traffic, stex_assigned_numbers
    while True:
        try:
            stex_keys = bot_settings.get("stex_keys", [])
            for api_key in stex_keys:
                try:
                    headers = {"mauthapi": api_key}
                    res = requests.get(f"{STEX_BASE_URL}/success-otp", headers=headers, timeout=10)
                    resp_data = res.json()
                    
                    if resp_data.get("meta", {}).get("code") == 200 and "data" in resp_data and "otps" in resp_data["data"]:
                        for item in resp_data["data"]["otps"]:
                            num = str(item.get("number", "")).replace("+", "")
                            msg_text = str(item.get("message", ""))
                            language_hint = str(item.get("language", item.get("lang", "")) or "").strip()
                            otp = extract_otp_code(msg_text) or "CODE"
                            otp_id = str(item.get("otp_id", otp))
                            
                            # Resolve the actual app from SMS/assigned number/API metadata.
                            # Never display the provider name (e.g. "Stex Service") as the service.
                            app_name = resolve_real_service(num, item.get("service", ""), msg_text)
                            if not app_name:
                                app_name = ""
                                
                            unique_id = f"STEX_{num}_{otp_id}"
                            
                            if unique_id not in processed_otps and num:
                                processed_otps.add(unique_id)
                                if len(processed_otps) > 5000: processed_otps.clear()
                                
                                char, iso = get_flag_and_code(num)
                                app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                                current_time = time.time()
                                
                                recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                                recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num, "time": current_time})
                                save_local_db()
                                
                                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                                masked = mask_number(display_num)
                                lang = detect_language(msg_text)
                                
                                lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
                                display_msg = format_otp_forward_body(display_num, app_name, msg_text)
                                
                                for fw in bot_settings.get("fw_groups", []):
                                    send_message(fw["chat_id"], display_msg, reply_markup=build_otp_forward_keyboard(otp, fw))
                                    
                                owner_id = None
                                clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                
                                for uid, session_data in user_active_sessions.items():
                                    for act_num in session_data.get("nums", []):
                                        act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                            owner_id = uid
                                            break
                                    if owner_id: break
                                    
                                if not owner_id:
                                    local_assignment = _local_assignment_for_number(num)
                                    if local_assignment:
                                        local_owners = local_assignment.get("owners", []) or []
                                        owner_id = local_owners[0] if local_owners else None

                                if not owner_id:
                                    for stex_n, n_owner in stex_assigned_numbers.items():
                                        clean_stex = str(stex_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if clean_stex == clean_api_num or (len(clean_stex) >= 8 and clean_stex.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_stex[-8:])):
                                            owner_id = n_owner
                                            break
                                        
                                if owner_id:
                                    lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
                                    inbox_msg = render_body_text(f"{get_flag_info_html(display_num)} {iso} | {prem_app_html} {display_num} | 💬 {lang_name}")
                                    inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
                                    
                                    reward = float(bot_settings.get("otp_reward", 0.0))
                                    if reward > 0:
                                        reward_ok, _, _, reward_err = update_balance(owner_id, reward)
                                        if reward_ok:
                                            inbox_msg = render_body_text(inbox_msg + f"\n\n💰 OTP Reward: {reward:g} TK")
                                        else:
                                            print(f"[OTP REWARD] Balance update failed for {owner_id}: {reward_err}")
                                    
                                    send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                                    
                                    try: increment_received_otps(owner_id, otp_number=display_num)
                                    except Exception as e: print(f"[USER STATS] STEX OTP counter failed for {owner_id}: {e}")
                except: pass
        except: pass
        time.sleep(5)

def main():
    global BOT_USERNAME
    res = api_call("getMe")
    if res.get("ok"): BOT_USERNAME = res["result"]["username"]
    print(f"🤖 Bot is starting... @{BOT_USERNAME}")
    
    threading.Thread(target=panel_monitor_thread, daemon=True).start()
    threading.Thread(target=global_sms_listener, daemon=True).start()
    threading.Thread(target=voltx_sms_listener, daemon=True).start()
    threading.Thread(target=voltx_console_listener, daemon=True).start()
    print("📡 Background APIs & Global SMS Listener Started!")
    
    # 🌟 PRO-LEVEL FAST SYSTEM: 500 Workers Pool
    executor = ThreadPoolExecutor(max_workers=500)
    
    offset = None
    while True:
        try:
            updates = api_call(f"getUpdates?timeout=50&offset={offset}")
            if updates and "result" in updates:
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    if "message" in update: 
                        executor.submit(handle_message, update["message"])
                    elif "callback_query" in update: 
                        executor.submit(handle_callback, update["callback_query"])
        except Exception as e:
            time.sleep(2)

if __name__ == "__main__":
    main()    