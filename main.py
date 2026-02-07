import sqlite3, random, asyncio, time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import config

db = sqlite3.connect("db.sqlite3", check_same_thread=False)
c = db.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance REAL DEFAULT 0,
    last_checkin INTEGER DEFAULT 0,
    ref_by INTEGER DEFAULT 0,
    total_deposit REAL DEFAULT 0,
    deposit_count INTEGER DEFAULT 0
)""")

c.execute("""CREATE TABLE IF NOT EXISTS banks (
    user_id INTEGER PRIMARY KEY,
    bank TEXT,
    stk TEXT,
    name TEXT
)""")

db.commit()

def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Nạp tiền", callback_data="deposit"),
         InlineKeyboardButton("💸 Rút tiền", callback_data="withdraw")],
        [InlineKeyboardButton("📅 Điểm danh", callback_data="checkin"),
         InlineKeyboardButton("👥 Mời bạn", callback_data="invite")],
        [InlineKeyboardButton("🎯 Nhiệm vụ", callback_data="task"),
         InlineKeyboardButton("🏆 Đua top", callback_data="top")],
        [InlineKeyboardButton("🎁 Sự kiện", callback_data="event"),
         InlineKeyboardButton("⚙️ Ngân hàng", callback_data="bank")],
        [InlineKeyboardButton("🎮 Game", callback_data="game"),
         InlineKeyboardButton("📊 Số dư", callback_data="balance")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    c.execute("INSERT OR IGNORE INTO users(user_id) VALUES(?)",(uid,))
    db.commit()
    await update.message.reply_text("🎮 BOT GIẢI TRÍ TÀI CHÍNH ẢO", reply_markup=menu())

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id

    if q.data == "balance":
        c.execute("SELECT balance FROM users WHERE user_id=?", (uid,))
        bal = c.fetchone()[0]
        await q.edit_message_text(f"💰 Số dư: {bal:.2f} USD", reply_markup=menu())

    elif q.data == "checkin":
        now = int(time.time())
        c.execute("SELECT last_checkin FROM users WHERE user_id=?", (uid,))
        last = c.fetchone()[0]
        if now - last < 86400:
            await q.edit_message_text("❌ Bạn đã điểm danh hôm nay!", reply_markup=menu())
            return

        reward = round(random.uniform(1,5),2)
        c.execute("UPDATE users SET balance = balance + ?, last_checkin=? WHERE user_id=?", (reward, now, uid))
        db.commit()
        await q.edit_message_text(f"🎁 Bạn nhận {reward} USD!", reply_markup=menu())

    elif q.data == "deposit":
        context.user_data["wait_deposit"] = True
        await q.edit_message_text("💰 Nhập số USD muốn nạp:")

    elif q.data == "withdraw":
        c.execute("SELECT balance FROM users WHERE user_id=?", (uid,))
        bal = c.fetchone()[0]
        if bal < 5:
            await q.edit_message_text("❌ Số dư không đủ để rút!", reply_markup=menu())
            return
        context.user_data["wait_withdraw"] = True
        await q.edit_message_text("💸 Nhập số USD muốn rút (5 - 10):")

    elif q.data == "bank":
        context.user_data["set_bank"] = 1
        await q.edit_message_text("🏦 Nhập tên ngân hàng:")

    elif q.data == "game":
        await q.edit_message_text("🎮 Game đang phát triển...")

    else:
        await q.edit_message_text("⏳ Đang cập nhật...")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    txt = update.message.text

    if context.user_data.get("wait_deposit"):
        usd = float(txt)
        vnd = int(usd * config.USD_TO_VND)
        context.user_data["wait_deposit"] = False

        c.execute("SELECT deposit_count FROM users WHERE user_id=?", (uid,))
        count = c.fetchone()[0]

        bonus = 0
        if count == 0: bonus = usd
        elif count == 1: bonus = usd * 0.5
        elif count == 2: bonus = usd * 0.25

        total = usd + bonus

        c.execute("UPDATE users SET balance=balance+?, deposit_count=deposit_count+1 WHERE user_id=?", (total, uid))
        db.commit()

        await update.message.reply_text(
            f"✅ Nạp thành công!\n💰 Nhận: {total:.2f} USD (thưởng {bonus:.2f})",
            reply_markup=menu()
        )

    elif context.user_data.get("wait_withdraw"):
        usd = float(txt)
        if usd < 5 or usd > 10:
            await update.message.reply_text("❌ Mức rút không hợp lệ!", reply_markup=menu())
            return

        c.execute("SELECT balance FROM users WHERE user_id=?", (uid,))
        bal = c.fetchone()[0]
        if bal < usd:
            await update.message.reply_text("❌ Không đủ số dư!", reply_markup=menu())
            return

        c.execute("UPDATE users SET balance=balance-? WHERE user_id=?", (usd, uid))
        db.commit()

        await update.message.reply_text(f"✅ Rút thành công {usd} USD", reply_markup=menu())

    elif context.user_data.get("set_bank") == 1:
        context.user_data["bank"] = txt
        context.user_data["set_bank"] = 2
        await update.message.reply_text("💳 Nhập STK:")

    elif context.user_data.get("set_bank") == 2:
        context.user_data["stk"] = txt
        context.user_data["set_bank"] = 3
        await update.message.reply_text("👤 Nhập tên thụ hưởng:")

    elif context.user_data.get("set_bank") == 3:
        bank = context.user_data["bank"]
        stk = context.user_data["stk"]
        name = txt
        c.execute("REPLACE INTO banks VALUES(?,?,?,?)",(uid,bank,stk,name))
        db.commit()
        context.user_data.clear()
        await update.message.reply_text("✅ Cập nhật ngân hàng thành công!", reply_markup=menu())

async def main():
    app = ApplicationBuilder().token(config.TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("BOT ĐANG CHẠY...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
