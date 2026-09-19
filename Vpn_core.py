import os, json, base64, requests

DB_FILE = "db.json"

def load_db():
    if not os.path.exists(DB_FILE): return {"users": {}, "banned": []}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)
            if "banned" not in db: db["banned"] = []
            return db
    except: return {"users": {}, "banned": []}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def init_user(user_id, username=""):
    db = load_db()
    u_id = str(user_id)
    uname = str(username).lower().replace("@", "") if username else ""
    if u_id not in db["users"]:
        db["users"][u_id] = {
            "username": uname,
            "status": "🔴 Не активна",
            "days_left": 0,
            "referrals": 0,
            "has_test": False
        }
        save_db(db)
    elif uname and db["users"][u_id].get("username") != uname:
        db["users"][u_id]["username"] = uname
        save_db(db)
    return db["users"][u_id]

def find_user_by_input(user_input):
    clean = str(user_input).strip().lower().replace("@", "")
    db = load_db()
    if clean.isdigit() and clean in db["users"]: return clean
    for uid, data in db["users"].items():
        if data.get("username") == clean: return uid
    return None

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
                try: lines = base64.b64decode(res.text).decode('utf-8').splitlines()
                except: lines = res.text.splitlines()
                for line in lines:
                    line = line.strip()
                    if line.startswith(("ss://", "vless://", "vmess://")): raw_servers.append(line)
        except: continue
            
    raw_servers = list(set(raw_servers))
    formatted_servers = []
    countries = ["Германия 🇩🇪", "Нидерланды 🇳🇱", "Франция 🇫🇷", "США 🇺🇸", "Япония 🇯🇵"]
    
    if raw_servers:
        # Самый первый и мощный узел делаем личным сервером короны
        first_node = raw_servers[0].split("#")[0]
        formatted_servers.append(f"{first_node}#Ваш Личный Сервер 👑")
    
    for i, server in enumerate(raw_servers[1:20]):
        country = countries[i % len(countries)]
        base_part = server.split("#")[0]
        formatted_servers.append(f"{base_part}#DoorVPN | {country} N{i+1}")
        
    return formatted_servers
