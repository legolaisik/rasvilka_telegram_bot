import asyncio
import sqlite3

async def check_transaction(hash, conn: sqlite3.Connection):
    if conn.cursor().execute("SELECT hash FROM transactions WHERE hash = ?", (hash,)).fetchone() != None:
        return True
    else:
        return False

async def add_v_transaction(source, hash, value, comment, conn: sqlite3.Connection):
    try:
        conn.cursor().execute("INSERT INTO transactions (source, hash, value, comment) VALUES (?, ?, ?, ?)",(source, hash, value, comment))
        conn.commit()
        return True
    except:
        return False
