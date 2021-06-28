import vk_api, json
import sqlite3
from vk_api.longpoll import VkLongPoll, VkEventType

vk_session = vk_api.VkApi(token="a8a5584e1a9e7e8c9c0eab0afc07a249f8985dfb4b8a5ce5c6dc945dabd598bc4e00228169c53f2014f52")
session_api = vk_session.get_api()
longpool = VkLongPoll(vk_session)
db = sqlite3.connect('action.db')
sql = db.cursor()
sql.execute("""CREATE TABLE IF NOT EXISTS users (
    userId BIGINT,
    act TEXT,
    fio TEXT,
    gender TEXT,
    age TEXT
)""")
db.commit()
userAct = '0'

def sendMsg(id, some_text):
    vk_session.method("messages.send", {"user_id": id, "message": some_text, "random_id": 0})

def fixMsg(msg):
    msg = "'"+msg+"'"
    return msg

for event in longpool.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        msg = event.text.lower()
        id = event.user_id
        sql.execute(f"SELECT userId FROM users WHERE userId = '{id}'")
        if sql.fetchone() is None:
            sql.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (id, "newUser", "0", "0", "0"))
            db.commit()
            sendMsg(id, "Привет, напиши 'магазин', что бы просмотреть доступные товары.")
        else:
            userAct = sql.execute(f"SELECT act FROM users WHERE userId = '{id}'").fetchone()[0]
            if userAct == "newUser" and msg == "магазин":
                sendMsg(id, "Товары доступные без регистрации: Хлеб, вода, овощи, фрукты. Отправь 'рег' для регистрации.")
            elif userAct == "newUser" and msg == "рег":
                sql.execute(f"UPDATE users SET act = 'getFio' WHERE userId = {id}")
                db.commit()
                sendMsg(id, "Напиши свое ФИО")
            elif userAct == "getFio":
                sql.execute(f"UPDATE users SET fio = {fixMsg(msg)} WHERE userId = {id}")
                sql.execute(f"UPDATE users SET act = 'getGender' WHERE userId = {id}")
                db.commit()
                sendMsg(id, "Твой пол?")
            elif userAct == "getGender":
                sql.execute(f"UPDATE users SET gender = {fixMsg(msg)} WHERE userId = {id}")
                sql.execute(f"UPDATE users SET act = 'getAge' WHERE userId = {id}")
                db.commit()
                sendMsg(id, "Сколько тебе лет?")
            elif userAct == "getAge":
                sql.execute(f"UPDATE users SET age = {fixMsg(msg)} WHERE userId = {id}")
                sql.execute(f"UPDATE users SET act = 'full' WHERE userId = {id}")
                db.commit()
                sendMsg(id, "Регистрация прошла успешно!")
            elif userAct == "full" and msg == "магазин":
                sendMsg(id, "Ты зарегистрированный пользователь, тебе доступно все: Хлеб, вода, овощи, фрукты, алкоголь, оружие, лекарства.")
