from telebot import types

def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🎯 Vòng quay", "✈ Máy bay")
    kb.add("💎 Đập đá", "💰 Số dư")
    return kb

def admin_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("➕ Cộng điểm", "➖ Trừ điểm")
    return kb
