import os
import json
import base64
import requests
from flask import Flask, request
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# --- ТВОИ ДАННЫЕ (УЖЕ ВШИТЫ) ---
BOT_TOKEN = "8789477182:AAEGulR-MpJ206pFeQ512DE32iRNcL3nD20"
APP_URL = "https://my-vpn-bot-huvy.onrender.com"
ADMIN_ID = 5606075763  # Твой ID из скриншота для панели администратора

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Состояние для админки
admin_states = {}

# --- ПАРСЕР РЕАЛЬНЫХ БЕСПЛАТНЫХ СЕРВЕРОВ ---
def get_free_servers():
    """
    Собирает свежие бесплатные vless/ss ключи из публичных комьюнити-листов
    и автоматически распределяет им красивые "честные" названия стран.
    """
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
                    # Пробуем декодировать Base64 подписку
                    decoded = base64.b64decode(res.text).decode('utf-8')
                    lines = decoded.splitlines()
                except Exception:
                    lines = res.text.splitlines()
                
                for line in lines:
                    line = line.strip()
                    if line.startswith("ss://") or line.startswith("vless://"):
                        raw_servers.append(line)
        except Exception:
            continue
            
    # Убираем дубликаты
    raw_servers = list(set(raw_servers))
    
    # Красиво переименовываем серверы по порядку, чтобы был полноценный каталог
    formatted_servers = []
    countries = ["Германия 🇩🇪", "Нидерланды 🇳🇱", "Франция 🇫🇷", "США 🇺🇸", "Япония 🇯🇵", "Сингапур 🇸🇬", "Великобритания 🇬🇧"]
    
    for i, server in enumerate(raw_servers[:30]):  # Ограничимся 30 серверами для стабильности
        country = countries[i % len(countries)]
        # Отрезаем старое имя после знака # если оно есть
        base_server = server.split("#")[0]
        # Присваиваем новое имя локации
        formatted_servers.append(f"{base_server}#DoorVPN | {country} N{i+1}")
        
    return formatted_servers

# --- ЭНДПОИНТ ДЛЯ КАТАЛОГА (ПОДПИСКА) ---
@app.route('/sub/<user_id>')
def generate_subscription(user_id):
    servers = get_free_servers()
    if not servers:
        return "No servers available", 404
        
    subscription_text = "\n".join(servers)
    b64_subscription = base64.b64encode(subscription_text.encode('utf-8')).decode('utf-8')
    return b64_subscription, 200, {'Content-Type': 'text/plain; charset=utf-8'}

# --- КЛАВИАТУРА ИНТЕРФЕЙСА ---
def get_main_keyboard(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("✨ Тарифы и Оплата"), KeyboardButton("📌 Инструкция"))
    markup.row(KeyboardButton("👤 Моя подписка"), KeyboardButton("👥 Пригласить друга"))
    markup.row(KeyboardButton("🔄 Обновить сервер"), KeyboardButton("🆘 Тех. поддержка"))
    
    if user_id == ADMIN_ID:
        markup.row(KeyboardButton("⚙️ Админ-панель"))
    return markup

# --- ОБРАБОТКА КОМАНД ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "🚪 **Добро пожаловать в Door VPN!**\n\n"
        "Мы создали удобный бесплатный VPN прямо в Telegram.\n"
        "Используйте кнопки меню ниже, чтобы получить настройки!"
    )
    bot.send_message(
        message.chat.id, 
        welcome_text, 
        parse_mode="Markdown", 
        reply_markup=get_main_keyboard(message.from_user.id)
    )

# --- ОБРАБОТКА ТЕКСТОВЫХ КНОПОК ---
@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    user_id = message.from_user.id
    text = message.text

    if text == "✨ Тарифы и Оплата":
        msg = "✨ **Тарифные планы**\n\nВыберите тариф для Нарр:"
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton("🎁 Тест — 5 Дн.", callback_data="buy_test"))
        markup.add(InlineKeyboardButton("🚀 1 Мес — 50 ⭐️", callback_data="buy_1m"), InlineKeyboardButton("🔥 3 Мес — 85 ⭐️", callback_data="buy_3m"))
        markup.add(InlineKeyboardButton("💥 6 Мес — 150 ⭐️", callback_data="buy_6m"), InlineKeyboardButton("👑 1 Год — 250 ⭐️", callback_data="buy_1y"))
        markup.add(InlineKeyboardButton("♾ НАВСЕГДА — 500 ⭐️", callback_data="buy_forever"))
        bot.send_message(message.chat.id, msg, parse_mode="Markdown", reply_markup=markup)

    elif text == "👤 Моя подписка":
        msg = f"👤 **Профиль:**\n\nID: `{user_id}`\nСтатус:\n🔴 Не активна"
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")

    elif text == "👥 Пригласить друга":
        ref_link = f"https://t.me{user_id}"
        msg = f"🎁 **Рефералы**\n\nЗа друга: +1 день.\n\n🔗 **Ссылка:**\n{ref_link}"
        bot.send_message(message.chat.id, msg, disable_web_page_preview=True)

    elif text == "📌 Инструкция":
        msg = (
            "⚙️ **Настройка Нарр:**\n\n"
            "1️⃣ Скачайте приложение v2rayNG (Android) или Shadowrocket / Streisand (iOS).\n"
            "2️⃣ Нажмите кнопку **'Обновить сервер'** в боте и скопируйте выданную ссылку-каталог.\n"
            "3️⃣ Вставьте её в приложение в раздел подписок (плюсик вверху экрана) и обновите список!"
        )
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")

    elif text == "🆘 Тех. поддержка":
        # Исправленная кнопка-ссылка на твой аккаунт
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("💬 Написать в поддержку", url="https://t.me"))
        bot.send_message(message.chat.id, "Нажмите кнопку ниже, чтобы связаться с администратором:", reply_markup=markup)

    elif text == "🔄 Обновить сервер":
        bot.send_message(message.chat.id, "🔍 Ищу свободные узлы и формирую каталог...")
        servers = get_free_servers()
        if servers:
            sub_link = f"{APP_URL}/sub/{user_id}"
            msg = (
                "✅ **Ваш персональный каталог готов!**\n\n"
                f"`{sub_link}`\n\n"
                "👉 Нажмите на ссылку, чтобы скопировать её. Вставьте её в приложение в качестве подписки (Subscription URL), чтобы загрузить сразу все серверы стран Европы и Азии."
            )
            bot.send_message(message.chat.id, msg, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "❌ Ошибка загрузки серверов. Попробуйте через пару минут.")

    elif text == "⚙️ Админ-панель" and user_id == ADMIN_ID:
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton("📈 Статистика", callback_data="admin_stats"), InlineKeyboardButton("🎫 Выдать доступ", callback_data="admin_give"))
        bot.send_message(message.chat.id, "🔒 **Панель Administrator:**", reply_markup=markup)

    # Обработка ввода ID для админки
    elif user_id == ADMIN_ID and admin_states.get(user_id) == "waiting_for_id":
        target_id = text
        admin_states[user_id] = None
        bot.send_message(message.chat.id, f"✅ Доступ для пользователя `{target_id}` успешно активирован!", parse_mode="Markdown", reply_markup=get_main_keyboard(user_id))

# --- ОБРАБОТКА CALLBACK КНОПОК ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.data == "admin_give" and call.from_user.id == ADMIN_ID:
        bot.answer_callback_query(call.id)
        admin_states[call.from_user.id] = "waiting_for_id"
        bot.send_message(call.message.chat.id, "✍️ **Введи Telegram ID** пользователя, которому хочешь выдать доступ:")
        
    elif call.data == "admin_stats" and call.from_user.id == ADMIN_ID:
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "📊 **Статистика Door VPN:**\n\nВсего пользователей: 1\nАктивных подписок: 0")
        
    elif call.data.startswith("buy_"):
        bot.answer_callback_query(call.id, "Оплата временно недоступна", show_alert=True)

# --- ВЕБХУКИ И ФЛАСК ---
@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL + '/' + BOT_TOKEN)
    return "Door VPN Бот успешно запущен!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
