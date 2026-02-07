from db import get_balance

def balance_text(uid):
    bal = get_balance(uid)
    return f"💰 Số dư: {bal:,} COIN"
