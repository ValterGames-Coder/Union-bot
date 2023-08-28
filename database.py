import sqlite3

db = sqlite3.connect("users.db", check_same_thread=False)
cursor = db.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users (
    id INTEGER,
    name TEXT,
    chat INTEGER
)""")
db.commit()


def get_users():
    users = cursor.execute(f"SELECT * FROM users").fetchall()
    db.commit()
    return users


def get_user(id):
    user = cursor.execute(f"SELECT * FROM users WHERE id = {id}").fetchall()
    db.commit()
    return user


def set_user(id: int, name: str):
    cursor.execute("INSERT INTO users VALUES (?, ?)", (id, name))
    db.commit()
    return 'Зарегестрирован'


def delete_user(id: int):
    cursor.execute(f"DELETE FROM users WHERE id = {id}")
    db.commit()