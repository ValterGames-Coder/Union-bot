import sqlite3

db = sqlite3.connect("users.db", check_same_thread=False)
cursor = db.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users (
    id INT,
    name TEXT
)""")
db.commit()


def get_users():
    users = cursor.execute(f"SELECT * FROM users").fetchall()
    db.commit()
    return users


def set_user(id: int, name: str):
    cursor.execute("INSERT INTO users VALUES (?, ?)", (id, name))
    db.commit()
    return 'Зарегестрирован'
