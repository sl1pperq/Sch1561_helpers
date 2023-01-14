import telebot
from telebot import types
import sqlite3
from peewee import *

OnWork = True
notes = {}
status = 0
token = '5984112909:AAF4yH3zH0vJaIMWsSY8PNZQlLzFZxaMp3s'
bot = telebot.TeleBot(token)
'''
db = sqlite3.connect('usersdata.db')
c = db.cursor()
c.execute("""CREATE TABLE articles(
        id text,
        problem text,
        status integer
    )""")
'''


@bot.message_handler(commands=['start', 'help'])
def start_message(message):
    db = sqlite3.connect('usersdata.db')
    c = db.cursor()
    user_id = message.chat.id
    bot.send_message(user_id, "👋 Привет! Это система для помощи ученикам в школе")
    menu(message)


def menu(message):
    db = sqlite3.connect('usersdata.db')
    c = db.cursor()
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text="‍🎓 Я могу помочь", callback_data="icanhelp")
    button2 = types.InlineKeyboardButton(text="✋ Мне нужна помощь", callback_data="ineedhelp")
    keyboard.add(button1)
    keyboard.add(button2)
    bot.send_message(message.chat.id, "⚙️ Выберите опцию:", reply_markup=keyboard)
    db.commit()


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == "icanhelp":
            icanhelp(call.message.chat.id)
        if call.data == "ineedhelp":
            ineedhelp(call.message.chat.id)
        if call.data.startswith("deleteapply2_"):
            problem = call.data.split('_')[1]
            db = sqlite3.connect('usersdata.db')
            c = db.cursor()
            print("UPDATE articles SET status = 2 WHERE id = '{call.from_user.id}' and problem = '{problem}'")
            c.execute(f"UPDATE articles SET status = 2 WHERE id = '{call.from_user.id}' and problem = '{problem}'")
            db.commit()
            menu(call.message)
        if call.data.startswith("deleteapply0_"):
            problem = call.data.split('_')[1]
            db = sqlite3.connect('usersdata.db')
            c = db.cursor()
            print("DELETE FROM articles WHERE id = '{call.from_user.id}' and problem = '{problem}'")
            c.execute(f"DELETE FROM articles WHERE id = '{call.from_user.id}' and problem = '{problem}'")
            db.commit()
            menu(call.message)


def ineedhelp(user_id):
    msg = bot.send_message(user_id, "📌 Опишите вашу проблему:")
    bot.register_next_step_handler(msg, update)


def update(message):
    db = sqlite3.connect('usersdata.db')
    c = db.cursor()
    user_id = message.chat.id
    tgid = message.from_user.id
    execl1 = f'{tgid}'
    c.execute(f"INSERT INTO articles VALUES ('{execl1}','{message.text}',1)")
    bot.send_message(user_id, "📝 Мы получили ваш запрос!")
    db.commit()
    c = db.cursor()
    bot.send_message(user_id, "📒 Список ваших заявок: ")
    c.execute(f"SELECT * FROM articles WHERE id={execl1}")
    items = c.fetchall()
    for el in items:
        bot.send_message(user_id, el[0])
    db.commit()
    db.close()
    aftermenu(user_id, message.text)
    return


def icanhelp(user_id):
    cnt = 0
    db = sqlite3.connect('usersdata.db')
    c = db.cursor()
    bot.send_message(user_id, "👨‍👩‍👦 Список нуждающихся:")
    endlist = []
    c.execute("SELECT id FROM articles")
    for ids in c.fetchall():
        endlist.append(f"tg://user?id={ids[0]}")
    print(endlist)
    c.execute("SELECT problem FROM articles WHERE status = 1")
    for problems in c.fetchall():
        stroke = 'Заявка: <a href="{0}"> {1} </a>'.format(endlist[cnt], problems[0])
        print(stroke)
        bot.send_message(user_id, text=stroke, parse_mode='HTML')
        cnt += 1
    db.commit()
    return


def aftermenu(user_id, problem):
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text="✅ Мне помогли", callback_data=f"deleteapply2_{problem}")
    button2 = types.InlineKeyboardButton(text="❌ Отмена", callback_data=f"deleteapply0_{problem}")
    keyboard.add(button1)
    keyboard.add(button2)
    bot.send_message(user_id, "📡 Статус задания?", reply_markup=keyboard)



bot.polling(none_stop=True)