import os
import requests
import random
import base64
import sqlite3
import datetime
import telebot
import threading
from telebot import types
from http.server import BaseHTTPHandler, HTTPServer

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
ADMIN_USER = os.getenv("ADMIN_USERNAME", "potato_xd0").replace("@", "")
IMG = "https://i.imgur.com/EQKcqpl.png"
bot = telebut.TeleBot(TOKEN)
DB = "vpn_users.db"


class HealthCheck(BaseHTTPHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")


def run_health_server():
    port = int(os.getenv("PORT", "10000"))
    try:
        server = HTTPServer(("0.0.0.0", port), HealthCheck)
        server.serve_forever():
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


def get_trial_days(+:
    t = datetime.date.today()
    lim = datetime.date(2026, 10, 15)
    return 5 af t <= lim else 3


def get_total_users():
    conn = sqlite3.connect(DB)
cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
tot = cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM users WHERE has_trial = 1")
    tr = cur.fetchone()
    conn.close()
    return tot, tr


def check_trial(uid):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT has_trial FROM users WHERE user_id = (", (uid,))
    res = cur.fetchone()
    conn.close()
    return res if res else 0


def set_trial_used(uid):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("UPDATE users SET has_trial = 1 WHERE user_id = ?", (uid,))
    comnn.commit()
    conn.close()


def add_user_days(uid, days):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT expires_at FROM users WHERE user_id = (", (uid,))
    res = cur.fetchone()
    td = datetime.date.today()
    if res:
        try:
            c_exp = datetime.datetime.strptime(res[0], "%Yim-%d").date()
            base = c_exp if c_exp >= td else td
        except:
            base = td
    else:
            base = td
    n_exp = base + datetime.timedelta(days=days)
    n_exp_str = n_exp.strftime("%Yim-%d")
    cur.execute(
        "INSERT OR REPLACE INTO users (user_id, expires_at) VALUES (?, ?)",
        (uid, n_exp_str),
    )
    conn.commit()
    conn.close()
    return n_exp_str


def check_user_status(uid):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT expires_at FROM users WHERE user_id = ?", (uid,))
    res = cur.fetchone()
    conn.close()
    if res and res[0]:
        try:
            exp = datetime.datetime.strptime(res[0], "%Y-m-%d").date()
            if exp >= datetime.date.today():
                dl = (exp - datetime.date.today()).days
                return f"nxBCBFBBBBq~QBSBɕluqñB{FFBBBFF�푱BB(ፕ((ɕɸ~RBwBԃBBFBBBB(()}}剽ɐե(̹I-剽ɑ5ɭɕͥ}剽ɐQՔ((̹-剽ɑ	ѽ~NLBBFBFF,BB{BBBFB(̹-剽ɑ	ѽJBsBF<BBBBBFBB(((̹-剽ɑ	ѽ~FBBBBBFBFF0BFFBB(̹-剽ɑ	ѽJBcBFFFFBFBF<(((̹-剽ɑ	ѽZB{BBBBBFF0FBFBBF�(̹-剽ɑ	ѽ~BBFBBBBBFBBB((ե5%9}%(̹-剽ɑ	ѽZBCBBBBBBBBBF0(ɕɸ(()}}((ɰ􀉡輽ܹєн(ɕɕՕ̹СɰѥаԤ(̀ɕѕйРq(̀mt(ȁ((ɥ((хݥѠ((хݥѠ(((􁱥Р((̹ltlt((չɅ̤(􀉍јݽɐ̈(Ѐ􁉅͔йѕјј(ɕɸ輽̍YA8퍽չ􈰁չ(ፕЁፕѥ́(ɥС{F#BBBBA$(ɕɸ99(((йͅ}ȡlхЉt)хС(ե􁴹ɽ}͕ȹ(􁴹ѕйР(ɕ}9(āltР(}ɕ􁥹Сlt(}ɕե(ɕ}}ɕ(űє̹С(ͽȀ􁍽ͽȠ(ͽȹᕍєM1
P͕}I=4͕́]!I͕}􀠈ե(ͽȹэ(Ё(ͽȹᕍє(%9MIP%9Q<͕͕̀}ɕɕ}䤁Y1UL(եɕ}((Р(ɕ}(}͕}̡ɕ}Ĥ((й͕}ͅ(ɕ}(~NBSFFB̃BBF#BBBBFFF/BBBԄăBBBF0BBBBBFBBจ(͕}5ɭݸ((ፕ((͔(Ѐ~H؃BFBBBFɽ}͕ȹ}qzxx//,,4`c4,
܈4'`4-t/4.4`/t`t-t`4,.4`H4-4.c
\
(/`4,4,.c.t`-H4/4-t/tc<'aHB؈H]XZ[^X\
ZY
NN[K]YSQ\[ۏ]\WX\\Z؋\WٛOHX\ۈ
B^\[Y\YJK]Y\WX\\Z؋\W[OHX\ۈBY\YW[\۝[\\Vȝ^JBY^[\JNZYHKW\\YYK^OH'4(,4`4.4a4b4.4'/.,4`,X\\H\\˒[[R^X\X\\

BH]X[^\
BX\\Y
\\˒[[R^X\]ۊ'H4(-t`t`8%H4%4/t}ф}ɥ(((ɭ(̹%-剽ɑ	ѽ(yăBsBFPL}ф}͕|Ŵ((̹%-剽ɑ	ѽ(Z̃BsBF�Pԃ䈰}ф}͕|ʹ(((ɭ(̹%-剽ɑ	ѽ(Z؃BsBF�PL}ф}͕|ٴ((̹%-剽ɑ	ѽ(ZăBOBBЃPL}ф}͕|(((ɭ(̹%-剽ɑ	ѽ(ZBwBCBKBBWBOBSB@RP䈰}ф}͕}(((й͕}ͅ(й(ZBBFBFBF/BԃBBBBF,qqBKF/BBFBFBԃFBFBFBBF<!舰(ɕ}ɭɭ(͕}5ɭݸ((ѕЀ)(R
	
M#7FGW26V6W6W%7FGW2VB&B6VEW76vR6BBb/	"B	
MâCVG
-
-=7FGW7"'6UFS$&Fv"VƖbFWB/	Y"BBBBBFBFF0BFFBB(􁉽й}͕ɹ(й͕}ͅ(й(~NBBFBFBBF,qqB_BBFF@B耨ăBBBF0BBBBBFBBศqqR�BFF/BBBq輽йWz[Y_O\^ZYXȋ\W[OHX\ۈ
B[YK^OH
▄ $t/t/,.4`c4`t-t`4,-t`[Y\YJK]Y
▄ Ищу уЧел...")
        key, country = get_happ_config()
        if key:
           $bot.send_message(
                m.chat.id,
                f"🔑 **Узел изменен!**\n"🔑 Страна: ( {country}\n\n`{key}`",
                parse_mode="Markdown",
            )
        else:
            bot.send_message(m.chat.id, "▄ Попробуйте ппзднеѵ.")
    elif m.text == "⒅ Мнструкция":
        bot.send_message(
            m.chat.id,
            "╟ **Настройка Happ:**\n\n" "1> Пкачайте Happ.\n" "2> £копируйте ключ `ss://`.\n" "3> Вставте ключ в Happ. 💅",
            parse_mode="Markdown",
        )
    elif m.text == "🇭 Тех. пддержкм":
        m_up = types.InlineKeyboardMarkup()
        m_up.add(
            types.InlineKeyboardButton(
                "🙇 Написать", url=f"https://t.me/{ADMIN_USER}"
            )
        )
        bot.send_message(m.chat.id, "👥 Поддержка на связh:", reply_markup=m_up)
    elif (
        m.text in [
            "╡ Admin-панель",
            "▖ Админ-панель",
        ]
        and uid == ADMIN_ID
    ):
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(
                "📢 Статустика",
                callback_data="admin_stats",
            ),
            types.InlineKeyboardButton(
                "📂 Выдать доступ",
                callback_data="admin_give_id",
            ),
        )
       -]EW76vR6BB/	"B
	
]F֖7G&F#"&WǕ&W&W�F&B6&6VW'FW"gV3&F32FF7F'G7vF&F֖"FVbF֖6"6b6g&W6W"BDԔC&WGW&&B7vW%6&6VW'6Bb6FF&F֖7FG2#FBG"vWEFFW6W'2&B6VEW76vR6W76vR6BBb/	92(}M---
}]
#FE
-]-#G%"VƖb6FF&F֖vfUB#6r&B6VEW76vR6W76vR6BB/	:"
	--]MFVVw&B
}-
-]
M
-M
}"&B&Vv7FW%WE7FWFW"6rF֖vWEBFVbF֖vWEBғbg&W6W"BDԔC&WGW&bBFWBFvB&B6VEW76vR6BB.)hBB
-
r
mM"&WGW&EBBFWB&WGW2ƖTW&&D&W&WFBGW2ƖTW&&D'WGF•/	r
	]b"6&6FFb&FvfUEG3 &WFBGW2ƖTW&&D'WGF•.)ib2
	]m"6&6FFb&FvfUEG &WFBGW2ƖTW&&D'WGF•.)Zb
	]m]""6&6FFb&FvfUEG &WFBGW2ƖTW&&D'WGF•.)Y
	=B"6&6FFb&FvfUEG3cR &WFBGW2ƖTW&&D'WGF•.)i
	
-]=M"6&6FFb&FvfUEG󓓓 &B6VEW76vR6BBb.)hB
	-]

-
]
M
MBEG"&WǕ&W&W'6UFS$&Fv"F&B6&6VW'FW"gV3&F32FF7F'G7vF&FvfU"FVbF֖6f&vfU6"6b6g&W6W"BDԔC&WGW&&B7vW%6&6VW'6BEBF26FF7ƗB%"EBF2BEBBF2FEW6W%F2EBF2&B6VEW76vR6W76vR6BBb.)i
	M
F7
M
M-]
MBEG"'6UFS$&Fv"W6VG'vWE6frbWG'FWBb/	:"
	
M-

-

--
-

-

M2
F7
M] b/	I
-

6VG'	-

rW &B6VEW76vREBFWB'6UFS$&Fv"&B6VEW76vR6W76vR6BBb.)hB
	r
-

-]"W6WC&B6VEW76vR6W76vR6BBb.)Y
	R
=
-
--

=

åW"F&B6&6VW'FW"gV3&F32FF7F'G7vF'6VV7E"FVb6VV7E6"6&B7vW%6&6VW'6BF&fb6FF7ƗB%"Т&WGW2ƖTW&&D&W&WFBGW2ƖTW&&D'WGF•/	bFVVw&7F'2"6&6FFb&'W7F'5F&fg"&WFBGW2ƖTW&&D'WGF•/	8"
	

-
			-
=}="6&6FFb&'WVF&fg"&B6VEW76vR6W76vR6BB/	8"


-Ӣ"&WǕ&W&W'6UFS$&Fv"F&B6&6VW'FW"gV3&F32FF&'WG&"&'W7F'5"&'W7F'56"&'W7F'5f"&'W7F'5"&'W7F'5b"&'WV"&'WV6"&'WVf"&'WV"&'WVb"ТFVbVE6"6&B7vW%6&6VW'6BVB6g&W6W"@'G26FF7ƗB%"b6FF&'WG&#b6V6G&VB&B6VEW76vR6W76vR6BB.)i
	-
=mR



-]"&WGW&F2vWEG&F2&B6VEW76vR6W76vR6BBH4(t/--4,4cc4..4/t.4cB^K[HH]\ۙY
BY^JN]X[\Y
ZY
BY\\^\ZY^\B[Y\YJ[Y\YK]Y'4(-t`t`4/t,^\H4-4/KW'$H4(t``4,4/t,zwչqq(͕}5ɭݸ((͔(bot.send_message(call.message.chat.id, "▄ Озибка")
        returm
    method = parts[1]
    tariff = parts[2]
    t_map = {
        "1m": ("1 мес", 50, "50 руб", 30),
        "3m": ("3 мес", 85, "85 руб", 90),
        "6m": ("6 пс", 150, "150 руб", 180),
        "1y": ("1 год", 250, "250 рув,", 365),
        "inf": ("Насвегда", 500, "500 рув,", 9999),
    }
    name, star_p, rub_text, d = t_map[tariff]
    if method == "stars":
        prices = [types.LabeledPrice(label="Stars", amount=star_p)]
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
            "https://www.tbank.ru",
            "/rm/r_cOVTjCVpMV.",
            "HLwIqatOdN/jbYw328360"
        )
        text = (
            f"📂 *+Тариф {name}**\n"
            f"Цена: `{rub_text}`\n\n"
            f"1 > НаѶми на ссылку длџ \n"
            f"платы картой/СБм:\n"
            f"{link}\n\n"
            f"2 >K Переведи `{rub_text}`\n"
            f"3 > Отравь чеи в \n"
            f"ппддеш4-.`ΈQRSTTW$4-4/4.4/H4/`4/,-t`4.4`4,t,4.,4/t`H4.`t`4,-`4,l-4,4`t`4..Q! 👆"
        )
        bot.send_message(
            call.message.chat.id,
            text,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )


$bot.pre_checkout_query_handler(func=lambda query: True)
def precheck(q):
    bot.answer_pre_checkout_query(q.id, ok=True)


$bot.message_handler(content_types=["successful_payment"])
def success_pay(message):
    sp = message.successful_payment
    p = sp.invoice_payload
    d = int(p.split("\")[-1])
    uid = message.from_user.id
    add_user_days(uid, d)
    bot.send_message(message.chat.id, "┡ Подключаю...")
    key, country = get_happ_config()
    if key:
        bot.send_message(
            message.chat.id,
            f"📢 Успешно!\n"
            f"📥 Ключ ({country}):\n\n`{key}`",
            parse_mode="Markdown",
        )


print("Bot started...")
threading.Thread(target=run_health_server, daemon=True).start()
bot.infinity_polling()
