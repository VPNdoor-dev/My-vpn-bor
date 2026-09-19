import os
import base64
from datetime import datetime
from flask import Flask, request
import telebot
from telebot.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    ReplyKeyboardMarkup, 
    KeyboardButton
)
from vpn_core import load_db, save_db, init_user, get_free_servers

BOT_TOKEN = "8789477182:AAEGulR-MpJ206pFeQ512DE32iRNcL3nD20"
APP_URL = "https://onrender.com"
ADMIN_ID = 5606075763

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)
admin_states = {}

@app.route('/sub/<user_id>')
def generate_subscription(user_id):
    db = load_db()
    user_data = db["users"].get(str(user_id))
    if not user_data or user_data["status"] == "🔴 Не активна":
        return "Нет активной подписки!", 403
    servers = get_free_servers()
    if not servers:
        return "Серверы недоступны", 404
    sub_text = "\n".join(servers)
    b64_sub = base64.b64encode(sub_text.encode('utf-8')).decode('utf-8')
    return b64_sub, 200, {'Content-Type': 'text/plain; charset=utf-8'}

def get_main_keyboard(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("✨ Тарифы и Оплата"), KeyboardButton("📌 Инструкция"))
    markup.row(KeyboardButton("👤 Моя подписка"), KeyboardButton("👥 Пригласить друга"))
    markup.row(KeyboardButton("🔄 Обновить server"), KeyboardButton("🆘 Тех. поддержка"))
    if user_id == ADMIN_ID:
        markup.row(KeyboardButton("⚙️ Админ-панель"))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    init_user(user_id, message.from_user.username)
    args = message.text.split()
    if len(args) > 1:
        ref_id = args[1].strip()
        db = load_db()
        if ref_id in db["users"] and ref_id != str(user_id):
            db["users"][ref_id]["referrals"] += 1
            db["users"][ref_id]["days_left"] += 2
            db["users"][ref_id]["status"] = "🟢 Активна"
            save_db(db)
            try:
                bot.send_message(int(ref_id), "🎉 Реферал! +2 дня подписки.")
            except:
                pass
    welcome_text = "🚪 **Добро пожаловать в Door VPN (Happ)!**"
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=get_main_keyboard(user_id))

@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    user_id = message.from_user.id
    text = message.text
    user_data = init_user(user_id, message.from_user.username)

    if text == "✨ Тарифы и Оплата":
        cur_date = datetime.now()
        tar_date = datetime(2026, 10, 19)
        days = 5 if cur_date >= tar_date else 7
        msg = "✨ **Тарифные планы Happ:**"
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton(f"🎁 Тест — {days} Дн.", callback_data="buy_test"))
        markup.add(InlineKeyboardButton("🚀 1 Мес — 50 ⭐️", callback_data="buy_1m"), InlineKeyboardButton("🔥 3 Мес — 85 ⭐️", callback_data="buy_3m"))
        markup.add(InlineKeyboardButton("💥 6 Мес — 150 ⭐️", callback_data="buy_6m"), InlineKeyboardButton("👑 1 Год — 250 ⭐️", callback_data="buy_1y"))
        markup.add(InlineKeyboardButton("♾ НАВСЕГДА — 500 ⭐️", callback_data="buy_forever"))
        bot.send_message(message.chat.id, msg, parse_mode="Markdown", reply_markup=markup)

    elif text == "👤 Моя подписка":
        msg = f"👤 **Профиль:**\n\nID: `{user_id}`\nСтатус: {user_data['status']}\nОсталось дней: `{user_data['days_left']}`\nДрузей: `{user_data['referrals']}`"
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")

    elif text == "👥 Пригласить друга":
        ref_link = f"https://t.me{user_id}"
        bot.send_message(message.chat.id, f"🎁 **Рефералы (+2 дня):**\n\n🔗 {ref_link}", disable_web_page_preview=True)

    elif text == "📌 Инструкция":
        msg = "⚙️ **Настройка Happ:**\n\n1️⃣ Нажмите 'Обновить server' и скопируйте ссылку.\n2️⃣ Вставьте её в Happ."
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")

    elif text == "🆘 Тех. поддержка":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("💬 Поддержка", url="tg://resolve?domain=potato_xd0"))
        bot.send_message(message.chat.id, "Связаться с разработчиком:", reply_markup=markup)

    elif text == "🔄 Обновить server":
        if user_data["status"] == "🔴 Не активна":
            bot.send_message(message.chat.id, "❌ Активируйте тест в разделе 'Тарифы'!")
            return
        bot.send_message(message.chat.id, f"✅ **Ссылка обновлена!**\n\n`{APP_URL}/sub/{user_id}`", parse_mode="Markdown")

    elif text == "⚙️ Админ-панель" and user_id == ADMIN_ID:
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton("📈 Статс", callback_data="admin_stats"), InlineKeyboardButton("🎫 Выдать", callback_data="admin_give"))
        markup.add(InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast"), InlineKeyboardButton("❌ Забрать", callback_data="admin_revoke"))
        bot.send_message(message.chat.id, "🔒 **Админка:**", reply_markup=markup)

    elif user_id == ADMIN_ID and admin_states.get(user_id) == "waiting_for_id":
        admin_states[user_id] = f"waiting_for_days:{message.text.strip()}"
        bot.send_message(message.chat.id, "🔢 Введите количество дней подписки:")

    elif user_id == ADMIN_ID and str(admin_states.get(user_id, "")).startswith("waiting_for_days:"):
        parts = admin_states[user_id].split(":")
        t_id = parts[1]
        try:
            days = int(message.text.strip())
        except:
            days = 30
        admin_states[user_id] = None
        db = load_db()
        if t_id in db["users"]:
            db["users"][t_id]["status"] = "🟢 Активна"
            db["users"][t_id]["days_left"] += days
            save_db(db)
            bot.send_message(message.chat.id, f"✅ Пользователю {t_id} добавлено {days} дней!")
            try:
                bot.send_message(int(t_id), f"🎉 Подписка продлена на {days} дней!")
            except:
                pass
        else:
            bot.send_message(message.chat.id, "❌ Пользователь не найден.")

    elif user_id == ADMIN_ID and admin_states.get(user_id) == "waiting_for_revoke_id":
        t_id = message.text.strip()
        admin_states[user_id] = None
        db = load_db()
        if t_id in db["users"]:
            db["users"][t_id]["status"] = "🔴 Не активна"
            db["users"][t_id]["days_left"] = 0
            save_db(db)
            bot.send_message(message.chat.id, f"❌ Подписка {t_id} аннулирована.")

    elif user_id == ADMIN_ID and admin_states.get(user_id) == "waiting_for_broadcast":
        admin_states[user_id] = None
        db = load_db()
        count = 0
        for uid in db["users"]:
            try:
                bot.send_message(int(uid), message.text)
                count += 1
            except:
                pass
        bot.send_message(message.chat.id, f"📢 Рассылка завершена для {count} человек.")

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    if call.data == "buy_test":
        bot.answer_callback_query(call.id)
        db = load_db()
        u_id = str(user_id)
        if db["users"][u_id]["has_test"]:
            bot.send_message(call.message.chat.id, "❌ Вы уже брали тест.")
        else:
            cur_date = datetime.now()
            tar_date = datetime(2026, 10, 19)
            test_days = 5 if cur_date >= tar_date else 7
            db["users"][u_id]["has_test"] = True
            db["users"][u_id]["days_left"] = test_days
            db["users"][u_id]["status"] = "🟢 Активна"
            save_db(db)
            bot.send_message(call.message.chat.id, f"🎉 **Тест на {test_days} дней активирован!**")
            
    elif call.data == "admin_give" and user_id == ADMIN_ID:
        bot.answer_callback_query(call.id)
        admin_states[user_id] = "waiting_for_id"
        bot.send_message(call.message.chat.id, "✍️ **Введи ID:**")
        
    elif call.data == "admin_revoke" and user_id == ADMIN_ID:
        bot.answer_callback_query(call.id)
        admin_states[user_id] = "waiting_for_revoke_id"
        bot.send_message(call.message.chat.id, "✍️ **Введи ID для блокировки:**")
        
    elif call.data == "admin_broadcast" and user_id == ADMIN_ID:
        bot.answer_callback_query(call.id)
        admin_states[user_id] = "waiting_for_broadcast"
        bot.send_message(call.message.chat.id, "✍️ Введите текст рассылки:")
        
    elif call.data == "admin_stats" and user_id == ADMIN_ID:
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"📊 Пользователей: {len(load_db()['users'])}")
        
    elif call.data.startswith("buy_"):
        bot.answer_callback_query(call.id, "Отладка платежей.", show_alert=True)

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
