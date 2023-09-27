import config
import time
import database
import telebot
from threading import Thread
import requests
import random
from bs4 import BeautifulSoup

bot = telebot.TeleBot(config.BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Hello!')
    print(message.chat.id)


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, 'Команды: /mute /unmute /ban /kick /reg /joke')


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
    else:
        bot.reply_to(message.chat.id, '⚠ У тебя нет прав!')


@bot.message_handler(commands=['unmute'])
def unmute(message):
    if message.from_user.id in config.ID_ADMIN:
        if message.reply_to_message is None:
            chat_id = message.chat.id
            user_id = message.reply_to_message.from_user.id
            bot.restrict_chat_member(chat_id, user_id, can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
            bot.reply_to(message, f"Пользователь @{message.reply_to_message.from_user.username} размучен")
        else:
            bot.reply_to(message, "Вы не указали пользователя")
    else:
        bot.reply_to(message.chat.id, '⚠ У тебя нет прав!')


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
    else:
        bot.reply_to(message.chat.id, '⚠ У тебя нет прав!')


@bot.message_handler(commands=['kick'])
def kick(message):
    if message.from_user.id in config.ID_ADMIN:
        if message.reply_to_message is None:
            chat_id = message.chat.id
            user_id = message.reply_to_message.from_user.id
            if message.reply_to_message.from_user.id in config.ID_ADMIN:
                bot.reply_to(message, "Невозможно кикнуть администратора")
            else:
                bot.kick_chat_member(chat_id, user_id)
                bot.reply_to(message, f"Пользователь @{message.reply_to_message.from_user.username} был кикнут")
        else:
            bot.reply_to(message, "Вы не указали пользователя")
    else:
        bot.reply_to(message.chat.id, '⚠ У тебя нет прав!')


@bot.message_handler(commands=['reg'])
def reg(message):
    user = database.get_user(message.from_user.id)
    print(user)
    if bool(user) is False:
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
    print(user)
    if bool(user) is False:
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


@bot.message_handler(content_types=['new_chat_members'])
def handler_new_member(message):
    bot.send_message(message.chat.id, on_reg(message.new_chat_members[0]), parse_mode='HTML')


@bot.message_handler(content_types=['left_chat_member'])
def handler_left_member(message):
    on_del(message.left_chat_member)


@bot.message_handler(commands=['delete'])
def delete(message):
    if message.from_user.id in config.ID_ADMIN:
        bot.delete_message(message_id=message.reply_to_message.id, chat_id=message.chat.id)


@bot.message_handler(commands=['joke'])
def joke(message):
    url = 'https://baneks.site/random'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    anekdot = soup.find('div', class_='block-content mdl-card__supporting-text mdl-color--grey-300 mdl-color-text--grey-900').find('p')
    str_anekdot = anekdot.get_text()
    bot.send_message(message.chat.id, str_anekdot, parse_mode='HTML')
    #if len(anekdots) <= 0:
        #bot.send_message(message.chat.id, 'Нет такого тега', parse_mode='HTML')
    #else:
        #soup = BeautifulSoup(r.text, 'html.parser')
        #anekdots = soup.find_all('div', class_ = 'holder-body')
        #anekdot = random.choice([c.text for c in anekdots])


#@bot.message_handler(commands=['old_joke'])
#def old_joke(message):
    #anekdots = []
    #for i, an in enumerate(anekdotSns.get_items()):
        #if i > 51:
            #break
        #anekdots.append(str(an.content))
        #print(f"{i}. {an.content}")
    #anekdot = random.choice([c for c in anekdots])
    #bot.send_message(message.chat.id, anekdot, parse_mode='HTML')

def loop1():
    print('----------------Bot start-----------------\n')
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
            time.sleep(3)


if __name__ == '__main__':
    Thread(target=loop1).start()