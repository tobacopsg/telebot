import sqlite3

conn = sqlite3.connect("data.db", check_same_thread=False)
cur = conn.cursor()

def init_db():
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        balance INTEGER DEFAULT 1000
    )""")
    conn.commit()

def get_user(uid):
    cur.execute("SELECT * FROM users WHERE user_id=?", (uid,))
    if not cur.fetchone():
        cur.execute("INSERT INTO users(user_id) VALUES(?)", (uid,))
        conn.commit()

def get_balance(uid):
    cur.execute("SELECT balance FROM users WHERE user_id=?", (uid,))
    return cur.fetchone()[0]

def set_balance(uid, bal):
    cur.execute("UPDATE users SET balance=? WHERE user_id=?", (bal, uid))
    conn.commit()



