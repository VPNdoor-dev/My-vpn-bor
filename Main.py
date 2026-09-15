import os, requests, random, base64, sqlite3, datetime, telebot; from telebot import types
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "potato_xd0")
IMAGE_URL = "https://i.imgur.com/EQKdqpl.png"
bot = telebot.TeleBot(TOKEN)
conn = sqlite3.connect("vpn_users.db"); cursor = conn.cursor(); cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, has_trial INTEGER DEFAULT 0, expires_at TEXT, referred_by INTEGER)"); conn.commit(); conn.close()
get_trial_days = lambda: 5 if datetime.date.today() <= datetime.date(2026, 10, 15) else 3
get_total_users = lambda: (lambda c, cur: (cur.execute("SELECT COUNT(*) FROM users"), (lambda tot: (cur.execute("SELECT COUNT(*) FROM users WHERE has_trial = 1"), (lambda tr: (c.close(), tot, tr))(cur.fetchone())))(cur.fetchone())))(sqlite3.connect("vpn_users.db"), sqlite3.connect("vpn_users.db").cursor())
check_trial = lambda uid: (lambda c, cur: (cur.execute("SELECT has_trial FROM users WHERE user_id = ?", (uid,)), (lambda res: (c.close(), res if res else 0))(cur.fetchone())))(sqlite3.connect("vpn_users.db"), sqlite3.connect("vpn_users.db").cursor())
set_trial_used = lambda uid: (lambda c, cur: (cur.execute("UPDATE users SET has_trial = 1 WHERE user_id = ?", (uid,)), c.commit(), c.close()))(sqlite3.connect("vpn_users.db"), sqlite3.connect("vpn_users.db").cursor())
add_user_days = lambda uid, days: (lambda c, cur: (cur.execute("SELECT expires_at FROM users WHERE user_id = ?", (uid,)), (lambda res: (lambda n_exp: (cur.execute("UPDATE users SET expires_at = ? WHERE user_id = ?", (n_exp.strftime("%Y-%m-%d"), uid)), c.commit(), c.close(), n_exp.strftime("%Y-%m-%d")))((datetime.datetime.strptime(res, "%Y-%m-%d").date() if res and res else datetime.date.today()) + datetime.timedelta(days=days) if (datetime.datetime.strptime(res, "%Y-%m-%d").date() if res and res else datetime.date.today()) >= datetime.date.today() else datetime.date.today() + datetime.timedelta(days=days)))((cur.fetchone())))(sqlite3.connect("vpn_users.db"), sqlite3.connect("vpn_users.db").cursor()))
check_user_status = lambda uid: (lambda c, cur: (cur.execute("SELECT expires_at FROM users WHERE user_id = ?", (uid,)), (lambda res: (c.close(), f"🟢 Активна\n📅 До: {res}\n⏳ Осталось: {(datetime.datetime.strptime(res, '%Y-%m-%d').date() - datetime.date.today()).days} дн." if res and res and datetime.datetime.strptime(res, '%Y-%m-%d').date() >= datetime.date.today() else "🔴 Не активна"))(cur.fetchone())))(sqlite3.connect("vpn_users.db"), sqlite3.connect("vpn_users.db").cursor())
get_main_keyboard = lambda uid: (lambda m: (m.add(types.KeyboardButton("📊 Тарифы и Оплата"), types.KeyboardButton("📌 Моя подписка")), m.add(types.KeyboardButton("👥 Пригласить друга"), types.KeyboardButton("💡 Инструкция")), m.add(types.KeyboardButton("🔄 Обновить сервер"), types.KeyboardButton("🆘 Тех. поддержка")), m.add(types.KeyboardButton("⚙️ Админ-панель")) if uid == ADMIN_ID else None, m))(types.ReplyKeyboardMarkup(resize_keyboard=True))
def get_happ_config():
 try:
  url = "http://vpngate.net"; resp = requests.get(url, timeout=10); lines = resp.text.split("\n"); ips = [line.split(",") for line in lines if not line.startswith("*") and not line.startswith("#") and line.strip() and len(line.split(",")) > 7]
  if ips:
   ch = random.choice(ips); m = "chacha20-ietf-poly1305:password123"; b64 = base64.b64encode(m.encode("utf-8")).decode("utf-8"); key = f"ss://{b64}@{ch}:{ch}#DoorVPN-{ch}"
   return key, ch
 except Exception as e: print(f"Ошибка: {e}")
 return None, None
@bot.message_handler(commands=["start"])
def start(m):
 uid = m.from_user.id; parts = m.text.split(); ref_id = int(parts) if len(parts) > 1 and parts.isdigit() and int(parts) != uid else None; conn = sqlite3.connect("vpn_users.db"); cursor = conn.cursor(); cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (uid,)); ex = cursor.fetchone()
 if not ex:
  cursor.execute("INSERT INTO users (user_id, referred_by) VALUES (?, ?)", (uid, ref_id)); conn.commit()
  if ref_id:
   add_user_days(ref_id, 1)
   try: bot.send_message(ref_id, "🎉 По вашей ссылке зашел друг! Вам начислен **1 день** подписки.", parse_mode="Markdown")
   except Exception: pass
 conn.close(); t = f"👋 Привет, {m.from_user.first_name}! Добро пожаловать в **Door VPN**.\n\n🛡 Премиум-сервис нового поколения для приложения **Happ**.\n\nУправляйте подпиской через меню 👇"
 try: bot.send_photo(m.chat.id, IMAGE_URL, caption=t, reply_markup=get_main_keyboard(uid), parse_mode="Markdown")
 except Exception: bot.send_message(m.chat.id, t, reply_markup=get_main_keyboard(uid), parse_mode="Markdown")
@bot.message_handler(content_types=["text"])
def text(m):
 uid = m.from_user.id
 if m.text == "📊 Тарифы и Оплата":
  markup = types.InlineKeyboardMarkup(); markup.add(types.InlineKeyboardButton(f"🎁 Тест — {get_trial_days()} Дн.", callback_data="buy_trial")); markup.add(types.InlineKeyboardButton("🚀 1 Мес — 50 ⭐", callback_data="buy_1m"), types.InlineKeyboardButton("🔥 3 Мес — 120 ⭐", callback_data="buy_3m")); markup.add(types.InlineKeyboardButton("💥 6 Мес — 220 ⭐", callback_data="buy_6m"), types.InlineKeyboardButton("👑 1 Год — 400 ⭐", callback_data="buy_1y")); markup.add(types.InlineKeyboardButton("♾ НАВСЕГДА — 1000 ⭐", callback_data="buy_inf"))
  bot.send_message(m.chat.id, "✨ **Тарифные планы Door VPN**\n\nВыберите тариф для автоматического получения доступа в Happ:", reply_markup=markup, parse_mode="Markdown")
 if m.text == "📌 Моя подписка": bot.send_message(m.chat.id, f"👤 **Профиль Door VPN:**\n\nID: `{uid}`\nСтатус подписки:\n{check_user_status(uid)}", parse_mode="Markdown")
 if m.text == "👥 Пригласить друга": bot.send_message(m.chat.id, f"🎁 **Рефералы**\n\nЗа каждого друга вы получите **+1 день** подписки.\n\n🔗 Ссылка:\n`https://t.me{bot.get_me().username}?start={uid}`", parse_mode="Markdown")
 if m.text == "🔄 Обновить сервер":
  bot.send_message(m.chat.id, "🔄 Ищу новый свободный узел..."); key, country = get_happ_config()
  if key: bot.send_message(m.chat.id, f"✅ **Локация изменена!**\n📍 Страна: {country}\n\n`{key}`", parse_mode="Markdown")
  else: bot.send_message(m.chat.id, "❌ Ошибка. Попробуйте позже.")
 if m.text == "💡 Инструкция": bot.send_message(m.chat.id, "⚙️ **Настройка Happ:**\n\n1️⃣ Скачайте Happ из App Store или Google Play.\n2️⃣ Скопируйте ключ `ss://` из бота.\n3️⃣ Откройте Happ, нажмите «Поехали».\n4️⃣ Включите круглую кнопку по центру. 🚀", parse_mode="Markdown")
 if m.text == "🆘 Тех. поддержка": m_up = types.InlineKeyboardMarkup(); m_up.add(types.InlineKeyboardButton("👨‍💻 Написать", url=f"https://t.me{ADMIN_USERNAME}")); bot.send_message(m.chat.id, "🤝 Служба поддержки sempre на связи:", reply_markup=m_up)
 if m.text in ["⚙️ Admin-панель", "⚙️ Админ-панель"] and uid == ADMIN_ID: markup = types.InlineKeyboardMarkup(); markup.add(types.InlineKeyboardButton("📈 Статистика", callback_data="admin_stats"), types.InlineKeyboardButton("🎫 Выдать ручной доступ", callback_data="admin_give_trial")); bot.send_message(m.chat.id, "🔒 Панель Администратора:", reply_markup=markup)
@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def admin_cb(call):
 if call.from_user.id != ADMIN_ID: return
 bot.answer_callback_query(call.id)
 if call.data == "admin_stats": total, trials = get_total_users(); bot.send_message(call.message.chat.id, f"📊 Статистика:\n\nЮзеров: {total}\nТестов: {trials}")
 if call.data == "admin_give_trial":
  key, country = get_happ_config()
  if key: bot.send_message(call.message.chat.id, f"🎁 Ключ ({country}):\n\n`{key}`", parse_mode="Markdown")
@bot.callback_query_handler(func=lambda call: call.data in ["buy_trial", "buy_1m", "buy_3m", "buy_6m", "buy_1y", "buy_inf"])
def payment_cb(call):
 bot.answer_callback_query(call.id); uid = call.from_user.id; trial_status = check_trial(uid)
 if call.data == "buy_trial":
  if trial_status == 1: bot.send_message(call.message.chat.id, "❌ Вы уже брали бесплатный тест!"); return
  days = get_trial_days(); bot.send_message(call.message.chat.id, "⏳ Создаю линию..."); key, country = get_happ_config()
  if key: set_trial_used(uid); add_user_days(uid, days); bot.send_message(call.message.chat.id, f"🎉 Доступ на {days} дней активирован!\n📍 Страна: {country}\n\n`{key}`", parse_mode="Markdown")
  return
 t_map = {"buy_1m": ("1 мес", 50, 30), "buy_3m": ("3 мес", 120, 90), "buy_6m": ("6 мес", 220, 180), "buy_1y": ("1 год", 400, 365), "buy_inf": ("Навсегда", 1000, 9999)}; name, price, d = t_map[call.data]; prices = [types.LabeledPrice(label="Telegram Stars", amount=price)]
 bot.send_invoice(call.message.chat.id, title=f"Door VPN — {name}", description="Личный премиум-доступ Happ", invoice_payload=f"vpn_sub_{d}", provider_token="", currency="XTR", prices=prices, start_parameter="vpn-sub")
@bot.pre_checkout_query_handler(func=lambda query: True)
def precheck(q): bot.answer_pre_checkout_query(q.id, ok=True)
@bot.message_handler(content_types=["successful_payment"])
def success_pay(message):
 p = message.successful_payment.invoice_payload; d = int(p.split("_")[-1]); uid = message.from_user.id; add_user_days(uid, d); bot.send_message(message.chat.id, "⏳ Оплата принята! Подключаю сервера..."); key, country = get_happ_config()
 if key: bot.send_message(message.chat.id, f"🎉 Оплата успешна!\n🔑 Ключ ({country}):\n\n`{key}`", parse_mode="Markdown")
print("Запуск...")
bot.infinity_polling()
