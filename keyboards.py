from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Số dư", callback_data="balance")],
        [InlineKeyboardButton("🎮 Game", callback_data="games")],
        [InlineKeyboardButton("🎯 Nhiệm vụ", callback_data="tasks")],
        [InlineKeyboardButton("👥 Mời bạn", callback_data="ref")],
        [InlineKeyboardButton("💳 Nạp tiền", callback_data="deposit")],
        [InlineKeyboardButton("🏧 Rút tiền", callback_data="withdraw")],
    ])

def game_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✈️ Phi công", callback_data="g_plane")],
        [InlineKeyboardButton("🎰 Slot", callback_data="g_slot")],
        [InlineKeyboardButton("🎯 Chẵn lẻ", callback_data="g_even")],
        [InlineKeyboardButton("⛏ Đào đá", callback_data="g_mine")],
        [InlineKeyboardButton("⚽ Sút bóng", callback_data="g_ball")],
    ])
