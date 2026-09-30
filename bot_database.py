import sqlite3



# ============================================================
# 1. DATABASE CONFIGURATION
# ============================================================


def get_connection():
    conn = sqlite3.connect("database.db", timeout=10)
    cr = conn.cursor()
    cr.execute("PRAGMA foreign_keys = ON;")
    return conn, cr
# ============================================================
# 1. CREATE TABLES
# ============================================================
def create_prompt_table():
    conn, cr = get_connection()
    cr.execute(
        """CREATE TABLE IF NOT EXISTS prompt (id INTEGER PRIMARY KEY,
        title TEXT,
        content TEXT,
        created_at TEXT DEFAULT (datetime('now', 'localtime')),
        updated_at TEXT DEFAULT (datetime('now', 'localtime'))
        )"""
    )


    cr.execute(
        """CREATE TRIGGER IF NOT EXISTS update_prompt_timestamp
        AFTER UPDATE ON prompt FOR EACH ROW 
        BEGIN
        UPDATE prompt SET updated_at = datetime('now','localtime') WHERE id = OLD.id;  
        END;
        """
    )


    conn.commit()
    conn.close()

def create_history_table():
    conn, cr = get_connection()
    cr.execute(
        """CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY,
        prompt_id INTEGER,
        response TEXT,
        model TEXT,
        input_tokens INTEGER,
        output_tokens INTEGER,
        total_tokens INTEGER,
        created_at TEXT DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (prompt_id) REFERENCES prompt(id))
        """
        )
   

    conn.commit()
    conn.close()

def create_saved_items_table():
    conn, cr = get_connection()
    cr.execute(
        """CREATE TABLE IF NOT EXISTS saved_items (id INTEGER PRIMARY KEY,
        prompt_id INTEGER,
        content TEXT,
        created_at TEXT DEFAULT (datetime('now','localtime')),
        telegram_sent INTEGER DEFAULT 0,
         FOREIGN KEY (prompt_id) REFERENCES prompt(id)
         )
        """
    )
    conn.commit()
    conn.close()



# ============================================================
# 2. INSERT
# ============================================================

def inser_into_prompt_table(title,content):
    conn, cr = get_connection()

    cr.execute("""INSERT INTO prompt (title,content) VALUES(?,?)""",(title,content))

    new_id = cr.lastrowid

    conn.commit()
    conn.close()
    return new_id

# ============================================================
# 3. SELECT
# ============================================================
def get_all_prompts():
    conn, cr = get_connection()
    cr.execute("SELECT * FROM prompt")
    prompts = cr.fetchall()
    list_rows = []
    for row in prompts :
        row = {
            "id": row[0],
            "title": row[1],
            "content": row[2]
        }
        list_rows.append(row)

    conn.close()
    return list_rows

# ============================================================
# 4. UPDATE
# ============================================================
def update_prompt_db(id, update_title, update_content):

    conn, cr = get_connection()
    cr.execute("""
UPDATE prompt
SET title = ?,
content = ? 
WHERE id = ?""",(update_title, update_content, id))

    
    rows_updated = cr.rowcount

    conn.commit()
    conn.close()
    return {
        "message": "Prompt updated",
        "rows_updated": rows_updated
    }
# ============================================================
# 5. DELETE
# ============================================================
def delete_prompt_db(id):
    conn,  cr = get_connection()
    cr.execute(
        "DELETE FROM prompt WHERE id = ?",
               (id,)
               )

    rows_deleted = cr.rowcount

    conn.commit()
    conn.close()
    return {
        "message": "Prompt deleted",
        "rows_deleted": rows_deleted
    }

# ============================================================
# 6. GET PROMPT BY ID
# ============================================================
def get_prompt_id(id):
    conn, cr = get_connection()
    cr.execute("SELECT content FROM prompt WHERE id = ?",(id,))
    prompt = cr.fetchone()
    conn.close()
    if prompt is None:
        return None
    return prompt[0]
# ============================================================
# 7. INSERT IN HISTORY
# ============================================================
def save_history (prompt_id ,
        response ,
        model,
        input_tokens,
        output_tokens,
        total_tokens):
    conn, cr = get_connection()
    cr.execute("""INSERT INTO history (prompt_id,
    response,
    model,
    input_tokens,
    output_tokens,
    total_tokens) VALUES (?,?,?,?,?,?)""",(prompt_id ,
        response ,
        model,
        input_tokens,
        output_tokens,
        total_tokens))
    conn.commit()
    conn.close()
    return {"message": "save succeded"}
    
def get_all_history():
    conn, cr = get_connection()
    cr.execute("SELECT * FROM history")
    all_history = cr.fetchall()
    list_history = []
    for history in all_history :
        history = {
            "id": history[0],
            "prompt_id":history[1] ,
        "response": history[2],
        "model":history[3],
        "input_tokens":history[4],
        "output_tokens":history[5],
        "total_tokens":history[6],
            "created_at": history[7]
        }

        list_history.append(history)

    conn.close()
    return list_history

# ============================================================
# 8. GET HISTORY BY ID
# ============================================================
def get_history_by_id(id):
    conn, cr = get_connection()
    cr.execute(
        "SELECT * FROM history WHERE id = ?",(id,)
    )
    history = cr.fetchone()
    if history is None:
            
            conn.close()
            return None
    row = {
            "id": history[0],
                        "prompt_id":history[1] ,
                    "response": history[2],
                    "model":history[3],
                    "input_tokens":history[4],
                    "output_tokens":history[5],
                    "total_tokens":history[6],
                        "created_at": history[7]
        }
    conn.close()
    return row
# ============================================================
# 8. GET HISTORY BY ID
# ============================================================
def delete_history_by_id_table(id):
    conn, cr =get_connection()
    cr.execute("DELETE FROM history WHERE id= ?",(id,))
    affected = cr.rowcount
    conn.commit()
    conn.close()
    
    return affected

# ============================================================
# 8. SAVED ITEMS
# ============================================================
def saved_items_table(prompt_id,content):
    conn, cr = get_connection()
    cr.execute("""
INSERT INTO saved_items (prompt_id,content) VALUES (?,?)
""",(prompt_id,content))
    last_row = cr.lastrowid
    conn.commit()
    conn.close()
    return last_row
# ============================================================
# 8. SELECT ITEMS
# ============================================================
def get_saved_items_db():

    conn, cr = get_connection()

    cr.execute("SELECT * FROM saved_items")

    saved_items = cr.fetchall()

    list_saved_items = []

    for row in saved_items:

        row = {
            "id": row[0],
            "prompt_id": row[1],
            "content": row[2],
            "created_at": row[3],
            "telegram_sent": row[4]
        }

        list_saved_items.append(row)

    conn.close()

    return list_saved_items
# ============================================================
# 8. DELETE ITEMS BY ID
# ============================================================
def delete_item_by_id_db(id):
    conn, cr = get_connection()
    cr.execute("DELETE FROM saved_items WHERE id = ?",(id,))
    row_deleted = cr.rowcount
    conn.commit()
    conn.close()
    return row_deleted
# ============================================================
# 8. TELEGRAM
# ============================================================
def get_saved_item_by_id_db(id):
    conn, cr = get_connection()
    cr.execute("SELECT * FROM saved_items WHERE id = ?",(id,))
    saved_item = cr.fetchone()

    conn.close()
    return saved_item

# ============================================================
# 9. update_telegram_status
# ============================================================
def update_telegram_status(id):
    conn, cr = get_connection()
    cr.execute("""
UPDATE saved_items
SET telegram_sent = ? WHERE id = ?
""",(1, id))
    affected = cr.rowcount
    conn.commit()
    conn.close()
    return affected




create_prompt_table()
create_saved_items_table()
create_history_table()
get_connection()
