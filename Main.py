import os
import telebot
from telebot import types

# Вставьте сюда ваш НОВЫЙ токен от @BotFather
TOKEN = "8789477182:AAFPSYA2BPxe5lOoCuLPUyMODtOuN5AIdfA"

bot = telebot.TeleBot(TOKEN)

# Главное меню бота
def get_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_rates = types.KeyboardButton("📊 Тарифы и Оплата")
    btn_status = types.KeyboardButton("📌 Моя подписка")
    btn_help = types.KeyboardButton("💡 Инструкция по настройке")
    keyboard.add(btn_rates)
    keyboard.add(btn_status, btn_help)
    return keyboard

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        f"👋 Привет, {message.from_user.first_name}! Добро пожаловать.\n\n"
        "🔒 Здесь ты можешь приобрести быстрый и защищенный VPN-доступ 24/7.\n"
        "Управляй своей подпиской с помощью меню ниже 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard())

# Обработка нажатий на кнопки меню
@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == "📊 Тарифы и Оплата":
        markup = types.InlineKeyboardMarkup()
        btn_1m = types.InlineKeyboardButton("🚀 1 Месяц — 50 Звёзд", callback_data="buy_1m")
        btn_3m = types.InlineKeyboardButton("🔥 3 Месяца — 120 Звёзд", callback_data="buy_3m")
        markup.add(btn_1m)
        markup.add(btn_3m)
        
        bot.send_message(
            message.chat.id, 
            "✨ **Выберите подходящий тариф:**\n\n"
            "После оплаты бот мгновенно вышлет ваш персональный ключ доступа и инструкцию.",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        
    elif message.text == "📌 Моя подписка":
        bot.send_message(
            message.chat.id,
            "👤 **Информация о подписке:**\n\n"
            "🔴 Статус: Не active\n"
            "📅 Действует до: Нет данных\n\n"
            "Чтобы активировать доступ, перейдите в раздел тарифов."
        )
        
    elif message.text == "💡 Инструкция по настройке":
        bot.send_message(
            message.chat.id,
            "⚙️ **Как подключить VPN:**\n\n"
            "1. Скачайте приложение **v2rayNG** (для Android) или **Streisand** (для iPhone).\n"
            "2. Скопируйте ключ, который выдаст бот после оплаты тарифа.\n"
            "3. Импортируйте ключ в приложение через кнопку «Плюс» (+).\n"
            "4. Нажмите кнопку подключения. Готово! 🚀"
        )

# Обработка выбора тарифа (Генерация счета на оплату через Telegram Stars)
@bot.callback_query_handler(func=lambda call: call.data in ["buy_1m", "buy_3m"])
def process_payment(call):
    bot.answer_callback_query(call.id)
    
    if call.data == "buy_1m":
        title = "VPN Доступ — 1 месяц"
        description = "Подписка на скоростной личный VPN сроком на 30 дней."
        prices = [types.LabeledPrice(label="Telegram Stars", amount=50)]
    else:
        title = "VPN Доступ — 3 месяца"
        description = "Выгодная подписка на личный VPN сроком на 90 дней."
        prices = [types.LabeledPrice(label="Telegram Stars", amount=120)]
        
    bot.send_invoice(
        call.message.chat.id,
        title=title,
        description=description,
        invoice_payload="vpn_subscription_payload",
        provider_token="", # Для Telegram Stars это поле обязательно оставляем пустым!
        currency="XTR",   # Код валюты Telegram Stars
        prices=prices,
        start_parameter="vpn-sub"
    )

# Подтверждение готовности принять платеж
@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# Обработка успешного платежа
@bot.successful_payment_handler(func=lambda payment: True)
def process_successful_payment(message):
    thank_you_text = (
        "🎉 **Оплата прошла успешно! Спасибо за покупку!**\n\n"
        "🔑 Ваш временный ключ доступа:\n"
        "`vless://public-test-key-here@185.12.34.56:443?security=reality`\n\n"
        "Скопируйте его целиком и вставьте в ваше приложение для VPN по инструкции."
    )
    bot.send_message(message.chat.id, thank_you_text, parse_mode="Markdown")

print("Бот запущен...")
bot.infinity_polling()
