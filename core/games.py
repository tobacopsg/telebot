import random
from db import get_balance, set_balance

def spin(uid):
    prize = random.choice([0, 100, 200, 500, 1000])
    bal = get_balance(uid)
    set_balance(uid, bal + prize)
    return prize

def plane():
    return round(random.uniform(1.0, 5.0), 2)

def stone(uid):
    prize = random.choice([0, 50, 200, 500])
    bal = get_balance(uid)
    set_balance(uid, bal + prize)
    return prize
