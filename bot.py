import config
import time
import database
import telebot

bot = telebot.TeleBot(config.BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Hello!')


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, 'Команды: /mute /unmute /ban /kick /reg')


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
    users = database.get_users()
    users_id = []
    for user in users:
        users_id.append(user[0])
    print(users_id)
    if message.from_user.id in users_id:
        bot.send_message(message.chat.id, f'<a href="tg://user?id={message.from_user.id}">Ты уже есть в базе данных</a>',
                                   parse_mode='HTML')
    else:
        if message.from_user.last_name is None:
            full_name = message.from_user.first_name
        else:
            full_name = f"{message.from_user.first_name} {message.from_user.last_name}"
        bot.send_message(message.chat.id,
                               f'<a href="tg://user?id={message.from_user.id}">{database.set_user(message.from_user.id, full_name)}</a>',
                               parse_mode='HTML')


def on_reg(member):
    users = database.get_users()
    users_id = []
    for user in users:
        users_id.append(user[0])
    print(users_id)
    if member.id in users_id:
        return f'<a href="tg://user?id={member.id}">Ты уже есть в базе данных</a>'
    else:
        if member.last_name is None:
            full_name = member.first_name
        else:
            full_name = f"{member.first_name} {member.last_name}"
        return f'<a href="tg://user?id={member.id}">{database.set_user(member.id, full_name)}</a>'


def on_del(member):
    return database.delete_user(member.id)


@bot.message_handler(commands=['everyone'])
def everyone(message):
    everyone_message = message.text.split(maxsplit=1)[1]
    print(everyone_message)
    if everyone_message is None:
        everyone_message = 'Общий сбор!'
    users = database.get_users()
    text = ''
    last = users[-1][0]
    for user in users:
        if user[0] == last:
            text += f'<a href="tg://user?id={user[0]}">{user[1]}</a>'
        else:
            text += f'<a href="tg://user?id={user[0]}">{user[1]}</a>, '
    print(text)
    gif = open("hog-rider-coc.mp4", 'rb')
    bot.send_animation(message.chat.id, gif, caption=f"<b>{everyone_message}</b>\n\n{text}", parse_mode='HTML')


@bot.message_handler(content_types=['new_chat_members'])
def handler_new_member(message):
    bot.send_message(message.chat.id, on_reg(message.new_chat_members[0]), parse_mode='HTML')


@bot.message_handler(content_types=['left_chat_member'])
def handler_left_member(message):
    on_del(message.left_chat_member)


if __name__ == '__main__':
    print('----------------Bot start-----------------\n')
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
            time.sleep(3)

