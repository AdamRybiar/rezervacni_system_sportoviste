import sqlite3

DB_NAME = "rezervace.db"

def connect():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = connect()
    cur = conn.cursor()

    # sportoviště
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sportoviste (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nazev TEXT NOT NULL,
        typ TEXT NOT NULL,
        kapacita INTEGER NOT NULL
    )
    """)

    # uživatelé
    cur.execute("""
    CREATE TABLE IF NOT EXISTS uzivatele (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        jmeno TEXT NOT NULL,
        email TEXT NOT NULL
    )
    """)

    # rezervace (s uzivatelem)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS rezervace (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        datum TEXT NOT NULL,
        cas_od TEXT NOT NULL,
        cas_do TEXT NOT NULL,
        sportoviste_id INTEGER,
        uzivatel_id INTEGER,
        FOREIGN KEY (sportoviste_id) REFERENCES sportoviste(id),
        FOREIGN KEY (uzivatel_id) REFERENCES uzivatele(id)
    )
    """)

    conn.commit()
    conn.close()

# ---- Sportoviště ----
def add_sportoviste(nazev, typ, kapacita):
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO sportoviste VALUES (NULL, ?, ?, ?)", (nazev, typ, kapacita))
    conn.commit()
    conn.close()

def get_sportoviste():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT id, nazev FROM sportoviste")
    data = cur.fetchall()
    conn.close()
    return data

# ---- Uživatele ----
def add_uzivatel(jmeno, email):
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO uzivatele VALUES (NULL, ?, ?)", (jmeno, email))
    conn.commit()
    conn.close()

def get_uzivatele():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT id, jmeno FROM uzivatele")
    data = cur.fetchall()
    conn.close()
    return data
