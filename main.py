import asyncio
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram import Update
from config import BOT_TOKEN, ADMIN_ID
from db import init_db
from core.wallet import get_balance, add_balance, sub_balance
from core.user import create_user
from core.games import *
from ui.keyboards import main_menu, game_menu

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await create_user(user.id)
    await update.message.reply_text(
        f"🎉 Chào mừng {user.first_name}\n💼 Bot Game Simulator Cao Cấp",
        reply_markup=main_menu()
    )

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "balance":
        bal = await get_balance(q.from_user.id)
        await q.edit_message_text(f"💰 Số dư: {bal:.2f} USD", reply_markup=main_menu())

    elif q.data == "games":
        await q.edit_message_text("🎮 Chọn trò chơi", reply_markup=game_menu())

    elif q.data == "g_plane":
        win = plane_game(1)
        if win > 1:
            await add_balance(q.from_user.id, win)
            await q.edit_message_text(f"✈️ Thắng {win:.2f} USD", reply_markup=main_menu())
        else:
            await q.edit_message_text("💥 Máy bay rơi", reply_markup=main_menu())

    elif q.data == "g_slot":
        win = slot_game()
        if win:
            await add_balance(q.from_user.id, win)
            await q.edit_message_text(f"🎰 Trúng {win:.2f} USD", reply_markup=main_menu())
        else:
            await q.edit_message_text("🎰 Không trúng", reply_markup=main_menu())

    elif q.data == "g_even":
        if even_odd():
            await add_balance(q.from_user.id, 1.85)
            await q.edit_message_text("🎯 Thắng 1.85 USD", reply_markup=main_menu())
        else:
            await q.edit_message_text("🎯 Thua", reply_markup=main_menu())

    elif q.data == "g_mine":
        win = mine_game()
        await add_balance(q.from_user.id, win)
        await q.edit_message_text(f"⛏ Đào được {win:.2f} USD", reply_markup=main_menu())

    elif q.data == "g_ball":
        win = football_game(3)
        if win:
            await add_balance(q.from_user.id, win)
            await q.edit_message_text(f"⚽ Ghi bàn: +{win} USD", reply_markup=main_menu())
        else:
            await q.edit_message_text("⚽ Sút hỏng", reply_markup=main_menu())

async def main():
    await init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback))

    print("BOT RUNNING...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
