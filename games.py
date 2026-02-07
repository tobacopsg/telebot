import random

def plane_game(bet):
    if bet < 1:
        return random.uniform(1.5, 10)
    return random.uniform(0, 3)

def slot_game():
    r = random.random()
    if r < 0.05:
        return 1000
    elif r < 0.2:
        return random.uniform(2, 20)
    return 0

def even_odd():
    return random.random() < 0.3

def mine_game():
    return random.uniform(0.5, 2)

def football_game(step):
    if random.random() < 0.4:
        return 2 ** step
    return 0
