import aiosqlite

DB_NAME = "database.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 0,
            bank_name TEXT,
            bank_stk TEXT,
            bank_owner TEXT
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS deposit_bank (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bank_name TEXT,
            bank_stk TEXT,
            bank_owner TEXT,
            content TEXT
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

async def set_bank(uid, bank, stk, owner):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE users SET bank_name=?, bank_stk=?, bank_owner=? WHERE user_id=?",
            (bank, stk, owner, uid)
        )
        await db.commit()

async def get_bank(uid):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute(
            "SELECT bank_name, bank_stk, bank_owner FROM users WHERE user_id=?",
            (uid,)
        )
        return await cur.fetchone()

async def set_deposit_bank(bank, stk, owner, content):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM deposit_bank")
        await db.execute("""
            INSERT INTO deposit_bank (bank_name, bank_stk, bank_owner, content)
            VALUES (?, ?, ?, ?)
        """, (bank, stk, owner, content))
        await db.commit()

async def get_deposit_bank():
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT bank_name, bank_stk, bank_owner, content FROM deposit_bank LIMIT 1")
        return await cur.fetchone()



