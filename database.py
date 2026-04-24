import aiosqlite
import datetime

DB_NAME = "clinic_bot.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        # User Language for i18n
        await db.execute('''
            CREATE TABLE IF NOT EXISTS user_language (
                user_id INTEGER PRIMARY KEY,
                language TEXT DEFAULT 'uz'
            )
        ''')
        # Users Table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Reviews Table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                service_name TEXT,
                rating INTEGER,
                review_text TEXT,
                review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        await db.commit()

async def get_user_language(user_id: int) -> str:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT language FROM user_language WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 'uz'

async def set_user_language(user_id: int, language: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT INTO user_language (user_id, language) 
            VALUES (?, ?) 
            ON CONFLICT(user_id) DO UPDATE SET language=excluded.language
        ''', (user_id, language))
        await db.commit()

async def register_user(user_id: int, username: str, first_name: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
        ''', (user_id, username, first_name))
        await db.commit()

async def save_review(user_id: int, service_name: str, rating: int, review_text: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT INTO reviews (user_id, service_name, rating, review_text) 
            VALUES (?, ?, ?, ?)
        ''', (user_id, service_name, rating, review_text))
        await db.commit()
