import random
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, ADMINS
import db

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
menu.add(
    "💰 Nạp tiền", "💸 Rút tiền",
    "📅 Điểm danh", "👥 Mời bạn",
    "🎯 Nhiệm vụ", "🏆 Đua top",
    "🎁 Sự kiện", "📊 Số dư"
)

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await db.add_user(msg.from_user.id)
    await msg.answer("🤖 Bot tài chính mô hình điểm → tiền\n1 điểm = 1.000 VNĐ", reply_markup=menu)

@dp.message_handler(lambda m: m.text == "📊 Số dư")
async def balance(msg: types.Message):
    bal = await db.get_balance(msg.from_user.id)
    await msg.answer(f"💰 Số dư: {bal} điểm (~{bal*1000:,} VNĐ)")

@dp.message_handler(lambda m: m.text == "📅 Điểm danh")
async def checkin(msg: types.Message):
    reward = random.randint(20, 50)
    await db.add_balance(msg.from_user.id, reward)
    await msg.answer(f"🎁 Điểm danh thành công\n+{reward} điểm")

@dp.message_handler(lambda m: m.text == "👥 Mời bạn")
async def invite(msg: types.Message):
    link = f"https://t.me/{(await bot.get_me()).username}?start={msg.from_user.id}"
    await msg.answer(f"👥 Link mời bạn:\n{link}\n\n🎁 Mỗi lượt +99 điểm")

@dp.message_handler(lambda m: m.text == "🏆 Đua top")
async def leaderboard(msg: types.Message):
    names = ["Minh Anh","Gia Huy","Tuấn Kiệt","Quốc Bảo","Thanh Tùng","Khánh Duy","Đức Anh","Quang Hưng","Hoàng Long"]
    names.append("Hải Hoàng")
    random.shuffle(names)
    names = names[:10]

    text = "🏆 BXH ĐUA TOP NẠP TIỀN HÔM NAY\n\n"
    for i,n in enumerate(names,1):
        money = random.randint(5,50) * 1_000_000
        text += f"{i}. {n} — {money:,}đ\n"

    text += "\n🥇 1000đ | 🥈 500đ | 🥉 250đ"
    await msg.answer(text)

@dp.message_handler(lambda m: m.text == "💰 Nạp tiền")
async def deposit(msg: types.Message):
    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton("✅ Đã chuyển tiền", callback_data=f"paid_{msg.from_user.id}"),
        InlineKeyboardButton("❌ Hủy", callback_data="cancel")
    )
    await msg.answer(
        "💰 NẠP TIỀN\n\n"
        "MB Bank\nSTK: 0123456789\nTên: HẢI HOÀNG\n\n"
        "Nội dung:\nck.bot,moneymind.7898624\n\n"
        "Sau khi chuyển bấm:",
        reply_markup=kb
    )

@dp.callback_query_handler(lambda c: c.data.startswith("paid_"))
async def paid(call: types.CallbackQuery):
    uid = int(call.data.split("_")[1])
    for admin in ADMINS:
        kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton("✅ Duyệt +100 điểm", callback_data=f"approve_{uid}")
        )
        await bot.send_message(admin, f"💰 YÊU CẦU NẠP TIỀN\nUser: {uid}", reply_markup=kb)
    await call.message.answer("⏳ Đã gửi admin duyệt")

@dp.callback_query_handler(lambda c: c.data.startswith("approve_"))
async def approve(call: types.CallbackQuery):
    uid = int(call.data.split("_")[1])
    await db.add_balance(uid, 100)
    await bot.send_message(uid, "✅ Nạp thành công +100 điểm")
    await call.message.edit_text("✔️ Đã duyệt")

@dp.message_handler(lambda m: m.text == "💸 Rút tiền")
async def withdraw(msg: types.Message):
    await msg.answer("💸 Nhập số điểm muốn rút (20–200):")

@dp.message_handler(lambda m: m.text.isdigit())
async def withdraw_amount(msg: types.Message):
    amount = int(msg.text)
    if amount < 20 or amount > 200:
        return await msg.answer("❌ Giới hạn: 20–200")

    bal = await db.get_balance(msg.from_user.id)
    if bal < amount:
        return await msg.answer("❌ Không đủ số dư")

    for admin in ADMINS:
        kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton("✅ Duyệt rút", callback_data=f"wd_{msg.from_user.id}_{amount}")
        )
        await bot.send_message(admin, f"💸 YÊU CẦU RÚT\nUser: {msg.from_user.id}\nSố điểm: {amount}", reply_markup=kb)

    await msg.answer("⏳ Chờ admin duyệt")

@dp.callback_query_handler(lambda c: c.data.startswith("wd_"))
async def approve_withdraw(call: types.CallbackQuery):
    _, uid, amount = call.data.split("_")
    uid, amount = int(uid), int(amount)

    await db.add_balance(uid, -amount)
    await bot.send_message(uid, f"✅ Rút thành công -{amount} điểm")
    await call.message.edit_text("✔️ Đã duyệt rút")

@dp.message_handler(lambda m: m.text == "🎯 Nhiệm vụ")
async def mission(msg: types.Message):
    await msg.answer("🎯 Trả lời 10 câu hỏi\nĐúng +10 | Sai -30\n(Đang tích hợp AI)")

@dp.message_handler(lambda m: m.text == "🎁 Sự kiện")
async def event(msg: types.Message):
    await msg.answer(
        "🎁 SỰ KIỆN & KHUYẾN MÃI\n\n"
        "🆕 Tân thủ: +100% → +50% → +30%\n"
        "🏆 Đua top nạp\n"
        "👥 Đua top mời bạn\n"
        "💎 Nạp >2000 điểm/tuần +30%"
    )

async def on_startup(_):
    await db.init_db()

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
