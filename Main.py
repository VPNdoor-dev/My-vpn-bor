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
def init_db():
conn = sqlite3.connect("vpn_users.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
user_id INTEGER PRIMARY KEY,
has_trial INTEGER DEFAULT 0,
expires_at TEXT,
referred_by INTEGER
)
""")
conn.commit()
conn.close()
init_db()
def get_trial_days():
current_date = datetime.date.today()
deadline_date = datetime.date(2026, 10, 15)
if current_date <= deadline_date:
return 5
return 3
def add_user_days(user_id, days):
conn = sqlite3.connect("vpn_users.db")
cursor = conn.cursor()
cursor.execute("SELECT expires_at FROM users WHERE user_id = ?", (user_id,))
result = cursor.fetchone()
current_date = datetime.date.today()
if result and result[0]:
current_expires = datetime.datetime.strptime(result[0], "%Y-%m-%d").date()
if current_expires >= current_date:
new_expires = current_expires + datetime.timedelta(days=days)
else:
new_expires = current_date + datetime.timedelta(days=days)
else:
new_expires = current_date + datetime.timedelta(days=days)
cursor.execute("UPDATE users SET expires_at = ? WHERE user_id = ?", (new_expires.strftime("%Y-%m-%d"), user_id))
conn.commit()
conn.close()
return new_expires.strftime("%Y-%m-%d")
def check_user_status(user_id):
conn = sqlite3.connect("vpn_users.db")
cursor = conn.cursor()
cursor.execute("SELECT expires_at, has_trial FROM users WHERE user_id = ?", (user_id,))
result = cursor.fetchone()
conn.close()
if result and result[0]:
current_date = datetime.date.today()
expires_date = datetime.datetime.strptime(result[0], "%Y-%m-%d").date()
if expires_date >= current_date:
days_left = (expires_date - current_date).days
return f"🟢 Активна\n📅 Действует до: {result[0]}\n⏳ Осталось дней: {days_left}"
return "🔴 Не активна"
def get_total_users():
conn = sqlite3.connect("vpn_users.db")
cursor = conn.cursor()
cursor.execute("SELECT COUNT() FROM users")
count = cursor.fetchone()
cursor.execute("SELECT COUNT() FROM users WHERE has_trial = 1")
trials = cursor.fetchone()
conn.close()
return count[0], trials[0]
def get_happ_config():
try:
url = "vpngate.net"
response = requests.get(url, timeout=10)
lines = response.text.split("\n")
valid_ips = []
for line in lines:
if line.startswith("*") or line.startswith("#") or not line.strip():
continue
parts = line.split(",")
if len(parts) > 7:
valid_ips.append((parts[1], parts[2], parts[6]))
if valid_ips:
chosen = random.choice(valid_ips)
fake_password = "password123"
method_and_pass = f"chacha20-ietf-poly1305:{fake_password}"
b64_login = base64.b64encode(method_and_pass.encode("utf-8")).decode("utf-8")
happ_key = f"ss://{b64_login}@{chosen[0]}:{chosen[1]}#DoorVPN-{chosen[2]}"
return happ_key, chosen[2]
except Exception as e:
print(f"Ошибка парсинга серверов: {e}")
return None, None
def get_main_keyboard(user_id):
keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn_rates = types.KeyboardButton("📊 Тарифы и Оплата")
btn_status = types.KeyboardButton("📌 Моя подписка")
btn_ref = types.KeyboardButton("👥 Пригласить друга")
btn_help = types.KeyboardButton("💡 Инструкция")
btn_refresh = types.KeyboardButton("🔄 Обновить сервер")
btn_support = types.KeyboardButton("🆘 Тех. поддержка")
keyboard.add(btn_rates, btn_status)
keyboard.add(btn_ref, btn_refresh)
keyboard.add(btn_help, btn_support)
if user_id == ADMIN_ID:
keyboard.add(types.KeyboardButton("⚙️ Админ-панель"))
return keyboard
@bot.message_handler(commands=["start"])
def send_welcome(message):
user_id = message.from_user.id
text_parts = message.text.split()
referrer_id = None
if len(text_parts) > 1:
try:
referrer_id = int(text_parts[1])
if referrer_id == user_id:
referrer_id = None
except ValueError:
pass
conn = sqlite3.connect("vpn_users.db")
cursor = conn.cursor()
cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
user_exists = cursor.fetchone()
if not user_exists:
cursor.execute("INSERT INTO users (user_id, referred_by) VALUES (?, ?)", (user_id, referrer_id))
conn.commit()
if referrer_id:
add_user_days(referrer_id, 1)
try:
bot.send_message(referrer_id, f"🎉 По вашей реферальной ссылке зарегистрировался новый пользователь! Вам начислен 1 день премиум-подписки.", parse_mode="Markdown")
except Exception:
pass
conn.close()
welcome_text = f"👋 Привет, {message.from_user.first_name}! Добро пожаловать в Door VPN.\n\n🛡 Door VPN — это премиум-сервис нового поколения. Мы обеспечиваем анонимность, защиту данных и доступ к ресурсам на максимальной скорости.\n\n🚀 Сервера идеально подходят для приложения Happ.\n\nУправляйте защитой через меню ниже 👇"
try:
bot.send_photo(message.chat.id, IMAGE_URL, caption=welcome_text, reply_markup=get_main_keyboard(user_id), parse_mode="Markdown")
except Exception:
bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard(user_id), parse_mode="Markdown")
@bot.message_handler(content_types=["text"])
def handle_text(message):
user_id = message.from_user.id
if message.text == "📊 Тарифы и Оплата":
days = get_trial_days()
markup = types.InlineKeyboardMarkup()
markup.add(types.InlineKeyboardButton(f"🎁 Пробный период — {days} Дней (Бесплатно)", callback_data="buy_trial"))
markup.add(types.InlineKeyboardButton("🚀 1 Месяц — 50 ⭐", callback_data="buy_1m"), types.InlineKeyboardButton("🔥 3 Месяца — 120 ⭐", callback_data="buy_3m"))
markup.add(types.InlineKeyboardButton("💥 6 Месяцев — 220 ⭐", callback_data="buy_6m"), types.InlineKeyboardButton("👑 1 Год — 400 ⭐", callback_data="buy_1y"))
markup.add(types.InlineKeyboardButton("♾ НАВСЕГДА (Безлимит) — 1000 ⭐", callback_data="buy_inf"))
text = "✨ Тарифные планы Door VPN\n\n🟢 Состояние сети: Стабильное\n⚡ Скорость узлов: до 1 Гбит/с\n\nВыберите тариф для мгновенного получения доступа в Happ:"
bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
elif message.text == "📌 Моя подписка":
status = check_user_status(user_id)
bot.send_message(message.chat.id, f"👤 Профиль Door VPN:\n\nID: {user_id}\nСтатус подписки:\n{status}", parse_mode="Markdown")
elif message.text == "👥 Пригласить друга":
bot_info = bot.get_me()
ref_link = f"t.me{bot_info.username}?start={user_id}"
ref_text = f"🎁 Реферальная программа Door VPN\n\nПриглашайте друзей и пользуйтесь VPN бесплатно! За каждого друга, который запустит бота по вашей ссылке, вы мгновенно получите +1 день к вашей подписки.\n\n🔗 Ваша личная ссылка для приглашений:\n{ref_link}\n\nПросто скопируйте её и отправьте друзьям!"
bot.send_message(message.chat.id, ref_text, parse_mode="Markdown")
elif message.text == "🔄 Обновить сервер":
bot.send_message(message.chat.id, "🔄 Поиск наиболее свободного узла Door VPN...")
key, country = get_happ_config()
if key:
text = f"✅ Локация успешно изменена!\n📍 Новый сервер: {country}\n\nСкопируйте новый ключ и добавьте в Happ:\n\n{key}"
bot.send_message(message.chat.id, text, parse_mode="Markdown")
else:
bot.send_message(message.chat.id, "❌ Не удалось переключить сервер. Попробуйте позже.")
elif message.text == "💡 Инструкция":
instructions = "⚙️ Инструкция по настройке через Happ:\n\n1️⃣ Скачайте приложение Happ:\n• Для iPhone (App Store)\n• Для Android (Google Play)\n\n2️⃣ Скопируйте персональный код (начинается с ss://), который выдал бот.\n\n3️⃣ Откройте Happ. Приложение само обнаружит ключ. Нажмите кнопку «Поехали».\n\n4️⃣ Выберите сервер DoorVPN и нажмите круглую кнопку включения по центру экрана. Готово! 🚀"
bot.send_message(message.chat.id, instructions, parse_mode="Markdown", disable_web_page_preview=True)
elif message.text == "🆘 Тех. поддержка":
markup = types.InlineKeyboardMarkup()
markup.add(types.InlineKeyboardButton("👨‍💻 Написать администратору", url=f"t.me{ADMIN_USERNAME}"))
bot.send_message(message.chat.id, "🤝 Возникли проблемы? Наша служба поддержки всегда на связи. Нажмите кнопку ниже:", reply_markup=markup)
elif message.text in ["⚙️ Admin-панель", "⚙️ Админ-панель"] and user_id == ADMIN_ID:
markup = types.InlineKeyboardMarkup()
btn_stats = types.InlineKeyboardButton("📈 Статистика", callback_data="admin_stats")
btn_give_trial = types.InlineKeyboardButton("🎫 Выдать ручной доступ", callback_data="admin_give_trial")
markup.add(btn_stats, btn_give_trial)
bot.send_message(message.chat.id, "🔒 Панель Администратора:", reply_markup=markup)
@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def handle_admin_callbacks(call):
if call.from_user.id != ADMIN_ID: return
bot.answer_callback_query(call.id)
if call.data == "admin_stats":
total, trials = get_total_users()
bot.send_message(call.message.chat.id, f"📊 Статистика Door VPN:\n\n👥 Всего уникальных пользователей: {total}\n🎁 Активировано бесплатных тестов: {trials}")
elif call.data == "admin_give_trial":
key, country = get_happ_config()
if key:
bot.send_message(call.message.chat.id, f"🎁 Админ-ключ создан (Локация: {country}):\n\n{key}", parse_mode="Markdown")
@bot.callback_query_handler(func=lambda call: call.data in ["buy_trial", "buy_1m", "buy_3m", "buy_6m", "buy_1y", "buy_inf"])
def process_payment(call):
bot.answer_callback_query(call.id)
user_id = call.from_user.id
conn = sqlite3.connect("vpn_users.db")
cursor = conn.cursor()
cursor.execute("SELECT has_trial FROM users WHERE user_id = ?", (user_id,))
res = cursor.fetchone()
has_trial = res[0] if res else 0
conn.close()
if call.data == "buy_trial":
if has_trial == 1:
bot.send_message(call.message.chat.id, "❌ Вы уже активировали пробный период ранее!")
return
days = get_trial_days()
bot.send_message(call.message.chat.id, "⏳ Выделяю приватную линию для Door VPN...")
key, country = get_happ_config()
if key:
conn = sqlite3.connect("vpn_users.db")
cursor = conn.cursor()
cursor.execute("UPDATE users SET has_trial = 1 WHERE user_id = ?", (user_id,))
conn.commit()
conn.close()
add_user_days(user_id, days)
trial_text = f"🎉 Ваш бесплатный доступ на {days} дней успешно активирован!\n📍 Локация: {country}\n\nНажмите на код ниже, чтобы скопировать его:\n\n{key}"
bot.send_message(call.message.chat.id, trial_text, parse_mode="Markdown")
return
tariff_map = {"buy_1m": ("1 месяц", 50, 30), "buy_3m": ("3 месяца", 120, 90), "buy_6m": ("6 месяцев", 220, 180), "buy_1y": ("1 год", 400, 365), "buy_inf": ("НАВСЕГДА", 1000, 9999)}
name, price, days = tariff_map[call.data]
prices = [types.LabeledPrice(label="Telegram Stars", amount=price)]
bot.send_invoice(call.message.chat.id, title=f"Door VPN — {name}", description=f"Премиум-доступ на {name}", invoice_payload=f"vpn_sub_{days}", provider_token="", currency="XTR", prices=prices, start_parameter="vpn-sub")
@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout(pre_checkout_query):
bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
@bot.message_handler(content_types=["successful_payment"])
def process_successful_payment(message):
payload = message.successful_payment.invoice_payload
days = int(payload.split("_")[-1])
user_id = message.from_user.id
add_user_days(user_id, days)
bot.send_message(message.chat.id, "⏳ Оплата принята! Подключаю сервера...")
key, country = get_happ_config()
if key:
thank_text = f"🎉 Оплата успешно завершена! Благодарим за выбор Door VPN!\n\n🔑 Ваш премиум-код для Happ (Локация: {country}):\n\n{key}"
bot.send_message(message.chat.id, thank_text, parse_mode="Markdown")
print("Сервер Door VPN успешно запущен...")
bot.infinity_polling()
