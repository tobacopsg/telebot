import telebot
from config import BOT_TOKEN, ADMIN_ID
from db import init_db, get_user, get_balance, set_balance
from ui.keyboards import main_menu, admin_menu
from core.games import spin, plane, stone

bot = telebot.TeleBot(BOT_TOKEN)
init_db()

@bot.message_handler(commands=['start'])
def start(msg):
    uid = msg.from_user.id
    get_user(uid)
    bot.send_message(uid, "🤖 BOT GAME TELEGRAM VIP", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "💰 Số dư")
def bal(msg):
    uid = msg.from_user.id
    bot.send_message(uid, f"💰 Bạn có: {get_balance(uid):,} COIN")

@bot.message_handler(func=lambda m: m.text == "🎯 Vòng quay")
def game_spin(msg):
    prize = spin(msg.from_user.id)
    bot.send_message(msg.chat.id, f"🎉 Bạn nhận: {prize} COIN")

@bot.message_handler(func=lambda m: m.text == "✈ Máy bay")
def game_plane(msg):
    rate = plane()
    bot.send_message(msg.chat.id, f"✈ Máy bay bay tới x{rate}")

@bot.message_handler(func=lambda m: m.text == "💎 Đập đá")
def game_stone(msg):
    prize = stone(msg.from_user.id)
    bot.send_message(msg.chat.id, f"💎 Nhận: {prize} COIN")

@bot.message_handler(commands=['admin'])
def admin(msg):
    if msg.from_user.id == ADMIN_ID:
        bot.send_message(msg.chat.id, "⚙ ADMIN PANEL", reply_markup=admin_menu())

@bot.message_handler(func=lambda m: m.text == "➕ Cộng điểm")
def add_coin(msg):
    if msg.from_user.id != ADMIN_ID: return
    m2 = bot.send_message(msg.chat.id, "Nhập: ID | COIN")
    bot.register_next_step_handler(m2, process_add)

def process_add(msg):
    try:
        uid, coin = msg.text.split("|")
        uid = int(uid)
        coin = int(coin)
        bal = get_balance(uid)
        set_balance(uid, bal + coin)
        bot.send_message(msg.chat.id, "✅ Cộng điểm thành công")
    except:
        bot.send_message(msg.chat.id, "❌ Sai định dạng")

print("BOT RUNNING...")
bot.infinity_polling()


