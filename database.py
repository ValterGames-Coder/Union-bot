import random
import sqlite3
import random

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


def create_pet(id: int, name: str, type: str):
    cursor.execute("INSERT INTO pets VALUES (?, ?, ?, ?, ?, ?)", (id, name, 10, 10, 10, type))
    db.commit()
    return f'Поздравляю! {name} появился на свет'


def get_pet(id: int):
    pet = cursor.execute(f"SELECT * FROM pets WHERE id = {id}").fetchall()[0]
    db.commit()
    return pet


def get_pets():
    pets = cursor.execute(f"SELECT * FROM pets")
    db.commit()
    return pets


def update_pets():
    pets = cursor.execute(f"SELECT * FROM pets").fetchall()
    print(pets)
    text = ''
    for pet in pets:
        print(pet)
        if pet[2] - 1 <= 0:
            text += f'<a href="tg://user?id={pet[0]}">{pet[1]} хочет гулять</a>!\n'
        if pet[3] - 1 <= 0:
            text += f'<a href="tg://user?id={pet[0]}">{pet[1]} хочет играть</a>!\n'
        if pet[4] - 1 <= 0:
            text += f'<a href="tg://user?id={pet[0]}">{pet[1]} хочет есть</a>!\n'

    print(text)
    sql_update()
    db.commit()
    return text


def sql_update():
    pets = cursor.execute(f"SELECT * FROM pets").fetchall()
    for pet in pets:
        if pet[2] - 1 > -1:
            cursor.execute(f"UPDATE pets SET walk = {pet[2] - 1} WHERE id = {pet[0]}")
        if pet[3] - 1 > -1:
            cursor.execute(f"UPDATE pets SET play = {pet[3] - 1} WHERE id = {pet[0]}")
        if pet[4] - 1 > -1:
            cursor.execute(f"UPDATE pets SET eat = {pet[4] - 1} WHERE id = {pet[0]}")
        db.commit()

def play_pet(id: int):
    count = random.randint(2, 5)
    pet = cursor.execute(f"SELECT * FROM pets WHERE id = {id}").fetchall()[0]
    if pet[3] + count <= 10:
        cursor.execute(f"UPDATE pets SET play = {pet[3] + count} WHERE id = {id}")
    else:
        cursor.execute(f"UPDATE pets SET play = 10 WHERE id = {id}")
    db.commit()
    return 'Вы поиграли с питомцем!'


def walk_pet(id: int):
    count = random.randint(2, 5)
    pet = cursor.execute(f"SELECT * FROM pets WHERE id = {id}").fetchall()[0]
    if pet[2] + count <= 10:
        cursor.execute(f"UPDATE pets SET walk = {pet[2] + count} WHERE id = {id}")
    else:
        cursor.execute(f"UPDATE pets SET walk = 10 WHERE id = {id}")
    db.commit()
    return 'Вы погуляли с питомцем!'


def eat_pet(id: int):
    count = random.randint(2, 5)
    pet = cursor.execute(f"SELECT * FROM pets WHERE id = {id}").fetchall()[0]
    if pet[4] + count <= 10:
        cursor.execute(f"UPDATE pets SET eat = {pet[4] + count} WHERE id = {id}")
    else:
        cursor.execute(f"UPDATE pets SET eat = 10 WHERE id = {id}")
    db.commit()
    return 'Вы покормили питомца!'