import sqlite3
import logging
from fastapi import HTTPException
#---------------JWT IMPORTING ---------------
from pwdlib import PasswordHash



def get_connection():
    conn= sqlite3.connect("con_bot.db")
    cr = conn.cursor()
    return conn, cr


def commit_close (conn):
    conn.commit()
    conn.close()
def close(conn):
    conn.close()

def create_db():
    conn, cr = get_connection()
    try:
        cr.execute("""CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        role TEXT ,
        message TEXT
        )
        """)
    except:
        logging.exception("database error")
        raise HTTPException (status_code=500,
                             detail= "une erreur de base de données  s'est produite.")

    finally:
        commit_close(conn)
    
def save_user (user_id,fin_user):
    conn, cr = get_connection()
    try:
        cr.execute("INSERT INTO history (user_id, role, message) Values(?,?,?)",(user_id,"user", fin_user))
        conn.commit()
        
    except Exception as e :
        logging.exception("Database error")
        raise HTTPException (status_code = 500,
                             detail= "une erreur de base de données  s'est produite.")

    finally : 
        close(conn)
    

def save_assistant(result):
    conn, cr = get_connection()
    try:
        cr.execute("INSERT INTO history (role, message) Values(?,?)",("assistant", result))
    except:
        logging.exception("database Error")
        raise HTTPException (status_code= 500, detail= "une erreur de base de données  s'est produite.")
    finally:
        commit_close(conn)
def create_users_table():
    conn, cr = get_connection()
    try:

        cr.execute("""
    CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    role TEXT,
    message TEXT
)
    """)
        conn.commit()
    except :
        logging.exception("Error In Create table")

        raise HTTPException (status_code=500,
                             detail="une erreur de base de données  s'est produite.")

    finally :
        close(conn)

password_hash = PasswordHash.recommended()

def create_user (username,password,role):
    conn, cr = get_connection()
    
    try: 
        hashed_password = password_hash.hash(password)

        cr.execute("""
    INSERT INTO users (username, password_hash, role) Values(?,?,?)
    """, (username,hashed_password,role))
        
        conn.commit()
    except :
        logging.exception("Une erreur in Database")
        raise HTTPException (status_code=500,
                             detail="une erreur de base de données  s'est produite.")
    finally:
        conn.close()
def get_user_by_username(username):
    conn, cr = get_connection()
    try:
        cr.execute("""SELECT id, username, password_hash, role, is_active
          FROM users WHERE username = (?)""",
          (username,))
        user = cr.fetchone()
        if user is None:
            return ("This username dont not exist")

        
        return user
    except:
        logging.exception("Une erreur in Database")
        raise HTTPException (status_code=500,
                            detail="une erreur de base de données  s'est produite.")
    finally:
        conn.close()
def add_user_id_to_history():
    conn, cr = get_connection()

    try:
        cr.execute("""
            ALTER TABLE history
            ADD COLUMN user_id INTEGER
        """)
        conn.commit()

    except Exception:
        logging.exception("Error adding user_id to history")

    finally:
        conn.close()


