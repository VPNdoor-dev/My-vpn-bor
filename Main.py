import os
import telebot
from telebot import types

# 1. Вставьте сюда ваш секретный токен от @BotFather (кавычки не удаляйте!)
TOKEN = "8789477182:AAFBI8Xz32wHR5gzQf0hGDe1_GjAV44FuFs"

# 2. Вставьте сюда ваш числовой Telegram ID (можно узнать в боте @userinfobot)
ADMIN_ID = 5606075763  # 👈 Замените 0 на ваш ID, например: ADMIN_ID = 12345678

bot = telebot.TeleBot(TOKEN)

# Главное меню бота
def get_main_keyboard(user_id):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_rates = types.KeyboardButton("📊 Тарифы и Оплата")
    btn_status = types.KeyboardButton("📌 Моя подписка")
    btn_help = types.KeyboardButton("💡 Инструкция по настройке")
    keyboard.add(btn_rates)
    keyboard.add(btn_status, btn_help)
    
    # Секретная кнопка для админа
    if user_id == ADMIN_ID:
        btn_admin = types.KeyboardButton("⚙️ Админ-панель")
        keyboard.add(btn_admin)
        
    return keyboard

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        f"👋 Привет, {message.from_user.first_name}! Добро пожаловать.\n\n"
        "🔒 Здесь ты можешь приобрести быстрый и защищенный VPN-доступ 24/7.\n"
        "Управляй своей подпиской с помощью меню ниже 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard(message.from_user.id))

# Обработка нажатий на кнопки меню
@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = message.from_user.id
    
    if message.text == "📊 Тарифы и Оплата":
        markup = types.InlineKeyboardMarkup()
        btn_1m = types.InlineKeyboardButton("🚀 1 Месяц — 50 Звёзд", callback_data="buy_1m")
        btn_3m = types.InlineKeyboardButton("🔥 3 Месяца — 120 Звёзд", callback_data="buy_3m")
        markup.add(btn_1m, btn_3m)
        
        bot.send_message(
            message.chat.id, 
            "✨ **Выберите подходящий тариф:**\n\nПосле оплаты бот мгновенно вышлет ключ.",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        
    elif message.text == "📌 Моя подписка":
        bot.send_message(message.chat.id, "👤 **Информация о подписке:**\n\n🔴 Статус: Не активна")
        
    elif message.text == "💡 Инструкция по настройке":
        bot.send_message(message.chat.id, "⚙️ **Как подключить VPN:**\n\n1. Скачайте приложение **v2rayNG** или **Streisand**.")
        
    # Админка
    elif message.text == "⚙️ Админ-панель" and user_id == ADMIN_ID:
        markup = types.InlineKeyboardMarkup()
        btn_stats = types.InlineKeyboardButton("📈 Статистика бота", callback_data="admin_stats")
        markup.add(btn_stats)
        bot.send_message(message.chat.id, "🔒 **Панель Администратора:**", reply_markup=markup)

# Обработка действий в админке
@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def handle_admin_callbacks(call):
    if call.from_user.id != ADMIN_ID:
        return
    if call.data == "admin_stats":
        bot.send_message(call.message.chat.id, "📊 **Статистика:**\n\nВсего пользователей: 1\nАктивных подписок: 0")

# Выставление счета (Telegram Stars)
@bot.callback_query_handler(func=lambda call: call.data in ["buy_1m", "buy_3m"])
def process_payment(call):
    bot.answer_callback_query(call.id)
    amount = 50 if call.data == "buy_1m" else 120
    prices = [types.LabeledPrice(label="Telegram Stars", amount=amount)]
    bot.send_invoice(
        call.message.chat.id,
        title="VPN Доступ",
        description="Подписка на личный VPN",
        invoice_payload="vpn_sub",
        provider_token="",
        currency="XTR",
        prices=prices,
        start_parameter="vpn-sub"
    )

# Подтверждение готовности принять платеж
@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# ИСПРАВЛЕННЫЙ хэндлер успешного платежа
@bot.message_handler(content_types=['successful_payment'])
def process_successful_payment(message):
    thank_you_text = (
        "🎉 **Оплата прошла успешно! Спасибо за покупку!**\n\n"
        "🔑 Ваш временный ключ доступа:\n"
        "`vless://public-test-key-here@185.12.34.56:443?security=reality`\n\n"
        "Скопируйте его целиком и вставьте в ваше приложение для VPN по инструкции."
    )
    bot.send_message(message.chat.id, thank_you_text, parse_mode="Markdown")

print("Бот успешно запущен...")
bot.infinity_polling()
