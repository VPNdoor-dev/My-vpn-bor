import os
import requests
import random
import base64
import sqlite3
import datetime
import telebot
import threading
from telebot import types
from http.server import (
    BaseHTTPRequestHandler,
    HTTPServer,
)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(
    os.getenv("ADMIN_ID", "0")
)
ADMIN_USER = os.getenv(
    "ADMIN_USERNAME", "potato_xd0"
).replace("@", "")
IMG = (
    "https://imgur.com"
)
bot = telebot.TeleBot(TOKEN)
DB = "vpn_users.db"


class HealthCheck(
    BaseHTTPRequestHandler
):
    def do_GET(self):
        self.send_response(200)
        self.send_header(
            "Content-type",
            "text/plain",
        )
        self.end_headers()
        self.wfile.write(b"OK")


def run_health_server():
    port = int(
        os.getenv("PORT", "10000")
    )
    try:
        server = HTTPServer(
            ("0.0.0.0", port),
            HealthCheck,
        )
        server.serve_forever()
    except:
        pass


def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT 
        EXISTS users (
            user_id INTEGER PRIMARY KEY, 
            has_trial INTEGER DEFAULT 0, 
            expires_at TEXT, 
            referred_by INTEGER
        )"""
    )
    conn.commit()
    conn.close()


init_db()


def get_trial_days():
    t = datetime.date.today()
    lim = datetime.date(2026, 10, 15)
    return 5 if t <= lim else 3


def get_total_users():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM users"
    )
    tot = cur.fetchone()
    cur.execute(
        "SELECT COUNT(*) FROM users "
        "WHERE has_trial = 1"
    )
    tr = cur.fetchone()
    conn.close()
    return tot, tr
 def check_trial(uid):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        "SELECT has_trial FROM users "
        "WHERE user_id = ?",
        (uid,),
    )
    res = cur.fetchone()
    conn.close()
    return res if res else 0


def set_trial_used(uid):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET "
        "has_trial = 1 "
        "WHERE user_id = ?",
        (uid,),
    )
    conn.commit()
    conn.close()


def add_user_days(uid, days):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        "SELECT expires_at FROM users "
        "WHERE user_id = ?",
        (uid,),
    )
    res = cur.fetchone()
    td = datetime.date.today()
    if res and res:
        try:
            fmt = "%Y-%m-%d"
            c_exp = (
                datetime.datetime
                .strptime(res, fmt)
                .date()
            )
            base = (
                c_exp if c_exp >= td
                else td
            )
        except:
            base = td
    else:
        base = td
    n_exp = base + (
        datetime.timedelta(days=days)
    )
    n_exp_str = (
        n_exp.strftime("%Y-%m-%d")
    )
    cur.execute(
        "INSERT OR REPLACE INTO "
        "users (user_id, expires_at) "
        "VALUES (?, ?)",
        (uid, n_exp_str),
    )
    conn.commit()
    conn.close()
    return n_exp_str


def check_user_status(uid):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        "SELECT expires_at FROM users "
        "WHERE user_id = ?",
        (uid,),
    )
    res = cur.fetchone()
    conn.close()
    if res and res:
        try:
            fmt = "%Y-%m-%d"
            exp = (
                datetime.datetime
                .strptime(res, fmt)
                .date()
            )
            if (
                exp >=
                datetime.date.today()
            ):
                dl = (
                    exp -
                    datetime.date
                    .today()
                ).days
                return (
                    f"🟢 Активна\n"
                    f"📅 До: {res}\n"
                    f"⏳ Осталось: "
                    f"{dl} дн."
                )
        except:
            pass
    return "🔴 Не активна"


def get_main_keyboard(uid):
    m = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )
    m.add(
        types.KeyboardButton(
            "📊 Тарифы и Оплата"
        ),
        types.KeyboardButton(
            "📌 Моя подписка"
        ),
    )
    m.add(
        types.KeyboardButton(
            "👥 Пригласить друга"
        ),
        types.KeyboardButton(
            "💡 Инструкция"
        ),
    )
    m.add(
        types.KeyboardButton(
            "🔄 Обновить сервер"
        ),
        types.KeyboardButton(
            "🆘 Тех. поддержка"
        ),
    )
    if uid == ADMIN_ID:
        m.add(
            types.KeyboardButton(
                "⚙️ Админ-панель"
            )
        )
    return m


def get_happ_config():
    try:
        url = (
            "http://vpngate.net"
            "/api/iphone/"
        )
        resp = requests.get(
            url, timeout=(4, 5)
        )
        lines = resp.text.split("\n")
        ips = []
        for line in lines:
            if (
                line.strip()
                and not
                line.startswith("*")
                and not
                line.startswith("#")
                and "vpn" in line
            ):
                p = line.split(",")
                if len(p) > 2:
                    ips.append((p, p))
        if ips:
            ip, country = (
                random.choice(ips)
            )
            m = (
                "chacha20-ietf-"
                "poly1305:"
                "password123"
            )
            b64 = (
                base64.b64encode(
                    m.encode("utf-8")
                ).decode("utf-8")
            )
            return (
                f"ss://{b64}@"
                f"{ip}:443#"
                f"DoorVPN-{country}",
                country,
            )
    except Exception as e:
        print(f"Ошибка API: {e}")
    return None, None
 @bot.message_handler(
    commands=["start"]
)
def start(m):
    uid = m.from_user.id
    p = m.text.split()
    ref_id = None
    if (
        len(p) > 1
        and p.isdigit()
    ):
        p_ref = int(p)
        if p_ref != uid:
            ref_id = p_ref
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_id FROM users "
        "WHERE user_id = ?",
        (uid,),
    )
    ex = cursor.fetchone()
    if not ex:
        cursor.execute(
            "INSERT INTO users "
            "(user_id, referred_by) "
            "VALUES (?, ?)",
            (uid, ref_id),
        )
        conn.commit()
        if ref_id:
            add_user_days(ref_id, 1)
            try:
                bot.send_message(
                    ref_id,
                    "🎉 Друг зашел по "
                    "ссылке! +1 день "
                    "подписки.",
                    parse_mode="Markdown"
                )
            except:
                pass
    conn.close()
    t = (
        f"👋 Привет, "
        f"{m.from_user.first_name}!\n"
        f"Добро пожаловать в "
        f"**Door VPN**.\n\n"
        f"🛡 Премиум-сервис для "
        f"**Happ**.\n"
        f"Управляйте меню 👇"
    )
    kb = get_main_keyboard(uid)
    try:
        bot.send_photo(
            m.chat.id,
            IMG,
            caption=t,
            reply_markup=kb,
            parse_mode="Markdown",
        )
    except:
        bot.send_message(
            m.chat.id,
            t,
            reply_markup=kb,
            parse_mode="Markdown",
        )


@bot.message_handler(
    content_types=["text"]
)
def text_handler(m):
    uid = m.from_user.id
    if m.text == "📊 Тарифы и Оплата":
        markup = (
            types
            .InlineKeyboardMarkup()
        )
        td = get_trial_days()
        markup.add(
            types.InlineKeyboardButton(
                f"🎁 Тест — {td} Дн.",
                callback_data="buy_trial",
            )
        )
        markup.add(
            types.InlineKeyboardButton(
                "🚀 1 Мес — 50 ⭐",
                callback_data=(
                    "pay_select_1m"
                ),
            ),
            types.InlineKeyboardButton(
                "🔥 3 Мес — 85 ⭐",
                callback_data=(
                    "pay_select_3m"
                ),
            ),
        )
        markup.add(
            types.InlineKeyboardButton(
                "💥 6 Мес — 150 ⭐",
                callback_data=(
                    "pay_select_6m"
                ),
            ),
            types.InlineKeyboardButton(
                "👑 1 Год — 250 ⭐",
                callback_data=(
                    "pay_select_1y"
                ),
            ),
        )
        markup.add(
            types.InlineKeyboardButton(
                "♾ НАВСЕГДА — 500 ⭐",
                callback_data=(
                    "pay_select_inf"
                ),
            )
        )
        bot.send_message(
            m.chat.id,
            "✨ **Тарифные планы**\n\n"
            "Выберите тариф для Happ:",
            reply_markup=markup,
            parse_mode="Markdown",
        )
    elif m.text == "📌 Моя подписка":
        status = check_user_status(uid)
        bot.send_message(
            m.chat.id,
            f"👤 **Профиль:**\n\n"
            f"ID: `{uid}`\n"
            f"Статус:\n{status}",
            parse_mode="Markdown",
        )
    elif m.text == "👥 Пригласить друга":
        name = bot.get_me().username
        bot.send_message(
            m.chat.id,
            f"🎁 **Рефералы**\n\n"
            f"За друга: **+1 день**.\n\n"
            f"🔗 Ссылка:\n"
            f"`https://t.me{name}"
            f"?start={uid}`",
            parse_mode="Markdown",
        )
    elif m.text == "🔄 Обновить сервер":
        bot.send_message(
            m.chat.id, "🔄 Ищу узел..."
        )
        key, country = (
            get_happ_config()
        )
        if key:
            bot.send_message(
                m.chat.id,
                f"✅ **Узел изменен!**\n"
                f"📍 Страна: "
                f"{country}\n\n"
                f"`{key}`",
                parse_mode="Markdown",
            )
        else:
            bot.send_message(
                m.chat.id,
                "❌ Попробуйте позже."
            )
    elif m.text == "💡 Инструкция":
        bot.send_message(
            m.chat.id,
            "⚙️ **Настройка Happ:**\n\n"
            "1️⃣ Скачайте Happ.\n"
            "2️⃣ Скопируйте ключ `ss://`.\n"
            "3️⃣ Вставьте ключ в Happ. 🚀",
            parse_mode="Markdown",
        )
    elif m.text == "🆘 Тех. поддержка":
        m_up = (
            types
            .InlineKeyboardMarkup()
        )
        m_up.add(
            types.InlineKeyboardButton(
                "👨‍💻 Написать",
                url=f"https://t.me"
                f"{ADMIN_USER}",
            )
        )
        bot.send_message(
            m.chat.id,
            "🤝 Поддержка на связи:",
            reply_markup=m_up,
        )
    elif (
        m.text in [
            "⚙️ Admin-панель",
            "⚙️ Админ-панель",
        ]
        and uid == ADMIN_ID
    ):
        markup = (
            types
            .InlineKeyboardMarkup()
        )
        markup.add(
            types.InlineKeyboardButton(
                "📈 Статистика",
                callback_data=(
                    "admin_stats"
                ),
            ),
            types.InlineKeyboardButton(
                "🎫 Выдать доступ",
                callback_data=(
                    "admin_give_id"
                ),
            ),
        )
        bot.send_message(
            m.chat.id,
            "🔒 Панель Administrator:",
            reply_markup=markup,
 )
     @bot.callback_query_handler(
    func=lambda c: c.data
    .startswith("admin_")
)
def admin_cb(call):
    if (
        call.from_user.id !=
        ADMIN_ID
    ):
        return
    bot.answer_callback_query(
        call.id
    )
    if (
        call.data ==
        "admin_stats"
    ):
        tot, tr = get_total_users()
        bot.send_message(
            call.message.chat.id,
            f"📊 Статистика:\n\n"
            f"Юзеров: {tot}\n"
            f"Тестов: {tr}",
        )
    elif (
        call.data ==
        "admin_give_id"
    ):
        msg = bot.send_message(
            call.message.chat.id,
            "✍️ Введи Telegram ID "
            "пользователя для выдачи:",
        )
        bot.register_next_step_handler(
            msg, admin_get_id
        )


def admin_get_id(m):
    if (
        m.from_user.id !=
        ADMIN_ID
    ):
        return
    if not m.text.isdigit():
        bot.send_message(
            m.chat.id,
            "❌ ID только из цифр!"
        )
        return
    t_id = int(m.text)
    markup = (
        types
        .InlineKeyboardMarkup()
    )
    markup.add(
        types.InlineKeyboardButton(
            "🚀 1 Месяц",
            callback_data=(
                f"adm_give_{t_id}_30"
            ),
        )
    )
    markup.add(
        types.InlineKeyboardButton(
            "🔥 3 Месяца",
            callback_data=(
                f"adm_give_{t_id}_90"
            ),
        )
    )
    markup.add(
        types.InlineKeyboardButton(
            "💥 6 Месяцев",
            callback_data=(
                f"adm_give_{t_id}_180"
            ),
        )
    )
    markup.add(
        types.InlineKeyboardButton(
            "👑 1 Год",
            callback_data=(
                f"adm_give_{t_id}_365"
            ),
        )
    )
    markup.add(
        types.InlineKeyboardButton(
            "♾ Навсегда",
            callback_data=(
                f"adm_give_{t_id}_9999"
            ),
        )
    )
    bot.send_message(
        m.chat.id,
        f"⏳ Выбери время "
        f"подписки для ID `{t_id}`:",
        reply_markup=markup,
        parse_mode="Markdown",
    )


@bot.callback_query_handler(
    func=lambda c: c.data
    .startswith("adm_give_")
)
def admin_confirm_give_cb(call):
    if (
        call.from_user.id !=
        ADMIN_ID
    ):
        return
    bot.answer_callback_query(
        call.id
    )
    _, _, t_id, days = (
        call.data.split("_")
    )
    t_id, days = int(t_id), int(days)
    add_user_days(t_id, days)
    bot.send_message(
        call.message.chat.id,
        f"✅ Подписка на {days} дн. "
        f"добавлена для ID `{t_id}`!",
        parse_mode="Markdown",
    )
    key, country = (
        get_happ_config()
    )
    if key:
        try:
            text = (
                f"🎉 Администратор "
                f"активировал вам "
                f"подписку на "
                f"**{days} дней**!\n"
                f"📍 Узел: {country}\n\n"
                f"Ваш ключ:\n`{key}`"
            )
            bot.send_message(
                t_id, text,
                parse_mode="Markdown"
            )
            bot.send_message(
                call.message.chat.id,
                f"🚀 Ключ отправлен!"
            )
        except:
            bot.send_message(
                call.message.chat.id,
                f"⚠️ Не удалось "
                f"отправить в чат. "
                f"Скопируй сам:\n\n"
                f"`{key}`",
            )


@bot.callback_query_handler(
    func=lambda c: c.data
    .startswith("pay_select_")
)
def pay_select_cb(call):
    bot.answer_callback_query(
        call.id
    )
    tariff = (
        call.data.split("_")[-1]
    )
    markup = (
        types
        .InlineKeyboardMarkup()
    )
    markup.add(
        types.InlineKeyboardButton(
            "⭐ Telegram Stars",
            callback_data=(
                f"buy_stars_"
                f"{tariff}"
            ),
        )
    )
    markup.add(
        types.InlineKeyboardButton(
            "💳 Карта / СБП (Вручную)",
            callback_data=(
                f"buy_manual_"
                f"{tariff}"
            ),
        )
    )
    bot.send_message(
        call.message.chat.id,
        "💳 **Способ оплаты:**",
        reply_markup=markup,
        parse_mode="Markdown",
    )


@bot.callback_query_handler(
    func=lambda c: c.data
    in [
        "buy_trial",
        "buy_stars_1m",
        "buy_stars_3m",
        "buy_stars_6m",
        "buy_stars_1y",
        "buy_stars_inf",
        "buy_manual_1m",
        "buy_manual_3m",
        "buy_manual_6m",
        "buy_manual_1y",
        "buy_manual_inf",
    ]
)
def payment_cb(call):
    bot.answer_callback_query(
        call.id
    )
    uid = call.from_user.id
    parts = call.data.split("_")
    if call.data == "buy_trial":
        if check_trial(uid) == 1:
            bot.send_message(
                call.message.chat.id,
                "❌ Вы уже брали тест!"
            )
            return
        days = get_trial_days()
        bot.send_message(
            call.message.chat.id,
            "⏳ Создаю линию..."
        )
        key, country = (
            get_happ_config()
        )
        if key:
            set_trial_used(uid)
            add_user_days(uid, days)
            bot.send_message(
                call.message.chat.id,
                f"🎉 Тест на "
                f"{days} дн.!\n"
                f"📍 Страна: "
                f"{country}\n\n"
                f"`{key}`",
                parse_mode="Markdown",
            )
        else:
            bot.send_message(
                call.message.chat.id,
                "❌ Ошибка линии."
            )
        return
    method = parts
    tariff = parts
    t_map = {
        "1m": (
            "1 мес", 50,
            "50 руб", 30
        ),
        "3m": (
            "3 мес", 85,
            "85 руб", 90
        ),
        "6m": (
            "6 мес", 150,
            "150 руб", 180
        ),
        "1y": (
            "1 год", 250,
            "250 руб", 365
        ),
        "inf": (
            "Навсегда", 500,
            "500 руб", 9999
        ),
    }
    name, star_p, rub_text, d = (
        t_map[tariff]
    )
    if method == "stars":
        prices = [
            types.LabeledPrice(
                label="Stars",
                amount=star_p,
            )
        ]
        bot.send_invoice(
            call.message.chat.id,
            title=f"VPN — {name}",
            description="Happ Premium",
            invoice_payload=f"vpn_{d}",
            provider_token="",
            currency="XTR",
            prices=prices,
            start_parameter="vpn-sub",
        )
    elif method == "manual":
        link = (
            "https://tbank.ru"
            "/rm/r_cOVTjCVpMV."
            "HLwIqatOdN/jbYw328360"
        )
        text = (
            f"💳 **Тариф {name}**\n"
            f"Цена: `{rub_text}`\n\n"
            f"1️⃣ Нажми на ссылку для "
            f"оплаты картой/СБП:\n"
            f"{link}\n\n"
            f"2️⃣ Переведи `{rub_text}`\n"
            f"3️⃣ Отправь чек в "
            f"поддержку: @{ADMIN_USER}\n"
            f"Админ проверит баланс и "
            f"сразу выдаст ключ! 🚀"
        )
        bot.send_message(
            call.message.chat.id,
            text,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )


@bot.pre_checkout_query_handler(
    func=lambda query: True
)
def precheck(q):
    bot.answer_pre_checkout_query(
        q.id, ok=True
    )


@bot.message_handler(
    content_types=[
        "successful_payment"
    ]
)
def success_pay(message):
    sp = (
        message
        .successful_payment
    )
    p = sp.invoice_payload
    d = int(p.split("_")[-1])
    uid = message.from_user.id
    add_user_days(uid, d)
    bot.send_message(
        message.chat.id,
        "⏳ Подключаю..."
    )
    key, country = (
        get_happ_config()
    )
    if key:
        bot.send_message(
            message.chat.id,
            f"🎉 Успешно!\n"
            f"🔑 Ключ ({country}):\n\n"
            f"`{key}`",
            parse_mode="Markdown",
        )


print("Бот запущен...")
threading.Thread(
    target=run_health_server,
    daemon=True,
).start()
bot.infinity_polling()
