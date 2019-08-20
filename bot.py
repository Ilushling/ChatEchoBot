
# -*- coding: utf-8 -*-
import telebot
from telebot import apihelper
from telebot import types
import pymysql
from pymysql.cursors import DictCursor
from contextlib import closing
import pyowm
import config

# Proxy
#apihelper.proxy = {
#    'https': config.PROXY
#}
# Telebot
bot = telebot.TeleBot(config.API['Telegramapikey'])

# DB

def start_server():
    create_db()
    create_db_tables()

    print('server started')
    bot.polling(none_stop=True)

def create_db():
    try:
        print ("Creating DB...")
        with closing(pymysql.connect(
            host=config.DATABASE_CONFIG['host'],
            user=config.DATABASE_CONFIG['user'],
            password=config.DATABASE_CONFIG['password'],
            db=config.DATABASE_CONFIG['db'],
            charset=config.DATABASE_CONFIG['charset'],
            cursorclass=DictCursor
        )) as connection:
            with connection.cursor() as cursor:
                query = """CREATE DATABASE IF NOT EXISTS `ilushling$ilushlingbot` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;"""
                cursor.execute(query)
                connection.commit()

                print ("DB created")
    except Exception as exc:
        print ("Error create DB")
        print (exc)

def create_db_tables():
    try:
        print ("Creating DB tables...")
        with closing(pymysql.connect(
            host=config.DATABASE_CONFIG['host'],
            user=config.DATABASE_CONFIG['user'],
            password=config.DATABASE_CONFIG['password'],
            db=config.DATABASE_CONFIG['db'],
            charset=config.DATABASE_CONFIG['charset'],
            cursorclass=DictCursor
        )) as connection:
            with connection.cursor() as cursor:
                query = """
                CREATE TABLE IF NOT EXISTS `users` (
                `id` int(11) NOT NULL AUTO_INCREMENT,
                `chat_id` int(11) NOT NULL,
                `user_id` int(11) DEFAULT NULL,
                `visible` tinyint(1) NOT NULL DEFAULT 1,
                PRIMARY KEY (`id`),
                KEY `id` (`id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;"""
                cursor.execute(query)
                connection.commit()

                print ("DB tables created")
    except Exception as exc:
        print ("Error create DB")
        print (exc)

def check_chat(message):
    try:
        with closing(pymysql.connect(
            host=config.DATABASE_CONFIG['host'],
            user=config.DATABASE_CONFIG['user'],
            password=config.DATABASE_CONFIG['password'],
            db=config.DATABASE_CONFIG['db'],
            charset=config.DATABASE_CONFIG['charset'],
            cursorclass=DictCursor
        )) as connection:
            with connection.cursor() as cursor:
                query = "SELECT * FROM users WHERE chat_id = " + str(message.chat.id)
                cursor.execute(query)
                for row in cursor:
                    if row['chat_id'] == message.chat.id:
                        return True
                    return False
    except Exception as exc:
        print ("Error chech chat")
        print (exc)

def save_chat(message):
    try:
        with closing(pymysql.connect(
            host=config.DATABASE_CONFIG['host'],
            user=config.DATABASE_CONFIG['user'],
            password=config.DATABASE_CONFIG['password'],
            db=config.DATABASE_CONFIG['db'],
            charset=config.DATABASE_CONFIG['charset'],
            cursorclass=DictCursor
        )) as connection:
            with connection.cursor() as cursor:
                query = "INSERT INTO users (chat_id, user_id) VALUES (" + str(message.chat.id) + ", " + str(message.from_user.id) + ")"
                cursor.execute(query)
                connection.commit()
    except Exception as exc:
        print ("Error save chat")
        print (exc)

def load_chats():
    try:
        with closing(pymysql.connect(
            host=config.DATABASE_CONFIG['host'],
            user=config.DATABASE_CONFIG['user'],
            password=config.DATABASE_CONFIG['password'],
            db=config.DATABASE_CONFIG['db'],
            charset=config.DATABASE_CONFIG['charset'],
            cursorclass=DictCursor
        )) as connection:
            with connection.cursor() as cursor:
                query = "SELECT * FROM users"
                cursor.execute(query)
                chats = []
                for row in cursor:
                    chats.append(row['chat_id'])
                return chats
    except Exception as exc:
        print ("Error load chats")
        print (exc)

def check_visible(message):
    try:
        with closing(pymysql.connect(
            host=config.DATABASE_CONFIG['host'],
            user=config.DATABASE_CONFIG['user'],
            password=config.DATABASE_CONFIG['password'],
            db=config.DATABASE_CONFIG['db'],
            charset=config.DATABASE_CONFIG['charset'],
            cursorclass=DictCursor
        )) as connection:
            with connection.cursor() as cursor:
                query = "SELECT visible FROM users WHERE user_id = " + str(message.from_user.id)
                cursor.execute(query)
                for row in cursor:
                    if row['visible']:
                        return True
                    else:
                        return False
    except Exception as exc:
        print (exc)


@bot.message_handler(commands=["start"])
def start_message(message):
    bot.send_message(message.chat.id, u"Привет " +
        message.from_user.username + u"\nЭто чат, ты здесь можешь сообщение и другие его увидят")
    try:
        if not check_chat(message):
            print('New chat ' + str(message.chat.id))
            save_chat(message)
            markup = telebot.types.InlineKeyboardMarkup()
            buttonv = telebot.types.InlineKeyboardButton(text='visible', callback_data='visible|' +
                                                         str(message.chat.id) + '|' + str(message.from_user.id))
            buttoni = telebot.types.InlineKeyboardButton(text='invisible', callback_data='invisible|' +
                                                         str(message.chat.id) + '|' + str(message.from_user.id))
            buttonw = telebot.types.InlineKeyboardButton(text='weather', callback_data='weather|' +
                                                         str(message.chat.id) + '|' + str(message.from_user.id))
            markup.add(buttonv)
            markup.add(buttoni)
            markup.add(buttonw)
            bot.send_message(chat_id=message.chat.id, text='Help', reply_markup=markup)
    except Exception as exc:
        print (exc)
# button handler
@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    data = call.data.split('|')
    if data[0] == 'visible':
        visible(False, data[1], data[2])
        bot.answer_callback_query(callback_query_id=call.id, text='visible')
    if data[0] == 'invisible':
        invisible(False, data[1], data[2])
        bot.answer_callback_query(callback_query_id=call.id, text='invisible')
    if data[0] == 'weather':
        weather(False, data[1], data[2])

@bot.message_handler(commands=["help"])
def help(message):
    markup = telebot.types.InlineKeyboardMarkup()
    buttonv = telebot.types.InlineKeyboardButton(text='visible', callback_data='visible|' +
                                                         str(message.chat.id) + '|' + str(message.from_user.id))
    buttoni = telebot.types.InlineKeyboardButton(text='invisible', callback_data='invisible|' +
                                                         str(message.chat.id) + '|' + str(message.from_user.id))
    buttonw = telebot.types.InlineKeyboardButton(text='weather', callback_data='weather|' +
                                                         str(message.chat.id) + '|' + str(message.from_user.id))
    markup.add(buttonv)
    markup.add(buttoni)
    markup.add(buttonw)
    bot.send_message(chat_id=message.chat.id, text='Help', reply_markup=markup)

# visible
@bot.message_handler(commands=["visible"])
def visible(message, chat_id = False, user_id = False):
    if not chat_id:
        chat_id = message.chat.id
    if not user_id:
        user_id = message.from_user.id

    try:
        with closing(pymysql.connect(
            host=config.DATABASE_CONFIG['host'],
            user=config.DATABASE_CONFIG['user'],
            password=config.DATABASE_CONFIG['password'],
            db=config.DATABASE_CONFIG['db'],
            charset=config.DATABASE_CONFIG['charset'],
            cursorclass=DictCursor
        )) as connection:
            with connection.cursor() as cursor:
                query = "UPDATE users SET visible = 1 WHERE user_id = " + str(user_id)
                cursor.execute(query)
                connection.commit()
                bot.send_message(chat_id, u"Твой ник видно в чате")
    except Exception as exc:
        print ('visible')
        print (exc)

# invisible
@bot.message_handler(commands=["invisible"])
def invisible(message, chat_id = False, user_id = False):
    if not chat_id:
        chat_id = message.chat.id
    if not user_id:
        user_id = message.from_user.id

    try:
        with closing(pymysql.connect(
            host=config.DATABASE_CONFIG['host'],
            user=config.DATABASE_CONFIG['user'],
            password=config.DATABASE_CONFIG['password'],
            db=config.DATABASE_CONFIG['db'],
            charset=config.DATABASE_CONFIG['charset'],
            cursorclass=DictCursor
        )) as connection:
            with connection.cursor() as cursor:
                query = "UPDATE users SET visible = 0 WHERE user_id = " + str(user_id)
                cursor.execute(query)
                connection.commit()
                bot.send_message(chat_id, u"Твой ник не отображается в чате")
    except Exception as exc:
        print ('invisible')
        print (exc)

@bot.message_handler(commands=["weather"])
def weather(message, chat_id = False, user_id = False):
    if not chat_id:
        chat_id = message.chat.id
    if not user_id:
        user_id = message.from_user.id


    owm = pyowm.OWM(config.API['OWMapikey'])
    observation = owm.weather_at_place('Moscow')
    w = observation.get_weather()
    temp = str(w.get_temperature('celsius')['temp']).split('.')[0]
    bot.send_message(chat_id, 'Temperature: ' + temp + ' C')

'''
ECHO
'''
@bot.message_handler(content_types=["text", "sticker", "pinned_message", "document", "photo", "audio", "voice", "video"])
def echo_all(message):
    try:
        # new chat
        if not check_chat(message):
            print('New chat ' + str(message.chat.id))
            save_chat(message)

        chats = load_chats()

        if check_visible(message):
            username = message.from_user.username
        else:
            username = u"Аноним"

        # echo message
        for chat in chats:
            if chat:# and str(message.chat.id) != chat:
                if message.content_type == 'text':
                    bot.send_message(chat, username + u" отправил:\n" + message.text)
                if message.content_type == 'photo':
                    bot.send_message(chat, username + u" отправил: ")
                    for photo in message.photo:
                        bot.send_photo(chat, photo.file_id)
                if message.content_type == 'sticker':
                    bot.send_message(chat, username + u" отправил: ")
                    bot.send_sticker(chat, message.sticker.file_id)
                if message.content_type == 'audio':
                    bot.send_message(chat, username + u" отправил: ")
                    bot.send_audio(chat, message.audio.file_id)
                if message.content_type == 'voice':
                    bot.send_message(chat, username + u" отправил: ")
                    bot.send_voice(chat, message.voice.file_id)
                if message.content_type == 'video':
                    bot.send_message(chat, username + u" отправил: ")
                    bot.send_video(chat, message.video.file_id)
                if message.content_type == 'document':
                    bot.send_message(chat, username + u" отправил: ")
                    bot.send_document(chat, message.document.file_id)

    except Exception as exc:
        print ("Error echo")
        print (exc)

start_server()