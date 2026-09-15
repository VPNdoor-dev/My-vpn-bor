import os, requests, random, base64, sqlite3, datetime, telebot, threading
from telebot import types
from http.server import BaseHTTPRequestHandler, HTTPServer
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
ADMIN_USER = os.getenv("ADMIN_USERNAME", "potato_xd0").replace("@", "")
IMG = "https://postimg.cc"
bot = telebot.TeleBot(TOKEN)
DB = "vpn_users.db"
class HealthCheck(BaseHTTPRequestHandler):
 def do_GET(self):
  self.send_response(200)
  self.send_header("Content-type", "text/plain")
  self.end_headers()
  self.wfile.write(b"OK")
def run_health_server():
 port = int(os.getenv("PORT", "10000"))
 try:
  server = HTTPServer(("0.0.0.0", port), HealthCheck)
  server.serve_forever()
 except: pass
def init_db():
 conn = sqlite3.connect(DB)
 cur = conn.cursor()
 cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, has_trial INTEGER DEFAULT 0, expires_at TEXT, referred_by INTEGER)")
 conn.commit()
 conn.close()
init_db()
def get_trial_days():
 t = datetime.date.today()
 lim = datetime.date(2026, 10, 15)
 return 5 if t <= lim else 3
def get_total_users():
 conn = sqlite3.connect(DB)
 cur = conn.cursor()
 cur.execute("SELECT COUNT(*) FROM users")
 tot = cur.fetchone()
 cur.execute("SELECT COUNT(*) FROM users WHERE has_trial = 1")
 tr = cur.fetchone()
 conn.close()
 return tot, tr
def check_trial(uid):
 conn = sqlite3.connect(DB)
 cur = conn.cursor()
 cur.execute("SELECT has_trial FROM users WHERE user_id = ?", (uid,))
 res = cur.fetchone()
 conn.close()
 return res if res else 0
def set_trial_used(uid):
 conn = sqlite3.connect(DB)
 cur = conn.cursor()
 cur.execute("UPDATE users SET has_trial = 1 WHERE user_id = ?", (uid,))
 conn.commit()
 conn.close()
def add_user_days(uid, days):
 conn = sqlite3.connect(DB)
 cur = conn.cursor()
 cur.execute("SELECT expires_at FROM users WHERE user_id = ?", (uid,))
 res = cur.fetchone()
 td = datetime.date.today()
 if res and res:
  try:
   c_exp = datetime.datetime.strptime(res, "%Y-%m-%d").date()
   base = c_exp if c_exp >= td else td
  except: base = td
 else: base = td
 n_exp = base + datetime.timedelta(days=days)
 n_exp_str = n_exp.strftime("%Y-%m-%d")
 cur.execute("UPDATE users SET expires_at = ? WHERE user_id = ?", (n_exp_str, uid))
 conn.commit()
 conn.close()
 return n_exp_str
def check_user_status(uid):
 conn = sqlite3.connect(DB)
 cur = conn.cursor()
 cur.execute("SELECT expires_at FROM users WHERE user_id = ?", (uid,))
 res = cur.fetchone()
 conn.close()
 if res and res:
  try:
   exp = datetime.datetime.strptime(res, "%Y-%m-%d").date()
   if exp >= datetime.date.today():
    dl = (exp - datetime.date.today()).days
    return f"🟢 Активна\n📅 До: {res}\n⏳ Осталось: {dl} дн."
  except: pass
 return "🔴 Не активна"
def get_main_keyboard(uid):
 m = types.ReplyKeyboardMarkup(resize_keyboard=True)
 m.add(types.KeyboardButton("📊 Тарифы и Оплата"), types.KeyboardButton("📌 Моя подписка"))
 m.add(types.KeyboardButton("👥 Пригласить друга"), types.KeyboardButton("💡 Инструкция"))
 m.add(types.KeyboardButton("🔄 Обновить сервер"), types.KeyboardButton("🆘 Тех. поддержка"))
 if uid == ADMIN_ID: m.add(types.KeyboardButton("⚙️ Админ-панель"))
 return m
def get_happ_config():
 try:
  url = "http://vpngate.net"
  resp = requests.get(url, timeout=(3, 4))
  lines = resp.text.split("\n")
  ips = []
  for line in lines:
   if not line.startswith("*") and not line.startswith("#") and line.strip():
    p = line.split(",")
    if len(p) > 7: ips.append(p)
  if ips:
   ip_line = random.choice(ips)
   ip = ip_line if len(ip_line) > 1 else "127.0.0.1"
   m = "chacha20-ietf-poly1305:password123"
   b64 = base64.b64encode(m.encode("utf-8")).decode("utf-8")
   return f"ss://{b64}@{ip}:443#DoorVPN-{ip}", ip
 except Exception as e: print(f"Ошибка: {e}")
 return None, None
@bot.message_handler(commands=["start"])
def start(m):
 uid = m.from_user.id
 p = m.text.split()
 ref_id = None
 if len(p) > 1 and p.isdigit():
  p_ref = int(p)
  if p_ref != uid: ref_id = p_ref
 conn = sqlite3.connect(DB)
 cursor = conn.cursor()
 cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (uid,))
 ex = cursor.fetchone()
 if not ex:
  cursor.execute("INSERT INTO users (user_id, referred_by) VALUES (?, ?)", (uid, ref_id))
  conn.commit()
  if ref_id:
   add_user_days(ref_id, 1)
   try: bot.send_message(ref_id, "🎉 Друг зашел по ссылке! +1 день подписки.", parse_mode="Markdown")
   except: pass
 conn.close()
 t = f"👋 Привет, {m.from_user.first_name}!\nДобро пожаловать в **Door VPN**.\n\n🛡 Премиум-сервис для **Happ**.\nУправляйте меню 👇"
 kb = get_main_keyboard(uid)
 try: bot.send_photo(m.chat.id, IMG, caption=t, reply_markup=kb, parse_mode="Markdown")
 except: bot.send_message(m.chat.id, t, reply_markup=kb, parse_mode="Markdown")
@bot.message_handler(content_types=["text"])
def text_handler(m):
 uid = m.from_user.id
 if m.text == "📊 Тарифы и Оплата":
  markup = types.InlineKeyboardMarkup()
  td = get_trial_days()
  markup.add(types.InlineKeyboardButton(f"🎁 Тест — {td} Дн.", callback_data="buy_trial"))
  markup.add(types.InlineKeyboardButton("🚀 1 Мес — 50 ⭐", callback_data="buy_1m"), types.InlineKeyboardButton("🔥 3 Мес — 120 ⭐", callback_data="buy_3m"))
  markup.add(types.InlineKeyboardButton("💥 6 Мес — 220 ⭐", callback_data="buy_6m"), types.InlineKeyboardButton("👑 1 Год — 400 ⭐", callback_data="buy_1y"))
  markup.add(types.InlineKeyboardButton("♾ НАВСЕГДА — 1000 ⭐", callback_data="buy_inf"))
  bot.send_message(m.chat.id, "✨ **Тарифные планы**\n\nВыберите тариф для Happ:", reply_markup=markup, parse_mode="Markdown")
 elif m.text == "📌 Моя подписка":
  status = check_user_status(uid)
  bot.send_message(m.chat.id, f"👤 **Профиль:**\n\nID: `{uid}`\nСтатус:\n{status}", parse_mode="Markdown")
 elif m.text == "👥 Пригласить друга":
  name = bot.get_me().username
  bot.send_message(m.chat.id, f"🎁 **Рефералы**\n\nЗа друга: **+1 день**.\n\n🔗 Ссылка:\n`https://t.me{name}?start={uid}`", parse_mode="Markdown")
 elif m.text == "🔄 Обновить сервер":
  bot.send_message(m.chat.id, "🔄 Ищу узел...")
  key, country = get_happ_config()
  if key: bot.send_message(m.chat.id, f"✅ **Узел изменен!**\n📍 Узел: {country}\n\n`{key}`", parse_mode="Markdown")
  else: bot.send_message(m.chat.id, "❌ Попробуйте позже.")
 elif m.text == "💡 Инструкция":
  bot.send_message(m.chat.id, "⚙️ **Настройка Happ:**\n\n1️⃣ Скачайте приложение Happ.\n2️⃣ Скопируйте ключ `ss://`.\n3️⃣ Вставьте ключ в Happ. 🚀", parse_mode="Markdown")
 elif m.text == "🆘 Тех. поддержка":
  m_up = types.InlineKeyboardMarkup()
  m_up.add(types.InlineKeyboardButton("👨‍💻 Написать", url=f"https://t.me{ADMIN_USER}"))
  bot.send_message(m.chat.id, "🤝 Поддержка на связи:", reply_markup=m_up)
 elif m.text in ["⚙️ Admin-панель", "⚙️ Админ-панель"] and uid == ADMIN_ID:
  markup = types.InlineKeyboardMarkup()
  markup.add(types.InlineKeyboardButton("📈 Статистика", callback_data="admin_stats"), types.InlineKeyboardButton("🎫 Выдать доступ", callback_data="admin_give_trial"))
  bot.send_message(m.chat.id, "🔒 Панель Администратора:", reply_markup=markup)
@bot.callback_query_handler(func=lambda c: c.data.startswith("admin_"))
def admin_cb(call):
 if call.from_user.id != ADMIN_ID: return
 bot.answer_callback_query(call.id)
 if call.data == "admin_stats":
  total, trials = get_total_users()
  bot.send_message(call.message.chat.id, f"📊 Статистика:\n\nЮзеров: {total}\nТестов: {trials}")
 elif call.data == "admin_give_trial":
  bot.send_message(call.message.chat.id, "🔄 Генерация ключа...")
  key, country = get_happ_config()
  if key: bot.send_message(call.message.chat.id, f"🎁 Ключ ({country}):\n\n`{key}`", parse_mode="Markdown")
  else: bot.send_message(call.message.chat.id, "❌ Ошибка получения узла.")
@bot.callback_query_handler(func=lambda c: c.data in ["buy_trial", "buy_1m", "buy_3m", "buy_6m", "buy_1y", "buy_inf"])
def payment_cb(call):
 bot.answer_callback_query(call.id)
 uid = call.from_user.id
 trial_status = check_trial(uid)
 if call.data == "buy_trial":
  if trial_status == 1:
   bot.send_message(call.message.chat.id, "❌ Вы уже брали тест!")
   return
  days = get_trial_days()
  bot.send_message(call.message.chat.id, "⏳ Создаю линию...")
  key, country = get_happ_config()
  if key:
   set_trial_used(uid)
   add_user_days(uid, days)
   bot.send_message(call.message.chat.id, f"🎉 Тест на {days} дн.!\n📍 Узел: {country}\n\n`{key}`", parse_mode="Markdown")
  else: bot.send_message(call.message.chat.id, "❌ Ошибка создания линии.")
  return
 t_map = {"buy_1m": ("1 мес", 50, 30), "buy_3m": ("3 мес", 120, 90), "buy_6m": ("6 мес", 220, 180), "buy_1y": ("1 год", 400, 365), "buy_inf": ("Навсегда", 1000, 9999)}
 name, price, d = t_map[call.data]
 prices = [types.LabeledPrice(label="Telegram Stars", amount=price)]
 bot.send_invoice(call.message.chat.id, title=f"Door VPN — {name}", description="Премиум Happ", invoice_payload=f"vpn_{d}", provider_token="", currency="XTR", prices=prices, start_parameter="vpn-sub")
@bot.pre_checkout_query_handler(func=lambda query: True)
def precheck(q): bot.answer_pre_checkout_query(q.id, ok=True)
@bot.message_handler(content_types=["successful_payment"])
def success_pay(message):
 p = message.successful_payment.invoice_payload
 d = int(p.split("_")[-1])
 uid = message.from_user.id
 add_user_days(uid, d)
 bot.send_message(message.chat.id, "⏳ Подключаю...")
 key, country = get_happ_config()
 if key: bot.send_message(message.chat.id, f"🎉 Успешно!\n🔑 Ключ ({country}):\n\n`{key}`", parse_mode="Markdown")
print("Бот запущен...")
threading.Thread(target=run_health_server, daemon=True).start()
bot.infinity_polling()
