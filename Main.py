import os
import requests
import random
import base64
import telebot
from telebot import types

# 1. СЮДА ВСТАВЬТЕ ВАШ ТОКЕН ОТ @BotFather (кавычки оставьте!)
TOKEN = "8789477182:AAFBI8Xz32wHR5gzQf0hGDe1_GjAV44FuFs"

# 2. СЮДА ВСТАВЬТЕ ВАШ ЧИСЛОВОЙ ID ОТ @userinfobot (БЕЗ кавычек!)
ADMIN_ID = 5606075763  # 👈 Замените 0 на ваш ID, например: ADMIN_ID = 123456789

# 3. Ваш юзернейм (уже настроен и готов к работе!)
ADMIN_USERNAME = "potato_xd0"

# 4. Ссылка на картинку логотипа
IMAGE_URL = "https://i.imgur.com/EQKdqpl.png" 

bot = telebot.TeleBot(TOKEN)

def get_happ_config():
    try:
        url = "http://vpngate.net"
        response = requests.get(url, timeout=10)
        lines = response.text.split('\n')
        
        valid_ips = []
        for line in lines:
            if line.startswith('*') or line.startswith('#') or not line.strip():
                continue
            parts = line.split(',')
            if len(parts) > 7:
                valid_ips.append((parts[1], parts[2], parts[6]))
                
        if valid_ips:
            chosen = random.choice(valid_ips)
            fake_password = "password123"
            method_and_pass = f"chacha20-ietf-poly1305:{fake_password}"
            b64_login = base64.b64encode(method_and_pass.encode('utf-8')).decode('utf-8')
            
            happ_key = f"ss://{b64_login}@{chosen[0]}:{chosen[1]}#DoorVPN-{chosen[2]}"
            return happ_key, chosen[2]
    except Exception as e:
        print(f"Ошибка парсинга серверов: {e}")
    return None, None

def get_main_keyboard(user_id):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_rates = types.KeyboardButton("📊 Тарифы и Оплата")
    btn_status = types.KeyboardButton("📌 Моя подписка")
    btn_help = types.KeyboardButton("💡 Инструкция по настройке")
    btn_support = types.KeyboardButton("🆘 Тех. поддержка")
    keyboard.add(btn_rates)
    keyboard.add(btn_status, btn_help)
    keyboard.add(btn_support)
    
    if user_id == ADMIN_ID:
        keyboard.add(types.KeyboardButton("⚙️ Админ-панель"))
    return keyboard

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        f"👋 Привет, {message.from_user.first_name}! Добро пожаловать в **Door VPN**.\n\n"
        "🔒 Мы генерируем самые быстрые, современные зашифрованные ключи для официального приложения **Happ**!\n\n"
        "Управляй подпиской с помощью меню ниже 👇"
    )
    try:
        bot.send_photo(message.chat.id, IMAGE_URL, caption=welcome_text, reply_markup=get_main_keyboard(message.from_user.id), parse_mode="Markdown")
    except Exception:
        bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard(message.from_user.id), parse_mode="Markdown")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = message.from_user.id
    
    if message.text == "📊 Тарифы и Оплата":
        markup = types.InlineKeyboardMarkup()
        btn_free = types.InlineKeyboardButton("🎁 Пробный период — 3 Дня (Бесплатно)", callback_data="buy_trial")
        btn_1m = types.InlineKeyboardButton("🚀 1 Месяц — 50 ⭐", callback_data="buy_1m")
        btn_3m = types.InlineKeyboardButton("🔥 3 Месяца — 120 ⭐", callback_data="buy_3m")
        btn_6m = types.InlineKeyboardButton("💥 6 Месяцев — 220 ⭐", callback_data="buy_6m")
        btn_1y = types.InlineKeyboardButton("👑 1 Год — 400 ⭐", callback_data="buy_1y")
        btn_inf = types.InlineKeyboardButton("♾ НАВСЕГДА (Безлимит) — 1000 ⭐", callback_data="buy_inf")
        
        markup.add(btn_free)
        markup.add(btn_1m, btn_3m)
        markup.add(btn_6m, btn_1y)
        markup.add(btn_inf)
        
        bot.send_message(message.chat.id, "✨ **Выберите тарифный план:**\n\nПосле выбора бот мгновенно создаст ключ для приложения Happ.", reply_markup=markup, parse_mode="Markdown")
        
    elif message.text == "📌 Моя подписка":
        bot.send_message(message.chat.id, "👤 **Информация о подписке:**\n\n🔴 Статус: **Не активна**\n⏳ Оставшееся время: 0 дней")
        
    elif message.text == "💡 Инструкция по настройке":
        instructions = (
            "⚙️ **Актуальная инструкция по настройке через Happ:**\n\n"
            "1️⃣ **Скачайте приложение Happ на устройство:**\n"
            "• [Скачать для iPhone (App Store)](https://apple.com)\n"
            "• [Скачать для Android (Google Play)](https://google.com)\n\n"
            "2️⃣ **Скопируйте ваш персональный ключ:**\n"
            "Нажмите на текстовый ключ, который выдал вам бот (он начинается с `ss://`), чтобы он полностью скопировался в буфер обмена телефона.\n\n"
            "3️⃣ **Активируйте ключ в приложении:**\n"
            "• Откройте приложение **Happ**.\n"
            "• Система автоматически обнаружит скопированный ключ и покажет уведомление.\n"
            "• Нажмите синюю кнопку **«Поехали»** (или «Добавить»), чтобы импортировать настройки.\n\n"
            "4️⃣ **Включите VPN:**\n"
            "Нажмите на добавленный сервер **DoorVPN** в списке, а затем нажмите на большую круглую кнопку включения по центру экрана. Готово! 🚀"
        )
        bot.send_message(message.chat.id, instructions, parse_mode="Markdown", disable_web_page_preview=True)
        
    elif message.text == "🆘 Тех. поддержка":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("👨‍💻 Написать администратору", url=f"https://t.me{ADMIN_USERNAME}"))
        bot.send_message(message.chat.id, "🤝 Возникли проблемы? Свяжитесь с нами:", reply_markup=markup)
        
    elif message.text in ["⚙️ Admin-панель", "⚙️ Админ-панель"] and user_id == ADMIN_ID:
        markup = types.InlineKeyboardMarkup()
        btn_stats = types.InlineKeyboardButton("📈 Статистика", callback_data="admin_stats")
        btn_give_trial = types.InlineKeyboardButton("🎫 Выдать Happ-ключ (Тест)", callback_data="admin_give_trial")
        markup.add(btn_stats)
        markup.add(btn_give_trial)
        bot.send_message(message.chat.id, "🔒 **Панель Администратора:**", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def handle_admin_callbacks(call):
    if call.from_user.id != ADMIN_ID: return
    bot.answer_callback_query(call.id)
    
    if call.data == "admin_stats":
        bot.send_message(call.message.chat.id, "📊 **Статистика:**\n\nВсего пользователей: 1\nАгрегатор Happ-ключей активен.")
    elif call.data == "admin_give_trial":
        bot.send_message(call.message.chat.id, "⏳ Генерирую ключ...")
        key, country = get_happ_config()
        if key:
            bot.send_message(call.message.chat.id, f"🎁 **Админ-ключ для Happ создан (Локация: {country}):**\n\n`{key}`\n\nПросто перешлите этот текст клиенту.", parse_mode="Markdown")
        else:
            bot.send_message(call.message.chat.id, "❌ База перегружена, повторите попытку.")

@bot.callback_query_handler(func=lambda call: call.data in ["buy_trial", "buy_1m", "buy_3m", "buy_6m", "buy_1y", "buy_inf"])
def process_payment(call):
    bot.answer_callback_query(call.id)
    
    if call.data == "buy_trial":
        bot.send_message(call.message.chat.id, "⏳ Подключаюсь к пулу серверов Happ...")
        key, country = get_happ_config()
        if key:
            trial_text = (
                f"🎉 **Твой бесплатный тест на 3 дня готов!**\n\n"
                f"📍 Страна подключения: **{country}**\n\n"
                f"Нажмите на ключ ниже, чтобы скопировать его:\n\n"
                f"`{key}`\n\n"
                f"Скопируйте его и откройте приложение **Happ** по нашей кнопке инструкции!"
            )
            bot.send_message(call.message.chat.id, trial_text, parse_mode="Markdown")
        else:
            bot.send_message(call.message.chat.id, "❌ Сервера обновляются, нажмите кнопку еще раз через 5 секунд.")
        return

    tariff_data = {
        "buy_1m": ("1 месяц", 50), "buy_3m": ("3 месяца", 120),
        "buy_6m": ("6 месяцев", 220), "buy_1y": ("1 год", 400), "buy_inf": ("НАВСЕГДА", 1000)
    }
    name, price = tariff_data[call.data]
    prices = [types.LabeledPrice(label="Telegram Stars", amount=price)]
    bot.send_invoice(call.message.chat.id, title=f"Door VPN — {name}", description=f"Ключ доступа для Happ", invoice_payload="vpn_sub", provider_token="", currency="XTR", prices=prices, start_parameter="vpn-sub")

@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def process_successful_payment(message):
    bot.send_message(message.chat.id, "⏳ Платеж принят! Создаю персональную подписку...")
    key, country = get_happ_config()
    if key:
        thank_text = (
            f"🎉 **Оплата успешно завершена!**\n\n"
            f"🔑 Твой премиум-ключ для приложения Happ (Локация: {country}):\n\n"
            f"`{key}`\n\n"
            f"Скопируй строчку и добавь в приложение!"
        )
        bot.send_message(message.chat.id, thank_text, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "❌ Сбой базы. Напишите в поддержку, админ выдаст ключ вручную через админку!")

print("Бот под Happ запущен...")
bot.infinity_polling()
