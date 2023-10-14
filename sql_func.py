import asyncio
import sqlite3

async def get_profile(profile_id, conn: sqlite3.Connection):
    profile_row = conn.cursor().execute("SELECT * FROM profiles WHERE profile_id = ?", (profile_id,)).fetchone()
    if profile_row != None:
        return profile_row
    else:
        return False
