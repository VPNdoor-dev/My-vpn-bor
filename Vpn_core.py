import os
import json
import base64
import requests

DB_FILE = "db.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"users": {}}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def init_user(user_id, username=""):
    db = load_db()
    u_id = str(user_id)
    if u_id not in db["users"]:
        db["users"][u_id] = {
            "username": username or "Premium User",
            "status": "🔴 Не активна",
            "days_left": 0,
            "referrals": 0,
            "has_test": False
        }
        save_db(db)
    return db["users"][u_id]

def get_free_servers():
    urls = [
        "https://githubusercontent.com",
        "https://githubusercontent.com"
    ]
    raw_servers = []
    for url in urls:
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                try:
                    decoded = base64.b64decode(res.text).decode('utf-8')
                    lines = decoded.splitlines()
                except Exception:
                    lines = res.text.splitlines()
                for line in lines:
                    line = line.strip()
                    if line.startswith(("ss://", "vless://", "vmess://")):
                        raw_servers.append(line)
        except Exception:
            continue
            
    raw_servers = list(set(raw_servers))
    formatted_servers = []
    countries = ["Германия 🇩🇪", "Нидерланды 🇳🇱", "Франция 🇫🇷", "США 🇺🇸", "Япония 🇯🇵", "Сингапур 🇸🇬"]
    
    for i, server in enumerate(raw_servers[:20]):
        country = countries[i % len(countries)]
        base_part = server.split("#")[0]
        formatted_servers.append(f"{base_part}#DoorVPN | {country} N{i+1}")
        
    return formatted_servers
