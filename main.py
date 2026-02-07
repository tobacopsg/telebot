import random
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
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

admin_menu = ReplyKeyboardMarkup(resize_keyboard=True)
admin_menu.add("⚙️ Cập nhật ngân hàng nạp")

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await db.add_user(msg.from_user.id)
    await msg.answer("🤖 BOT TÀI CHÍNH\n1 điểm = 1.000 VNĐ", reply_markup=menu)
    if msg.from_user.id in ADMINS:
        await msg.answer("⚙️ MENU ADMIN", reply_markup=admin_menu)

@dp.message_handler(commands=["bank"])
async def set_bank_cmd(msg: types.Message):
    await msg.answer("🏦 Nhập ngân hàng theo mẫu:\nNgân hàng | STK | Tên chủ TK")

@dp.message_handler(lambda m: "|" in m.text and len(m.text.split("|")) == 3)
async def save_bank(msg: types.Message):
    bank, stk, owner = [x.strip() for x in msg.text.split("|")]
    await db.set_bank(msg.from_user.id, bank, stk, owner)
    await msg.answer("✅ Đã lưu thông tin ngân hàng")

@dp.message_handler(lambda m: m.text == "⚙️ Cập nhật ngân hàng nạp")
async def admin_deposit_bank(msg: types.Message):
    if msg.from_user.id not in ADMINS: return
    await msg.answer("Nhập:\nNgân hàng | STK | Tên chủ TK | Nội dung CK")

@dp.message_handler(lambda m: "|" in m.text and len(m.text.split("|")) == 4)
async def save_deposit_bank(msg: types.Message):
    if msg.from_user.id not in ADMINS: return
    bank, stk, owner, content = [x.strip() for x in msg.text.split("|")]
    await db.set_deposit_bank(bank, stk, owner, content)
    await msg.answer("✅ Đã cập nhật ngân hàng nạp tiền")

@dp.message_handler(lambda m: m.text == "📊 Số dư")
async def balance(msg):
    bal = await db.get_balance(msg.from_user.id)
    await msg.answer(f"💰 Số dư: {bal} điểm (~{bal*1000:,} VNĐ)")

@dp.message_handler(lambda m: m.text == "📅 Điểm danh")
async def checkin(msg):
    reward = random.randint(20,50)
    await db.add_balance(msg.from_user.id, reward)
    await msg.answer(f"🎁 +{reward} điểm")

@dp.message_handler(lambda m: m.text == "👥 Mời bạn")
async def invite(msg):
    link = f"https://t.me/{(await bot.get_me()).username}?start={msg.from_user.id}"
    await msg.answer(f"👥 Link mời:\n{link}\n+99 điểm")

@dp.message_handler(lambda m: m.text == "🏆 Đua top")
async def top(msg):
    names = ["Minh Anh","Gia Huy","Tuấn Kiệt","Quốc Bảo","Thanh Tùng","Khánh Duy","Đức Anh","Quang Hưng","Hoàng Long","Hải Hoàng"]
    random.shuffle(names)
    text="🏆 BXH ĐUA TOP\n\n"
    for i,n in enumerate(names[:10],1):
        money=random.randint(5,50)*1_000_000
        text+=f"{i}. {n} — {money:,}đ\n"
    await msg.answer(text)

@dp.message_handler(lambda m: m.text == "💰 Nạp tiền")
async def deposit(msg):
    info = await db.get_deposit_bank()
    if not info:
        return await msg.answer("⚠️ Admin chưa cập nhật ngân hàng nạp")
    bank, stk, owner, content = info

    kb=InlineKeyboardMarkup().add(
        InlineKeyboardButton("✅ Đã chuyển tiền",callback_data=f"paid_{msg.from_user.id}")
    )

    await msg.answer(
        f"💰 NẠP TIỀN\n\n"
        f"🏦 {bank}\n💳 {stk}\n👤 {owner}\n\n"
        f"📝 Nội dung: {content}",
        reply_markup=kb
    )

@dp.callback_query_handler(lambda c: c.data.startswith("paid_"))
async def paid(call):
    uid=int(call.data.split("_")[1])
    for admin in ADMINS:
        kb=InlineKeyboardMarkup().add(
            InlineKeyboardButton("✅ Duyệt +100",callback_data=f"nap_{uid}")
        )
        await bot.send_message(admin,f"💰 YÊU CẦU NẠP\nUser: {uid}",reply_markup=kb)
    await call.message.answer("⏳ Chờ admin duyệt")

@dp.callback_query_handler(lambda c: c.data.startswith("nap_"))
async def approve_nap(call):
    uid=int(call.data.split("_")[1])
    await db.add_balance(uid,100)
    await bot.send_message(uid,"✅ Nạp thành công +100 điểm")
    await call.message.edit_text("✔️ Đã duyệt")

@dp.message_handler(lambda m: m.text == "💸 Rút tiền")
async def withdraw(msg):
    bank = await db.get_bank(msg.from_user.id)
    if not bank or not bank[0]:
        return await msg.answer("⚠️ Chưa nhập ngân hàng\nGõ /bank")
    await msg.answer("💸 Nhập số điểm muốn rút (20–200)")

@dp.message_handler(lambda m: m.text.isdigit())
async def withdraw_amount(msg):
    amount=int(msg.text)
    if amount<20 or amount>200:
        return await msg.answer("❌ 20–200")

    bal=await db.get_balance(msg.from_user.id)
    if bal<amount:
        return await msg.answer("❌ Không đủ số dư")

    bank=await db.get_bank(msg.from_user.id)
    bank_name,stk,owner=bank

    for admin in ADMINS:
        kb=InlineKeyboardMarkup().add(
            InlineKeyboardButton("✅ Duyệt rút",callback_data=f"rut_{msg.from_user.id}_{amount}")
        )
        await bot.send_message(
            admin,
            f"💸 YÊU CẦU RÚT\nUser: {msg.from_user.id}\nSố điểm: {amount}\n\n"
            f"🏦 {bank_name}\n💳 {stk}\n👤 {owner}",
            reply_markup=kb
        )

    await msg.answer("⏳ Chờ admin duyệt")

@dp.callback_query_handler(lambda c: c.data.startswith("rut_"))
async def approve_rut(call):
    _,uid,amount=call.data.split("_")
    uid=int(uid);amount=int(amount)
    await db.add_balance(uid,-amount)
    await bot.send_message(uid,f"✅ Rút thành công -{amount} điểm")
    await call.message.edit_text("✔️ Đã duyệt")

@dp.message_handler(lambda m: m.text=="🎯 Nhiệm vụ")
async def mission(msg):
    await msg.answer("🎯 Trả lời câu hỏi (sắp nâng cấp AI)")

@dp.message_handler(lambda m: m.text=="🎁 Sự kiện")
async def event(msg):
    await msg.answer(
        "🎁 KHUYẾN MÃI\n\n"
        "🆕 Tân thủ 3 ngày\n"
        "🏆 Đua top nạp\n"
        "👥 Đua top mời\n"
        "💎 Nạp >2000 điểm/tuần +30%"
    )

async def on_startup(_):
    await db.init_db()

if __name__=="__main__":
    executor.start_polling(dp,on_startup=on_startup)

