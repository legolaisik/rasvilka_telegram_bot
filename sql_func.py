import asyncio
import sqlite3

# Проверка наличия юзера
async def db_check_user(user_id, conn):
    try:
        conn.cursor().execute("SELECT telegram_id FROM users where telegram_id = ?",(user_id))
        result = conn.cursor().fetchone()
        if result == False:
            return False
        else:
            return True
    except:
        return False
            

# Создание юзера
async def db_create_user(user_id, conn):
    try:
        conn.cursor().execute("INSERT INTO users (telegram_id) VALUES (?)", (user_id))
        conn.commit()
        return True
    except:
        return False
        
# Создание профиля
async def db_create_profile(user_id, conn, **kwargs):
    try:
        conn.cursor().execute()
    except:
        return False 
    
# Получение профилей для юзера
async def db_get_user_profiles(user_id, conn: sqlite3.Connection):
    try:
        conn.cursor().execute("SELECT profile_name FROM profiles WHERE telegram_id = ?", (user_id))
        return conn.cursor().fetchone()
    except:
        return False
    
    
async def get_profile(profile_id, conn: sqlite3.Connection):
    profile_row = conn.cursor().execute("SELECT * FROM profiles WHERE profile_id = ?", (profile_id,)).fetchone()
    if profile_row != None:
        return profile_row
    else:
        return False
