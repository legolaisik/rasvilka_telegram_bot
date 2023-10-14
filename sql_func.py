import asyncio
import sqlite3

# Проверка наличия юзера
async def db_check_user(user_id, conn: sqlite3.Connection):
    try:
        if conn.cursor().execute("SELECT * FROM users where telegram_id = ?", (user_id,)).fetchone() != None:
            return True
        else:
            return False
    except:
        return False
            
# Создание юзера
async def db_create_user(user_id, conn: sqlite3.Connection):
    try:
        conn.cursor().execute("INSERT INTO users (telegram_id) VALUES (?)", (str(user_id), ))
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
    
async def db_get_profile(profile_id, conn: sqlite3.Connection):
    profile_row = conn.cursor().execute("SELECT * FROM profiles WHERE profile_id = ?", (profile_id,)).fetchone()
    if profile_row != None:
        return profile_row
    else:
        return False
