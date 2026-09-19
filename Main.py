import os, base64, telebot
from datetime import datetime
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from vpn_core import load_db, save_db, init_user, get_free_servers, find_user_by_input

BOT_TOKEN = "8789477182:AAEGulR-MpJ206pFeQ512DE32iRNcL3nD20"
APP_URL = "https://onrender.com"
ADMIN_ID = 5606075763
LOGO_URL = "https://imgur.com"

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)
admin_states = {}

@app.route('/sub/<user_id>')
def generate_subscription(user_id):
    db = load_db()
    if str(user_id) in db.get("banned", []): return "Вы забанены!", 403
    user_data = db["users"].get(str(user_id))
    if not user_data or user_data["status"] == "🔴 Не активна": return "Нет подписки!", 403
    servers = get_free_servers()
    if not servers: return "Ошибка серверов", 404
    return base64.b64encode("\n".join(servers).encode('utf-8')).decode('utf-8'), 200, {'Content-Type': 'text/plain; charset=utf-8'}

def get_main_keyboard(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("✨ Тарифы и Оплата"), KeyboardButton("📌 Инструкция"))
    markup.row(KeyboardButton("👤 Моя подписка"), KeyboardButton("👥 Пригласить друга"))
    markup.row(KeyboardButton("🔄 Обновить сервер"), KeyboardButton("🆘 Тех. поддержка"))
    if user_id == ADMIN_ID: markup.row(KeyboardButton("⚙️ Admin-панель"))
    return markup

def send_tariffs_menu(chat_id):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🎁 Получить ТЕСТ — 5 Дн. (Бесплатно)", callback_data="buy_test"),
        InlineKeyboardButton("💳 Купить Подписку (Т-Банк / СБП)", callback_data="buy_premium")
    )
    bot.send_message(chat_id, "✨ **Тарифные планы Happ:**", reply_markup=markup)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if str(user_id) in load_db().get("banned", []): return
    init_user(user_id, message.from_user.username)
    args = message.text.split()
    if len(args) > 1 and args[1].strip() != str(user_id):
        db = load_db()
        ref = args[1].strip()
        if ref in db["users"]:
            db["users"][ref]["referrals"] += 1
            db["users"][ref]["days_left"] += 2
            db["users"][ref]["status"] = "🟢 Активна"
            save_db(db)
            try: bot.send_message(int(ref), "🎉 Реферал! +2 дня подписки.")
            except: pass
    welcome_text = (
        "Добро Пожаловать В Door🚪VPN.\n"
        "Наши преимущества:\n"
        "Самые Низкие Цены🤩\n"
        "Тестовый Период 5 Дней🔥\n"
        "Под Каждого Пользователя Выделяется 1 Собственный Сервер👀\n"
        "Бесконечное Кол-во Устройств на 1 подписку♾️\n"
        "оформить подписку👇:"
    )
    inline_markup = InlineKeyboardMarkup().add(InlineKeyboardButton("✨ Оформить подписку", callback_data="open_tariffs"))
    try: bot.send_photo(message.chat.id, LOGO_URL, caption=welcome_text, reply_markup=inline_markup)
    except: bot.send_message(message.chat.id, welcome_text, reply_markup=inline_markup)
    bot.send_message(message.chat.id, "Используйте меню внизу для навигации:", reply_markup=get_main_keyboard(user_id))

@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    user_id = message.from_user.id
    if str(user_id) in load_db().get("banned", []): return
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
        markup.add(InlineKeyboardButton("🎫 Выдать подписку", callback_data="a_give"), InlineKeyboardButton("➖ Убрать дни", callback_data="a_sub"))
        markup.add(InlineKeyboardButton("❌ Аннулировать подписку", callback_data="a_clear"), InlineKeyboardButton("🚫 Забанить юзера", callback_data="a_ban"))
        markup.add(InlineKeyboardButton("🟢 Разбанить юзера", callback_data="a_unban"), InlineKeyboardButton("🔍 Проверить профиль", callback_data="a_view"))
        markup.add(InlineKeyboardButton("📢 Рассылка", callback_data="a_bc"), InlineKeyboardButton("📊 Статистика", callback_data="a_stats"))
        bot.send_message(message.chat.id, "🔒 **Супер-Админка Door VPN:**", reply_markup=markup)
    elif user_id == ADMIN_ID and str(admin_states.get(user_id, "")).startswith("wait_user_"):
        mode = admin_states[user_id].split("_")[2]
        t_id = find_user_by_input(text)
        if not t_id and mode != "unban":
            bot.send_message(message.chat.id, "❌ Юзер не найден в бд бота.")
            admin_states[user_id] = None
            return
        db = load_db()
        if mode == "give":
            admin_states[user_id] = f"wait_days_give:{t_id}"
            bot.send_message(message.chat.id, "🔢 Сколько дней ДОБАВИТЬ?:")
        elif mode == "sub":
            admin_states[user_id] = f"wait_days_sub:{t_id}"
            bot.send_message(message.chat.id, "🔢 Сколько дней ОТНЯТЬ?:")
        elif mode == "clear":
            admin_states[user_id] = None
            db["users"][t_id].update({"status": "🔴 Не активна", "days_left": 0})
            save_db(db)
            bot.send_message(message.chat.id, f"✅ Подписка юзера {t_id} сброшена в ноль.")
        elif mode == "ban":
            admin_states[user_id] = None
            if t_id not in db["banned"]: db["banned"].append(t_id)
            db["users"][t_id].update({"status": "🔴 Не активна", "days_left": 0})
            save_db(db)
            bot.send_message(message.chat.id, f"🚫 Юзер {t_id} полностью забанен.")
        elif mode == "unban":
            admin_states[user_id] = None
            clean_input = text.strip().lower().replace("@", "")
            found = None
            for b_id in db["banned"]:
                if b_id == clean_input or db["users"].get(b_id, {}).get("username") == clean_input: found = b_id
            if found:
                db["banned"].remove(found)
                save_db(db)
                bot.send_message(message.chat.id, f"🟢 Юзер {found} успешно разбанен.")
            else: bot.send_message(message.chat.id, "❌ Юзер не найден в списке бана.")
        elif mode == "view":
            admin_states[user_id] = None
            u_d = db["users"][t_id]
            bot.send_message(message.chat.id, f"📋 Профиль {t_id}:\nНик: @{u_d['username']}\nСтатус: {u_d['status']}\nДней: {u_d['days_left']}")
    elif user_id == ADMIN_ID and str(admin_states.get(user_id, "")).startswith("wait_days_"):
        mode, t_id = admin_states[user_id].split(":")
        try: days = int(text.strip())
        except: days = 0
        admin_states[user_id] = None
        db = load_db()
        if mode == "wait_days_give":
            db["users"][t_id]["days_left"] += days
            db["users"][t_id]["status"] = "🟢 Активна"
            bot.send_message(message.chat.id, f"✅ Добавлено {days} дней.")
            try: bot.send_message(int(t_id), f"🎉 Подписка продлена на {days} дней!")
            except: pass
        elif mode == "wait_days_sub":
            db["users"][t_id]["days_left"] = max(0, db["users"][t_id]["days_left"] - days)
            if db["users"][t_id]["days_left"] == 0: db["users"][t_id]["status"] = "🔴 Не активна"
            bot.send_message(message.chat.id, f"✅ Списано {days} дней.")
        save_db(db)
    elif user_id == ADMIN_ID and admin_states.get(user_id) == "waiting_for_broadcast":
        admin_states[user_id] = None
        count = 0
        for uid in load_db()["users"]:
            try: bot.send_message(int(uid), text); count += 1
            except: pass
        bot.send_message(message.chat.id, f"📢 Отправлено {count} людям.")

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    if call.data == "open_tariffs":
        bot.answer_callback_query(call.id)
        send_tariffs_menu(call.message.chat.id)
    elif call.data == "buy_test":
        bot.answer_callback_query(call.id)
        db = load_db()
        if db["users"][str(user_id)]["has_test"]: bot.send_message(call.message.chat.id, "❌ Вы уже брали тест.")
        else:
            db["users"][str(user_id)].update({"has_test": True, "days_left": 5, "status": "🟢 Активна"})
            save_db(db)
            bot.send_message(call.message.chat.id, "🎉 **Тест на 5 дней успешно активирован!**")
    elif call.data == "buy_premium":
        bot.answer_callback_query(call.id)
        pay_msg = f"💳 **Покупка премиум-доступа Happ**\n\n💵 **Стоимость:** 100 рублей / 30 дней.\n\nПереведите **100 рублей** по номеру телефона на Т-Банк. Отправьте скриншот чека разработчику с вашим ID: `{user_id}`"
        bot.send_message(call.message.chat.id, pay_msg, reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("💬 Отправить чек", url="tg://resolve?domain=potato_xd0")))
    elif call.data.startswith("a_") and user_id == ADMIN_ID:
        bot.answer_callback_query(call.id)
        if call.data == "a_stats":
            bot.send_message(call.message.chat.id, f"📊 Юзеров: {len(load_db()['users'])}\n🚫 В бане: {len(load_db().get('banned', []))}")
        elif call.data == "a_bc":
            admin_states[user_id] = "waiting_for_broadcast"
            bot.send_message(call.message.chat.id, "✍️ Введите текст рассылки:")
        else:
            mode = call.data.split("_")[1]
            admin_states[user_id] = f"wait_user_{mode}"
            bot.send_message(call.message.chat.id, "✍️ **Введи @username или ID пользователя:**")

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
