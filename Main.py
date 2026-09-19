import os, base64, telebot
from datetime import datetime
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from vpn_core import load_db, save_db, init_user, get_free_servers

BOT_TOKEN = "8789477182:AAEGulR-MpJ206pFeQ512DE32iRNcL3nD20"
APP_URL = "https://onrender.com"
ADMIN_ID = 5606075763
LOGO_URL = "https://imgur.com"

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)
admin_states = {}

@app.route('/sub/<user_id>')
def generate_subscription(user_id):
    user_data = load_db()["users"].get(str(user_id))
    if not user_data or user_data["status"] == "🔴 Не активна":
        return "Нет активной подписки!", 403
    servers = get_free_servers()
    if not servers: return "Серверы недоступны", 404
    b64_sub = base64.b64encode("\n".join(servers).encode('utf-8')).decode('utf-8')
    return b64_sub, 200, {'Content-Type': 'text/plain; charset=utf-8'}

def get_main_keyboard(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("✨ Тарифы и Оплата"), KeyboardButton("📌 Инструкция"))
    markup.row(KeyboardButton("👤 Моя подписка"), KeyboardButton("👥 Пригласить друга"))
    markup.row(KeyboardButton("🔄 Обновить сервер"), KeyboardButton("🆘 Тех. поддержка"))
    if user_id == ADMIN_ID: markup.row(KeyboardButton("⚙️ Админ-панель"))
    return markup

def send_tariffs_menu(chat_id):
    days = 5 if datetime.now() >= datetime(2026, 10, 19) else 7
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton(f"🎁 Тест — {days} Дн.", callback_data="buy_test"))
    markup.add(InlineKeyboardButton("🚀 1 Мес — 50 ⭐️", callback_data="buy_1m"), InlineKeyboardButton("🔥 3 Мес — 85 ⭐️", callback_data="buy_3m"))
    markup.add(InlineKeyboardButton("💥 6 Мес — 150 ⭐️", callback_data="buy_6m"), InlineKeyboardButton("👑 1 Год — 250 ⭐️", callback_data="buy_1y"))
    markup.add(InlineKeyboardButton("♾ НАВСЕГДА — 500 ⭐️", callback_data="buy_forever"))
    bot.send_message(chat_id, "✨ **Тарифные планы Happ:**", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    init_user(user_id, message.from_user.username)
    args = message.text.split()
    if len(args) > 1 and args.strip() != str(user_id):
        db = load_db()
        if args.strip() in db["users"]:
            db["users"][args.strip()]["referrals"] += 1
            db["users"][args.strip()]["days_left"] += 2
            db["users"][args.strip()]["status"] = "🟢 Активна"
            save_db(db)
            try: bot.send_message(int(args.strip()), "🎉 Реферал! +2 дня подписки.")
            except: pass
            
    welcome_text = "Добро Пожаловать В Door🚪VPN\nУ Нас Есть:\nПробная Подписка 7 Дней 🤩\nЛичный Выделенный Сервер Под Каждого👀\nСамые Низкие Цены🔥\n\nОформить подписку👇:"
    inline_markup = InlineKeyboardMarkup().add(InlineKeyboardButton("✨ Оформить подписку", callback_data="open_tariffs"))
    try: bot.send_photo(message.chat.id, LOGO_URL, caption=welcome_text, reply_markup=inline_markup)
    except: bot.send_message(message.chat.id, welcome_text, reply_markup=inline_markup)
    bot.send_message(message.chat.id, "Используйте меню внизу для навигации:", reply_markup=get_main_keyboard(user_id))

@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    user_id = message.from_user.id
    text = message.text
    user_data = init_user(user_id, message.from_user.username)

    if text == "✨ Тарифы и Оплата": send_tariffs_menu(message.chat.id)
    elif text == "👤 Моя подписка":
        bot.send_message(message.chat.id, f"👤 **Профиль:**\n\nID: `{user_id}`\nСтатус: {user_data['status']}\nОсталось дней: `{user_data['days_left']}`\nДрузей: `{user_data['referrals']}`", parse_mode="Markdown")
    elif text == "👥 Пригласить друга":
        bot.send_message(message.chat.id, f"🎁 **Рефералы (+2 дня):**\n\n🔗 https://t.me{user_id}", disable_web_page_preview=True)
    elif text == "📌 Инструкция":
        bot.send_message(message.chat.id, "⚙️ **Настройка Happ:**\n\n1️⃣ Нажмите 'Обновить сервер' и скопируйте ссылку.\n2️⃣ Вставьте её в Happ.", parse_mode="Markdown")
    elif text == "🆘 Тех. поддержка":
        bot.send_message(message.chat.id, "Связаться с разработчиком:", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("💬 Поддержка", url="tg://resolve?domain=potato_xd0")))
    elif text == "🔄 Обновить сервер":
        if user_data["status"] == "🔴 Не активна":
            bot.send_message(message.chat.id, "❌ Активируйте тест в разделе '✨ Тарифы и Оплата'!")
            return
        bot.send_message(message.chat.id, f"✅ **Ссылка обновлена!**\n\n`{APP_URL}/sub/{user_id}`", parse_mode="Markdown")
    elif text == "⚙️ Админ-панель" and user_id == ADMIN_ID:
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton("📈 Статс", callback_data="admin_stats"), InlineKeyboardButton("🎫 Выдать", callback_data="admin_give"))
        markup.add(InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast"), InlineKeyboardButton("❌ Забрать", callback_data="admin_revoke"))
        bot.send_message(message.chat.id, "🔒 **Админка:**", reply_markup=markup)
    elif user_id == ADMIN_ID and admin_states.get(user_id) == "waiting_for_id":
        admin_states[user_id] = f"waiting_for_days:{text.strip()}"
        bot.send_message(message.chat.id, "🔢 Введите количество дней подписки:")
    elif user_id == ADMIN_ID and str(admin_states.get(user_id, "")).startswith("waiting_for_days:"):
        t_id = admin_states[user_id].split(":")[1]
        try: days = int(text.strip())
        except: days = 30
        admin_states[user_id] = None
        db = load_db()
        if t_id in db["users"]:
            db["users"][t_id]["status"] = "🟢 Активна"
            db["users"][t_id]["days_left"] += days
            save_db(db)
            bot.send_message(message.chat.id, f"✅ Пользователю {t_id} добавлено {days} дней!")
            try: bot.send_message(int(t_id), f"🎉 Подписка продлена на {days} дней!")
            except: pass
        else: bot.send_message(message.chat.id, "❌ Пользователь не найден.")
    elif user_id == ADMIN_ID and admin_states.get(user_id) == "waiting_for_revoke_id":
        admin_states[user_id] = None
        db = load_db()
        if text.strip() in db["users"]:
            db["users"][text.strip()]["status"] = "🔴 Не активна"
            db["users"][text.strip()]["days_left"] = 0
            save_db(db)
            bot.send_message(message.chat.id, f"❌ Подписка {text.strip()} аннулирована.")
    elif user_id == ADMIN_ID and admin_states.get(user_id) == "waiting_for_broadcast":
        admin_states[user_id] = None
        count = 0
        for uid in load_db()["users"]:
            try: bot.send_message(int(uid), text); count += 1
            except: pass
        bot.send_message(message.chat.id, f"📢 Рассылка завершена для {count} человек.")

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    if call.data == "open_tariffs":
        bot.answer_callback_query(call.id)
        send_tariffs_menu(call.message.chat.id)
    elif call.data == "buy_test":
        bot.answer_callback_query(call.id)
        db = load_db()
        if db["users"][str(user_id)]["has_test"]:
            bot.send_message(call.message.chat.id, "❌ Вы уже брали тест.")
        else:
            days = 5 if datetime.now() >= datetime(2026, 10, 19) else 7
            db["users"][str(user_id)].update({"has_test": True, "days_left": days, "status": "🟢 Активна"})
            save_db(db)
            bot.send_message(call.message.chat.id, f"🎉 **Тест на {days} дней активирован!**")
    elif call.data in ["admin_give", "admin_revoke", "admin_broadcast"] and user_id == ADMIN_ID:
        bot.answer_callback_query(call.id)
        modes = {"admin_give": ("waiting_for_id", "✍️ **Введи ID:**"), "admin_revoke": ("waiting_for_revoke_id", "✍️ **Введи ID для блокировки:**"), "admin_broadcast": ("waiting_for_broadcast", "✍️ Введите текст рассылки:")}
        admin_states[user_id] = modes[call.data][0]
        bot.send_message(call.message.chat.id, modes[call.data][1])
    elif call.data == "admin_stats" and user_id == ADMIN_ID:
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"📊 Пользователей: {len(load_db()['users'])}")
    elif call.data.startswith("buy_"):
        bot.answer_callback_query(call.id, "Оплата в режиме отладки.", show_alert=True)

@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode('utf-8'))])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL + '/' + BOT_TOKEN)
    return "Бот запущен!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
