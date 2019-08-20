# -*- coding: utf-8 -*-
import telebot
from telebot import apihelper
from telebot import types
import pymysql
from pymysql.cursors import DictCursor
from contextlib import closing
import pyowm
import config
import os
from PIL import Image, ImageDraw

# Proxy
#apihelper.proxy = {
#    'https': config.PROXY
#}
# Telebot
bot = telebot.TeleBot(config.API['TelegramApiKey'])

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
        message.from_user.username + u"\nЭто чат, ты здесь можешь отправить сообщение и другие его увидят")
    try:
        if not check_chat(message):
            print('New chat ' + str(message.chat.id))
            save_chat(message)
            help(message)
    except Exception as exc:
        print (exc)


@bot.message_handler(commands=["help"])
def help(message):
    markup = telebot.types.InlineKeyboardMarkup()
    buttonv = telebot.types.InlineKeyboardButton(text='visible', callback_data='visible')
    buttoni = telebot.types.InlineKeyboardButton(text='invisible', callback_data='invisible')
    buttonw = telebot.types.InlineKeyboardButton(text='weather', callback_data='weather')
    buttonr = telebot.types.InlineKeyboardButton(text='resize image for sticker', callback_data='resize_image_for_sticker')
    markup.add(buttonv)
    markup.add(buttoni)
    markup.add(buttonw)
    markup.add(buttonr)
    bot.send_message(chat_id=message.from_user.id, text='Help', reply_markup=markup)

# button handler
@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    if call.message:
        if call.data:
            if call.data == 'visible':
                visible(call.message)
                bot.answer_callback_query(callback_query_id=call.id, text='visible')
            if call.data == 'invisible':
                invisible(call.message)
                bot.answer_callback_query(callback_query_id=call.id, text='invisible')
            if call.data == 'weather':
                weather(call.message)
                bot.answer_callback_query(callback_query_id=call.id, text='weather')
            if call.data == 'resize_image_for_sticker':
                switch_resize_image_for_sticker(call.message)
                bot.answer_callback_query(callback_query_id=call.id, text='resize_image_for_sticker')

# visible
@bot.message_handler(commands=["visible"])
def visible(message):
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
                query = "UPDATE users SET visible = 1 WHERE user_id = " + str(message.from_user.id)
                cursor.execute(query)
                connection.commit()
                bot.send_message(message.chat.id, u"Твой ник видно в чате")
    except Exception as exc:
        print ('visible')
        print (exc)

# invisible
@bot.message_handler(commands=["invisible"])
def invisible(message):
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
                query = "UPDATE users SET visible = 0 WHERE user_id = " + str(message.from_user.id)
                cursor.execute(query)
                connection.commit()
                bot.send_message(message.chat.id, u"Твой ник не отображается в чате")
    except Exception as exc:
        print ('invisible')
        print (exc)

# weather
@bot.message_handler(commands=["weather"])
def weather(message):
    owm = pyowm.OWM(config.API['OWMApiKey'])
    observation = owm.weather_at_place('Moscow')
    w = observation.get_weather()
    temp = str(w.get_temperature('celsius')['temp']).split('.')[0]
    bot.send_message(message.chat.id, 'Temperature: ' + temp + ' C')

# resize for telegram sticker
need_resize_image_for_sticker = False
@bot.message_handler(commands=["resize_image_for_sticker"])
def switch_resize_image_for_sticker(message):
    global need_resize_image_for_sticker
    need_resize_image_for_sticker = not need_resize_image_for_sticker
    if need_resize_image_for_sticker == True:
        bot.send_message(message.chat.id, 'Для преобразования изображения для стикера отправьте jpg или png')
    else:
        bot.send_message(message.chat.id, 'Преобразование для стикера отменено')

def resize_image_for_sticker(message):
    try:
        file = bot.download_file(bot.get_file(message.document.file_id).file_path)
        src_original = message.document.file_name
        with open(src_original, 'wb') as new_file:
            new_file.write(file)
        image = Image.open(src_original)
        width = image.width
        height = image.height
        if width > 512 or height > 512:
            if width > height:
                factor = 512 / width
            else:
                factor = 512 / height
        image = image.resize((int(width * factor), int(height * factor)), Image.ANTIALIAS)

        src_converted = 'converted_' + message.document.file_name
        image.save(src_converted, "PNG")
        if message.document.mime_type == 'image/jpeg' or message.document.mime_type == 'image/png':
            bot.send_document(message.from_user.id, open(src_converted, 'rb'))
            bot.send_message(message.chat.id, 'Изображение преобразовано')
            if os.path.isfile(src_converted):
                os.remove(src_converted)
                if os.path.isfile(src_original):
                    os.remove(src_original)
                    need_resize_image_for_sticker = False
                else:
                    print("Error: %s file not found" % src_converted)
            else:
                print("Error: %s file not found" % src_converted)
        else:
            bot.send_message(message.chat.id, 'Отправьте jpg или png')
    except Exception as exc:
        print ("Error resize")
        print (exc)
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
                    if need_resize_image_for_sticker == True:
                        resize_image_for_sticker(message)
                    else:
                        bot.send_message(chat, username + u" отправил: ")
                        bot.send_document(chat, message.document.file_id)

    except Exception as exc:
        print ("Error echo")
        print (exc)

start_server()
