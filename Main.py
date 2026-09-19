import os
from datetime import datetime
from flask import Flask, request
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
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
    if not user_data or user_data["status"] == "🔴 Не active":
        return "У вас нет активной подписки. Активируйте её в боте!", 403
    servers = get_free_servers()
    if not servers:
        return "Серверы временно недоступны", 404
    subscription_text = "\n".join(servers)
    b64_subscription = base64.b64encode(subscription_text.encode('utf-8')).decode('utf-8')
    return b64_subscription, 200, {'Content-Type': 'text/plain; charset=utf-8'}

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
        referrer_id = args[1]
        db = load_db()
        if referrer_id in db["users"] and referrer_id != str(user_id):
            db["users"][referrer_id]["referrals"] += 1
            db["users"][referrer_id]["days_left"] += 2
            db["users"][referrer_id]["status"] = "🟢 Активна"
            save_db(db)
            try: bot.send_message(int(referrer_id), "🎉 По вашей ссылке зашел новый друг! Вам начислено +2 дня подписки.")
            except: pass
            
    welcome_text = "🚪 **Добро пожаловать в Door VPN (Happ)!**\n\nИспользуйте меню ниже для управления подпиской."
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=get_main_keyboard(user_id))

@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    user_id = message.from_user.id
    text = message.text
    user_data = init_user(user_id, message.from_user.username)

    if text == "✨ Тарифы и Оплата":
        current_date = datetime.now()
        target_date = datetime(2026, 10, 19)
        days_count = 5 if current_date >= target_date else 7
        msg = "✨ **Тарифные планы**\n\nВыберите тариф для Happ:"
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton(f"🎁 Тест — {days_count} Дн.", callback_data="buy_test"))
        markup.add(InlineKeyboardButton("🚀 1 Мес — 50 ⭐️", callback_data="buy_1m"), InlineKeyboardButton("🔥 3 Мес — 85 ⭐️", callback_data="buy_3m"))
        markup.add(InlineKeyboardButton("💥 6 Мес — 150 ⭐️", callback_data="buy_6m"), InlineKeyboardButton("👑 1 Год — 250 ⭐️", callback_data="buy_1y"))
        markup.add(InlineKeyboardButton("♾ НАВСЕГДА — 500 ⭐️", callback_data="buy_forever"))
        bot.send_message(message.chat.id, msg, parse_mode="Markdown", reply_markup=markup)

    elif text == "👤 Моя подписка":
        msg = f"👤 **Профиль:**\n\nID: `{user_id}`\nСтатус: {user_data['status']}\nОсталось дней: `{user_data['days_left']}`\nПриглашено друзей: `{user_data['referrals']}`"
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")

    elif text == "👥 Пригласить друга":
        ref_link = f"https://t.me{user_id}"
        bot.send_message(message.chat.id, f"🎁 **Реферальная система**\n\nЗа каждого друга: +2 дня подписки!\n\n🔗 {ref_link}", disable_web_page_preview=True)

    elif text == "📌 Инструкция":
        msg = "⚙️ **Настройка Happ:**\n\n1️⃣ Нажмите 'Обновить server' и скопируйте ссылку.\n2️⃣ Вставьте её в приложение Happ в настройки подписок и обновите конфигурации!"
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")

    elif text == "🆘 Тех. поддержка":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("💬 Поддержка", url="tg://resolve?domain=potato_xd0"))
        bot.send_message(message.chat.id, "Нажмите на кнопку для перехода в ЛС разработчика:", reply_markup=markup)

    elif text == "🔄 Обновить server":
        if user_data["status"] == "🔴 Не активна":
            bot.send_message(message.chat.id, "❌ У вас нет активной подписки. Активируйте тест в разделе 'Тарифы'!", parse_mode="Markdown")
            return
        bot.send_message(message.chat.id, f"✅ **Ваша подписка Happ обновлена!**\n\n`{APP_URL}/sub/{user_id}`", parse_mode="Markdown")

    elif text == "⚙️ Админ-панель" and user_id == ADMIN_ID:
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton("📈 Статистика", callback_data="admin_stats"), InlineKeyboardButton("🎫 Выдать подписку", callback_data="admin_give"))
        markup.add(InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast"), InlineKeyboardButton("❌ Забрать доступ", callback_data="admin_revoke"))
        bot.send_message(message.chat.id, "🔒 **Панель Администратора:**", reply_markup=markup)

    elif user_id == ADMIN_ID and admin_states.get(user_id) == "waiting_for_id":
        admin_states[user_id] = f"waiting_for_days:{message.text.strip()}"
        bot.send_message(message.chat.id, "🔢 Теперь введите **количество дней**, которое хотите начислить:")

    elif user_id == ADMIN_ID and admin_states.get(user_id, "").startswith("waiting_for_days:"):
        target_id = admin_states[user_id].split(":")[1]
        try: days = int(message.text.strip())
        except: days = 30
        admin_states[user_id] = None
        db = load_db()
        if target_id in db["users"]:
            db["users"][target_id]["status"] = "🟢 Активна"
            db["users"][target_id]["days_left"] += days
            save_db(db)
            bot.send_message(message.chat.id, f"✅ Пользователю `{target_id}` добавлено дней: {days}!")
            try: bot.send_message(int(target_id), f"🎉 Администратор активировал вашу подписку Happ на {days} дней!")
            except: pass
        else: bot.send_message(message.chat.id, "❌ Пользователь не найден в бд.")

    elif user_id == ADMIN_ID and admin_states.get(user_id) == "waiting_for_revoke_id":
        target_id = message.text.strip()
        admin_states[user_id] = None
        db = load_db()
        if target_id in db["users"]:
            db["users"][target_id]["status"] = "🔴 Не активна"
            db["users"][target_id]["days_left"] = 0
            save_db(db)
            bot.send_message(message.chat.id, f"❌ Доступ для пользователя `{target_id}` успешно аннулирован.")
        else: bot.send_message(message.chat.id, "❌ Пользователь не найден.")

    elif user_id == ADMIN_ID and admin_states.get(user_id) == "waiting_for_broadcast":
        admin_states[user_id] = None
        db = load_db()
        count = 0
        for uid in db["users"]:
            try:
                bot.send_message(int(uid), message.text)
                count += 1
            except: pass
        bot.send_message(message.chat.id, f"📢 Рассылка завершена. Успешно отправлено {count} пользователям.")
        @bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    if call.data == "buy_test":
        bot.answer_callback_query(call.id)
        db = load_db()
        u_id = str(user_id)
        if db["users"][u_id]["has_test"]:
            bot.send_message(call.message.chat.id, "❌ Вы уже активировали тестовый период.")
        else:
            current_date = datetime.now()
            target_date = datetime(2026, 10, 19)
            test_days = 5 if current_date >= target_date else 7
            db["users"][u_id]["has_test"] = True
            db["users"][u_id]["days_left"] = test_days
            db["users"][u_id]["status"] = "🟢 Активна"
            save_db(db)
            bot.send_message(call.message.chat.id, f"🎉 **Тест на {test_days} дней для Happ успешно активирован!**")
            
    elif call.data == "admin_give" and user_id == ADMIN_ID:
        bot.answer_callback_query(call.id)
        admin_states[user_id] = "waiting_for_id"
        bot.send_message(call.message.chat.id, "✍️ **Введи Telegram ID** пользователя, кому выдать доступ:")
        
    elif call.data == "admin_revoke" and user_id == ADMIN_ID:
        bot.answer_callback_query(call.id)
        admin_states[user_id] = "waiting_for_revoke_id"
        bot.send_message(call.message.chat.id, "✍️ **Введи Telegram ID** пользователя для полной блокировки подписки:")
        
    elif call.data == "admin_broadcast" and user_id == ADMIN_ID:
        bot.answer_callback_query(call.id)
        admin_states[user_id] = "waiting_for_broadcast"
        bot.send_message(call.message.chat.id, "✍️ Введите **текст сообщения** для рассылки всем пользователям:")
        
    elif call.data == "admin_stats" and user_id == ADMIN_ID:
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"📊 Всего зарегистрировано пользователей: {len(load_db()['users'])}")
        
    elif call.data.startswith("buy_"):
        bot.answer_callback_query(call.id, "Оплата временно в режиме отладки.", show_alert=True)

@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode('utf-8'))])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL + '/' + BOT_TOKEN)
    return "Бот успешно настроен!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
