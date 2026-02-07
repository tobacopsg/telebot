import aiosqlite

DB_NAME = "database.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 0,
            referrals INTEGER DEFAULT 0
        )
        """)
        await db.commit()

async def add_user(uid):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (uid,))
        await db.commit()

async def get_balance(uid):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT balance FROM users WHERE user_id=?", (uid,))
        row = await cur.fetchone()
        return row[0] if row else 0

async def add_balance(uid, amount):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, uid))
        await db.commit()

