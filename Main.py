import os
import requests
import random
import base64
import sqlite3
import datetime
import telebot
from telebot import types
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "potato_xd0")
IMAGE_URL = "https://i.imgur.com/EQKdqpl.png"
bot = telebot.TeleBot(TOKEN)
conn = sqlite3.connect("vpn_users.db"); cursor = conn.cursor(); cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, has_trial INTEGER DEFAULT 0, expires_at TEXT, referred_by INTEGER)"); conn.commit(); conn.close()
get_trial_days = lambda: 5 if datetime.date.today() <= datetime.date(2026, 10, 15) else 3
def add_user_days(user_id, days):
conn = sqlite3.connect("vpn_users.db"); cursor = conn.cursor(); cursor.execute("SELECT expires_at FROM users WHERE user_id = ?", (user_id,)); res = cursor.fetchone(); curr = datetime.date.today()
new_exp = (datetime.datetime.strptime(res[0], "%Y-%m-%d").date() if res and res[0] else curr) + datetime.timedelta(days=days) if (datetime.datetime.strptime(res[0], "%Y-%m-%d").date() if res and res[0] else curr) >= curr else curr + datetime.timedelta(days=days)
cursor.execute("UPDATE users SET expires_at = ? WHERE user_id = ?", (new_exp.strftime("%Y-%m-%d"), user_id)); conn.commit(); conn.close(); return new_exp.strftime("%Y-%m-%d")
def check_user_status(user_id):
conn = sqlite3.connect("vpn_users.db"); cursor = conn.cursor(); cursor.execute("SELECT expires_at FROM users WHERE user_id = ?", (user_id,)); res = cursor.fetchone(); conn.close()
if res and res[0]:
exp = datetime.datetime.strptime(res[0], "%Y-%m-%d").date()
if exp >= datetime.date.today(): return f"🟢 Активна\n📅 До: {res[0]}\n⏳ Осталось: {(exp - datetime.date.today()).days} дн."
return "🔴 Не активна"
def check_trial(user_id): conn = sqlite3.connect("vpn_users.db"); cursor = conn.cursor(); cursor.execute("SELECT has_trial FROM users WHERE user_id = ?", (user_id,)); res = cursor.fetchone(); conn.close(); return res[0] if res else 0
def set_trial_used(user_id): conn = sqlite3.connect("vpn_users.db"); cursor = conn.cursor(); cursor.execute("UPDATE users SET has_trial = 1 WHERE user_id = ?", (user_id,)); conn.commit(); conn.close()
def get_total_users(): conn = sqlite3.connect("vpn_users.db"); cursor = conn.cursor(); cursor.execute("SELECT COUNT() FROM users"); total = cursor.fetchone(); cursor.execute("SELECT COUNT() FROM users WHERE has_trial = 1"); trials = cursor.fetchone(); conn.close(); return total, trials
def get_happ_config():
try:
url = "vpngate.net"; resp = requests.get(url, timeout=10); lines = resp.text.split("\n"); ips = [line.split(",") for line in lines if not line.startswith("*") and not line.startswith("#") and line.strip() and len(line.split(",")) > 7]
if ips:
ch = random.choice(ips); m = "chacha20-ietf-poly1305:password123"; b64 = base64.b64encode(m.encode("utf-8")).decode("utf-8"); key = f"ss://{b64}@{ch[1]}:{ch[2]}#DoorVPN-{ch[6]}"
return key, ch[6]
except Exception as e: print(f"Ошибка: {e}")
return None, None
def get_main_keyboard(user_id):
markup = types.ReplyKeyboardMarkup(resize_keyboard=True); markup.add(types.KeyboardButton("📊 Тарифы и Оплата"), types.KeyboardButton("📌 Моя подписка")); markup.add(types.KeyboardButton("👥 Пригласить друга"), types.KeyboardButton("💡 Инструкция")); markup.add(types.KeyboardButton("🔄 Обновить сервер"), types.KeyboardButton("🆘 Тех. поддержка"))
if user_id == ADMIN_ID: markup.add(types.KeyboardButton("⚙️ Админ-панель"))
return markup
@bot.message_handler(commands=["start"])
def send_welcome(message):
uid = message.from_user.id; parts = message.text.split(); ref_id = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() and int(parts[1]) != uid else None; conn = sqlite3.connect("vpn_users.db"); cursor = conn.cursor(); cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (uid,)); exists = cursor.fetchone()
if not exists:
cursor.execute("INSERT INTO users (user_id, referred_by) VALUES (?, ?)", (uid, ref_id)); conn.commit()
if ref_id:
add_user_days(ref_id, 1)
try: bot.send_message(ref_id, "🎉 По вашей ссылке зашел друг! Вам начислен 1 день подписки.", parse_mode="Markdown")
except Exception: pass
conn.close(); w_text = f"👋 Привет, {message.from_user.first_name}! Добро пожаловать в Door VPN.\n\n🛡 Премиум-сервис нового поколения. Мы обеспечиваем скорость и защиту.\n\nУправляйте подпиской через меню 👇"
try: bot.send_photo(message.chat.id, IMAGE_URL, caption=w_text, reply_markup=get_main_keyboard(uid), parse_mode="Markdown")
catch Exception: bot.send_message(message.chat.id, w_text, reply_markup=get_main_keyboard(uid), parse_mode="Markdown")
@bot.message_handler(content_types=["text"])
def handle_text(message):
uid = message.from_user.id
if message.text == "📊 Тарифы и Оплата":
days = get_trial_days(); m = types.InlineKeyboardMarkup(); m.add(types.InlineKeyboardButton(f"🎁 Тест — {days} Дн.", callback_data="buy_trial")); m.add(types.InlineKeyboardButton("🚀 1 Мес — 50 ⭐", callback_data="buy_1m"), types.InlineKeyboardButton("🔥 3 Мес — 120 ⭐", callback_data="buy_3m")); m.add(types.InlineKeyboardButton("💥 6 Мес — 220 ⭐", callback_data="buy_6m"), types.InlineKeyboardButton("👑 1 Год — 400 ⭐", callback_data="buy_1y")); m.add(types.InlineKeyboardButton("♾ НАВСЕГДА — 1000 ⭐", callback_data="buy_inf")); t = "✨ Тарифы Door VPN\n\nВыберите тариф для Happ:"
bot.send_message(message.chat.id, t, reply_markup=m, parse_mode="Markdown")
elif message.text == "📌 Моя подписка": bot.send_message(message.chat.id, f"👤 Профиль:\n\nID: {uid}\n{check_user_status(uid)}", parse_mode="Markdown")
elif message.text == "👥 Пригласить друга": link = f"t.me{bot.get_me().username}?start={uid}"; bot.send_message(message.chat.id, f"🎁 Рефералы\n\nЗа друга вы получите +1 день подписки.\n\n🔗 Ссылка:\n{link}", parse_mode="Markdown")
elif message.text == "🔄 Обновить сервер":
bot.send_message(message.chat.id, "🔄 Ищу новый свободный узел..."); key, country = get_happ_config()
if key: bot.send_message(message.chat.id, f"✅ Локация изменена!\n📍 Страна: {country}\n\n{key}", parse_mode="Markdown")
else: bot.send_message(message.chat.id, "❌ Ошибка. Попробуйте позже.")
elif message.text == "💡 Инструкция": bot.send_message(message.chat.id, "⚙️ Настройка Happ:\n\n1️⃣ Скачайте Happ из App Store или Google Play.\n2️⃣ Скопируйте ключ ss:// из бота.\n3️⃣ Откройте Happ, нажмите «Поехали».\n4️⃣ Включите круглую кнопку по центру. 🚀", parse_mode="Markdown")
elif message.text == "🆘 Тех. поддержка": m = types.InlineKeyboardMarkup(); m.add(types.InlineKeyboardButton("👨‍💻 Написать", url=f"t.me{ADMIN_USERNAME}")); bot.send_message(message.chat.id, "🤝 Служба поддержки:", reply_markup=m)
elif message.text in ["⚙️ Admin-панель", "⚙️ Админ-панель"] and uid == ADMIN_ID: m = types.InlineKeyboardMarkup(); m.add(types.InlineKeyboardButton("📈 Статистика", callback_data="admin_stats"), types.InlineKeyboardButton("🎫 Выдать доступ", callback_data="admin_give_trial")); bot.send_message(message.chat.id, "🔒 Админка:", reply_markup=m)
@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def handle_admin_callbacks(call):
if call.from_user.id != ADMIN_ID: return
bot.answer_callback_query(call.id)
if call.data == "admin_stats": total, trials = get_total_users(); bot.send_message(call.message.chat.id, f"📊 Статистика:\n\nЮзеров: {total[0]}\nТестов: {trials[0]}")
elif call.data == "admin_give_trial":
key, country = get_happ_config()
if key: bot.send_message(call.message.chat.id, f"🎁 Ключ ({country}):\n\n{key}", parse_mode="Markdown")
@bot.callback_query_handler(func=lambda call: call.data in ["buy_trial", "buy_1m", "buy_3m", "buy_6m", "buy_1y", "buy_inf"])
def process_payment(call):
bot.answer_callback_query(call.id); uid = call.from_user.id; trial_status = check_trial(uid)
if call.data == "buy_trial":
if trial_status == 1: bot.send_message(call.message.chat.id, "❌ Вы уже брали тест!"); return
days = get_trial_days(); bot.send_message(call.message.chat.id, "⏳ Создаю линию..."); key, country = get_happ_config()
if key: set_trial_used(uid); add_user_days(uid, days); bot.send_message(call.message.chat.id, f"🎉 Доступ на {days} дней активирован!\n📍 Страна: {country}\n\n{key}", parse_mode="Markdown")
return
t_map = {"buy_1m": ("1 мес", 50, 30), "buy_3m": ("3 мес", 120, 90), "buy_6m": ("6 мес", 220, 180), "buy_1y": ("1 год", 400, 365), "buy_inf": ("Навсегда", 1000, 9999)}; name, price, d = t_map[call.data]; prices = [types.LabeledPrice(label="Telegram Stars", amount=price)]
bot.send_invoice(call.message.chat.id, title=f"Door VPN — {name}", description="Премиум-доступ", invoice_payload=f"vpn_sub_{d}", provider_token="", currency="XTR", prices=prices, start_parameter="vpn-sub")
@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout(pre_checkout_query): bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
@bot.message_handler(content_types=["successful_payment"])
def process_successful_payment(message):
p = message.successful_payment.invoice_payload; d = int(p.split("_")[-1]); uid = message.from_user.id; add_user_days(uid, d); bot.send_message(message.chat.id, "⏳ Подключаю сервера..."); key, country = get_happ_config()
if key: bot.send_message(message.chat.id, f"🎉 Оплата успешна!\n🔑 Ключ ({country}):\n\n{key}", parse_mode="Markdown")
print("Запуск...")
bot.infinity_polling()
