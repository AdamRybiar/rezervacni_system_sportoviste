import tkinter as tk
from tkinter import ttk, messagebox
import db
import sqlite3
from datetime import datetime

db.init_db()

# ---------- DB FUNKCE ----------

def add_sportoviste(nazev, typ, kapacita):
    conn = db.connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO sportoviste VALUES (NULL, ?, ?, ?)", (nazev, typ, kapacita))
    conn.commit()
    conn.close()

def get_sportoviste():
    conn = db.connect()
    cur = conn.cursor()
    cur.execute("SELECT id, nazev FROM sportoviste")
    data = cur.fetchall()
    conn.close()
    return data

def get_uzivatele():
    conn = db.connect()
    cur = conn.cursor()
    cur.execute("SELECT id, jmeno FROM uzivatele")
    data = cur.fetchall()
    conn.close()
    return data

def check_collision(datum, od, do, sportoviste_id):
    conn = db.connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM rezervace
        WHERE datum=? AND sportoviste_id=? AND NOT (cas_do <= ? OR cas_od >= ?)
    """, (datum, sportoviste_id, od, do))
    kolize = cur.fetchone()
    conn.close()
    return kolize is not None

def add_rezervace(datum, od, do, sportoviste_id, uzivatel_id):
    if check_collision(datum, od, do, sportoviste_id):
        messagebox.showerror("Chyba", "Kolize rezervace!")
        return
    conn = db.connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO rezervace VALUES (NULL, ?, ?, ?, ?, ?)",
                (datum, od, do, sportoviste_id, uzivatel_id))
    conn.commit()
    conn.close()
    load_today()

def add_uzivatel(jmeno, email):
    conn = db.connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO uzivatele VALUES (NULL, ?, ?)", (jmeno, email))
    conn.commit()
    conn.close()

def delete_rezervace(rid):
    conn = db.connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM rezervace WHERE id=?", (rid,))
    conn.commit()
    conn.close()
    load_today()

# ---------- GUI ----------

root = tk.Tk()
root.title("Správa sportoviště")
root.geometry("1050x650")
root.configure(bg="#e0f7fa")  # jemně modré pozadí

# --- Styly ---
style = ttk.Style(root)
style.theme_use("clam")
style.configure("Treeview", font=("Segoe UI", 10), rowheight=25, background="#ffffff",
                fieldbackground="#f1f8e9")  # pastel zelená
style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#00acc1", foreground="white")
style.map("Treeview", background=[("selected", "#ffcc80")])  # zvýraznění vybrané řádky

style.configure("TButton", font=("Segoe UI", 10), padding=5, background="#00acc1", foreground="white")
style.map("TButton", background=[("active", "#26c6da")])

style.configure("TLabel", font=("Segoe UI", 10), background="#e0f7fa")

padx = 10
pady = 5

# ---- Sportoviště frame ----
frame_s = ttk.LabelFrame(root, text="Přidat sportoviště", padding=(10,10))
frame_s.pack(fill="x", padx=padx, pady=pady)

tk.Label(frame_s, text="Název").grid(row=0, column=0, sticky="w")
tk.Label(frame_s, text="Typ").grid(row=0, column=2, sticky="w")
tk.Label(frame_s, text="Kapacita").grid(row=0, column=4, sticky="w")

nazev_e = tk.Entry(frame_s)
typ_e = tk.Entry(frame_s)
kap_e = tk.Entry(frame_s)

nazev_e.grid(row=0, column=1, padx=5)
typ_e.grid(row=0, column=3, padx=5)
kap_e.grid(row=0, column=5, padx=5)

def gui_add_sport():
    if not kap_e.get().isdigit():
        messagebox.showerror("Chyba", "Kapacita musí být číslo")
        return
    add_sportoviste(nazev_e.get(), typ_e.get(), int(kap_e.get()))
    messagebox.showinfo("OK", "Sportoviště přidáno")
    refresh_combo()

tk.Button(frame_s, text="Přidat", command=gui_add_sport).grid(row=0, column=6, padx=5)

# ---- Uživatel frame ----
frame_u = ttk.LabelFrame(root, text="Přidat uživatele", padding=(10,10))
frame_u.pack(fill="x", padx=padx, pady=pady)

tk.Label(frame_u, text="Jméno").grid(row=0, column=0, sticky="w")
tk.Label(frame_u, text="Email").grid(row=0, column=2, sticky="w")

jmeno_e = tk.Entry(frame_u)
email_e = tk.Entry(frame_u)

jmeno_e.grid(row=0, column=1, padx=5)
email_e.grid(row=0, column=3, padx=5)

def gui_add_user():
    add_uzivatel(jmeno_e.get(), email_e.get())
    messagebox.showinfo("OK", "Uživatel přidán")
    refresh_combo()

tk.Button(frame_u, text="Přidat", command=gui_add_user).grid(row=0, column=4, padx=5)

# ---- Rezervace frame ----
frame_r = ttk.LabelFrame(root, text="Nová rezervace", padding=(10,10))
frame_r.pack(fill="x", padx=padx, pady=pady)

tk.Label(frame_r, text="Datum YYYY-MM-DD").grid(row=0, column=0, sticky="w")
tk.Label(frame_r, text="Od HH:MM").grid(row=0, column=2, sticky="w")
tk.Label(frame_r, text="Do HH:MM").grid(row=0, column=4, sticky="w")
tk.Label(frame_r, text="Sportoviště").grid(row=0, column=6, sticky="w")
tk.Label(frame_r, text="Uživatel").grid(row=0, column=8, sticky="w")

datum_e = tk.Entry(frame_r)
od_e = tk.Entry(frame_r)
do_e = tk.Entry(frame_r)

datum_e.grid(row=0, column=1, padx=5)
od_e.grid(row=0, column=3, padx=5)
do_e.grid(row=0, column=5, padx=5)

sport_combo = ttk.Combobox(frame_r, width=15, state="readonly")
sport_combo.grid(row=0, column=7, padx=5)

user_combo = ttk.Combobox(frame_r, width=15, state="readonly")
user_combo.grid(row=0, column=9, padx=5)

def refresh_combo():
    sport_data = get_sportoviste()
    sport_combo["values"] = [f"{i} - {n}" for i, n in sport_data]
    user_data = get_uzivatele()
    user_combo["values"] = [f"{i} - {n}" for i, n in user_data]

refresh_combo()

def gui_add_rez():
    try:
        datetime.strptime(datum_e.get(), "%Y-%m-%d")
        datetime.strptime(od_e.get(), "%H:%M")
        datetime.strptime(do_e.get(), "%H:%M")
    except:
        messagebox.showerror("Chyba", "Špatný formát data/času")
        return

    if not sport_combo.get() or not user_combo.get():
        messagebox.showerror("Chyba", "Vyberte sportoviště a uživatele")
        return

    sid = sport_combo.get().split(" - ")[0]
    uid = user_combo.get().split(" - ")[0]
    add_rezervace(datum_e.get(), od_e.get(), do_e.get(), sid, uid)

tk.Button(frame_r, text="Rezervovat", command=gui_add_rez).grid(row=0, column=10, padx=5)

# ---- Treeview denní přehled ----
frame_t = ttk.LabelFrame(root, text="Denní přehled", padding=(10,10))
frame_t.pack(fill="both", expand=True, padx=padx, pady=pady)

tree = ttk.Treeview(frame_t, columns=("id", "datum", "od", "do", "sport", "uzivatel"), show="headings")
for c in ("id", "datum", "od", "do", "sport", "uzivatel"):
    tree.heading(c, text=c)
tree.pack(fill="both", expand=True, padx=5, pady=5)

# Alternující barvy řádků
tree.tag_configure('odd', background='#e1f5fe')  # světle modrá
tree.tag_configure('even', background='#b2ebf2')  # tmavší modrá

def load_today():
    conn = db.connect()
    cur = conn.cursor()
    cur.execute("""
    SELECT r.id, r.datum, r.cas_od, r.cas_do, s.nazev, u.jmeno
    FROM rezervace r
    JOIN sportoviste s ON s.id = r.sportoviste_id
    LEFT JOIN uzivatele u ON u.id = r.uzivatel_id
    """)
    for row in tree.get_children():
        tree.delete(row)
    for i, row in enumerate(cur.fetchall()):
        tag = 'even' if i % 2 == 0 else 'odd'
        tree.insert("", "end", values=row, tags=(tag,))
    conn.close()

load_today()

def delete_selected():
    sel = tree.selection()
    if not sel:
        return
    rid = tree.item(sel[0])["values"][0]
    delete_rezervace(rid)

tk.Button(root, text="Smazat rezervaci", command=delete_selected).pack(pady=10)

root.mainloop()
