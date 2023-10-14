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
    except Exception as e:
        print(e)
        return False
    
async def db_set_primary_profile(user_id, conn: sqlite3.Connection, name):
    try:
        conn.cursor().execute('''UPDATE users set active_profile = 
                              (select profile_id from profiles where telegram_id = ? and profile_name = ? limit 1)''', (str(user_id), name,))
        conn.commit()
        return True
    except:
        return False   
    
async def db_delete_current_profile(user_id, conn: sqlite3.Connection):
    try:
        conn.cursor().execute('''delete from profiles where profile_id = (select active_profile from users where telegram_id = ?) ''', (str(user_id),))
        conn.cursor().execute('''UPDATE users set active_profile = 
                              (select profile_id from profiles where telegram_id = ? limit 1)''', (str(user_id),))
        conn.commit()
        return True
    except:
        return False 
        
# Создание профиля
async def db_create_profile(user_id, conn: sqlite3.Connection, data):
    try:
        conn.cursor().execute("""INSERT INTO profiles (telegram_id, profile_name, salary, skills, education, expirience, jobtime, jobtype, city) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                              (str(user_id), data['enter_profile_name'], data['enter_salary'], data['enter_skills'], data['enter_education'], data['enter_experience'], data['enter_jobtime'], data['enter_jobtype'], '2'))
        conn.cursor().execute('''UPDATE users set active_profile = 
                              (select profile_id from profiles where telegram_id = ? and profile_name = ? limit 1)''', (str(user_id), data['enter_profile_name'],))
        conn.commit()
    except Exception as e:
        print(e)
        return False     
    
async def db_get_profile(user_id, conn: sqlite3.Connection):
    profile_row = conn.cursor().execute("""SELECT * FROM profiles WHERE 
                                        profile_id = (select active_profile from users where telegram_id = ?)""", (user_id,)).fetchone()
    if profile_row != None:
        return profile_row
    else:
        return False
    
async def db_get_profiles(user_id, conn: sqlite3.Connection):
    profiles = conn.cursor().execute("""SELECT profile_name FROM profiles WHERE 
                                        telegram_id = ?""", (user_id,)).fetchall()
    if profiles != None:
        profiles = [profile[0] for profile in profiles]
        return profiles
    else:
        return False
