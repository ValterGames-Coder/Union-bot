import config
import time
import database
import telebot
import schedule
from threading import Thread
import requests
import random

bot = telebot.TeleBot(config.BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Hello!')
    print(message.chat.id)


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, 'Команды: /mute /unmute /ban /kick /reg /tamepet /pet')


@bot.message_handler(commands=['mute'])
def mute(message):
    mute_args = str(message.text).split(' ')
    mute_time = int(mute_args[1])
    if message.from_user.id in config.ID_ADMIN:
        if len(mute_args) == 1:
            bot.reply_to(message, 'Вы не указали время')
        else:
            if message.reply_to_message is None:
                bot.reply_to(message, 'Вы не указали участника')
            else:
                if mute_time < 31:
                    bot.send_message(message.chat.id, f'Мут меньше, чем на 30 сек. невозможен')
                else:
                    bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id,
                                               until_date=time.time() + mute_time)
                    bot.send_message(message.chat.id, f'Участник @{message.reply_to_message.from_user.username} '
                                                        f'попал в мут')


@bot.message_handler(commands=['unmute'])
def unmute(message):
    if message.reply_to_message and message.from_user.id in config.ID_ADMIN:
        chat_id = message.chat.id
        user_id = message.reply_to_message.from_user.id
        bot.restrict_chat_member(chat_id, user_id, can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
        bot.reply_to(message, f"Пользователь @{message.reply_to_message.from_user.username} размучен")
    else:
        bot.reply_to(message, "Вы не указали пользователя")


@bot.message_handler(commands=['ban'])
def ban(message):
    if message.from_user.id in config.ID_ADMIN:
        if message.reply_to_message is None:
            bot.reply_to(message, 'Вы не указали участника')
        elif message.reply_to_message.from_user.id in config.ID_ADMIN:
            bot.reply_to(message, "Невозможно забанить администратора")
        else:
            bot.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
            bot.send_message(message.chat.id, f'Участник @{message.reply_to_message.from_user.username} '
                                                        f'попал в бан')


@bot.message_handler(commands=['kick'])
def kick(message):
    if message.reply_to_message and message.from_user.id in config.ID_ADMIN:
        chat_id = message.chat.id
        user_id = message.reply_to_message.from_user.id
        if message.reply_to_message.from_user.id in config.ID_ADMIN:
            bot.reply_to(message, "Невозможно кикнуть администратора")
        else:
            bot.kick_chat_member(chat_id, user_id)
            bot.reply_to(message, f"Пользователь @{message.reply_to_message.from_user.username} был кикнут")
    else:
        bot.reply_to(message, "Вы не указали пользователя")


@bot.message_handler(commands=['reg'])
def reg(message):
    user = database.get_user(message.from_user.id)
    if user is None:
        if message.from_user.last_name is None:
            full_name = message.from_user.first_name
        else:
            full_name = f"{message.from_user.first_name} {message.from_user.last_name}"
        bot.send_message(message.chat.id,
                         f'<a href="tg://user?id={message.from_user.id}">{database.set_user(message.from_user.id, full_name)}</a>',
                         parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, f'<a href="tg://user?id={message.from_user.id}">Ты уже есть в базе данных</a>', parse_mode='HTML')


def on_reg(member):
    user = database.get_user(member.id)
    if user is None:
        if member.last_name is None:
            full_name = member.first_name
        else:
            full_name = f"{member.first_name} {member.last_name}"
        return f'<a href="tg://user?id={member.id}">{database.set_user(member.id, full_name)}</a>'
    else:
        return f'<a href="tg://user?id={member.id}">Ты уже есть в базе данных</a>'


def on_del(member):
    return database.delete_user(member.id)


@bot.message_handler(commands=['everyone'])
def everyone(message):
    everyone_message = 'Общий сбор!'
    print(everyone_message)
    users = database.get_users()
    text = ''
    for user in users:
        user_status = bot.get_chat_member(message.chat.id, user[0]).status
        print(user_status)
        if user_status != 'left':
            text += f'<a href="tg://user?id={user[0]}">{user[1]}</a>, '
    print(text)
    gif = open("hog-rider-coc.mp4", 'rb')
    bot.send_animation(message.chat.id, gif, caption=f"<b>{everyone_message}</b>\n\n{text}"[:-2], parse_mode='HTML')


@bot.message_handler(commands=['tamepet'])
def tame_pet(message):
    pets = database.get_pets()
    pets_id = []
    for pet in pets:
        pets_id.append(pet[0])
    if message.from_user.id in pets_id:
        bot.reply_to(message, 'У тебя уже есть питомец')
    elif len(message.text.split(' ')) == 2:
        bot.reply_to(message, 'Вы не указали тип питомца (на английском желательно)')
    elif len(message.text.split(' ')) == 3:
        name = message.text.split(' ')[1]
        type = message.text.split(' ')[2]
        bot.reply_to(message, database.create_pet(message.from_user.id, name, type))
    else:
        bot.reply_to(message,'Вы не указали имя питомца')


@bot.message_handler(commands=['pet'])
def pet(message):
    pet = database.get_pet(message.from_user.id)
    print(pet)
    if pet is None:
        bot.reply_to(message, 'У вас нет питомца. Чтобы его приручить напишите /tamepet')
    else:
        text = f'<a href="tg://user?id={pet[0]}">Питомец {pet[1]}</a>\n'
        text += f'🚶 Прогулки: {pet[2]}\n'
        text += f'😀 Настроение: {pet[3]}\n'
        text += f'🌯 Еда: {pet[4]}\n'
        print()
        bot.send_message(message.chat.id, text, parse_mode='HTML')

@bot.message_handler(content_types=['new_chat_members'])
def handler_new_member(message):
    bot.send_message(message.chat.id, on_reg(message.new_chat_members[0]), parse_mode='HTML')


@bot.message_handler(content_types=['left_chat_member'])
def handler_left_member(message):
    on_del(message.left_chat_member)


chat_id = -1001880123787
def update():
    text = database.update_pets()
    print(text)
    bot.send_message(chat_id, text, parse_mode='HTML')

@bot.message_handler(commands=['play'])
def play(message):
    pet = database.get_pet(message.from_user.id)
    response = requests.get("https://g.tenor.com/v1/search?q={0}&key=LIVDSRZULELA&limit=30".format(f'{pet[5]} play'))
    data = response.json()
    gif = random.choice(data["results"])
    if pet is None:
        bot.reply_to(message, 'У вас нет питомца. Чтобы его приручить напишите /tamepet')
    else:
        bot.send_animation(message.chat.id, gif['media'][0]['gif']['url'], caption=database.play_pet(message.from_user.id))


@bot.message_handler(commands=['walk'])
def walk(message):
    pet = database.get_pet(message.from_user.id)
    response = requests.get("https://g.tenor.com/v1/search?q={0}&key=LIVDSRZULELA&limit=30".format(f'walk with {pet[5]}'))
    data = response.json()
    gif = random.choice(data["results"])
    if pet is None:
        bot.reply_to(message, 'У вас нет питомца. Чтобы его приручить напишите /tamepet')
    else:
        bot.send_animation(message.chat.id, gif['media'][0]['gif']['url'], caption=database.walk_pet(message.from_user.id))


@bot.message_handler(commands=['eat'])
def eat(message):
    pet = database.get_pet(message.from_user.id)
    response = requests.get("https://g.tenor.com/v1/search?q={0}&key=LIVDSRZULELA&limit=30".format(f'{pet[5]} eat'))
    data = response.json()
    gif = random.choice(data["results"])
    if pet is None:
        bot.reply_to(message, 'У вас нет питомца. Чтобы его приручить напишите /tamepet')
    else:
        bot.send_animation(message.chat.id, gif['media'][0]['gif']['url'], caption=database.eat_pet(message.from_user.id))


schedule.every().minute.do(update)


def loop1():
    print('----------------Pets start-----------------\n')
    while True:
        try:
            schedule.run_pending()
            time.sleep(10)
        except Exception as e:
            print(e)
            time.sleep(3)


def loop2():
    print('----------------Bot start-----------------\n')
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
            time.sleep(3)


if __name__ == '__main__':
    Thread(target=loop1).start()
    Thread(target=loop2).start()