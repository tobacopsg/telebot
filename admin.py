from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def admin_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Cập nhật ngân hàng", callback_data="admin_bank")],
        [InlineKeyboardButton("📊 Xem thống kê", callback_data="admin_stats")]
    ])
