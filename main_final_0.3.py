from atexit import register
from email import message
from os import remove
import requests
from bs4 import BeautifulSoup as b
import json
import telebot
from telebot import types
from dop import pars_new_post, pars_one_post
from work_with_json import json_now_post, json_remove_avtor

API_KEY = '5324085182:AAGOgFlXmC691d9ItR2vhy28l2nhaYYDJ48'
# URL = 'https://joyreactor.cc/'



with open('spisok.json', 'r') as file:      # открываем файл на чтение и достаём значение json файла
    meta = json.load(file)
file.close()

meta_list = list(meta.keys())               # делаем из словаря список с ключами, в нашем случае это URL ссылки


def separator_name(URL):
        buf = URL.split("/")
        # print(len(buf))
        if (len(buf) > 3):
            # print(buf[4])
            return (buf[4])
        else:
            # print(buf[2]) 
            return (buf[2])






bot = telebot.TeleBot(API_KEY)

@bot.message_handler(commands=['go'])
def hello(message):
    for URL in meta_list:
        list_exit = pars_new_post(URL)             # пишем в переменную list_exit наш список постов, которые надо выгрузить (значение приходит из парсера функции pars_new_post)
        if (list_exit):
            bot.send_message(message.chat.id, " 👉🏻 "+separator_name(URL)+" 👈🏻 ")
        for item in list_exit:
            bot.send_message(message.chat.id, "https://joyreactor.cc"+item)
    list_exit.clear()                                                         # чистим список после выгрузки постов


# @bot.message_handler(commands=['add_1'])    # команда на добавление нового автора в список расслыки
# def add(message):

#     with open('spisok.json', 'r') as file: 
#         meta = json.load(file)
#     file.close()

#     meta[10] = 'ten'

#     with open('spisok.json', 'w') as file:
#         json.dump(meta, file, indent=4)
#     file.close()

#     bot.send_message(message.chat.id, "команда add выполнена")


@bot.message_handler(commands=['add'])    # команда берёт текст, который мы отправляем после команды '/add'
def add(message):
    sent = bot.reply_to(message, 'команда на добавление нового автора')
    bot.register_next_step_handler(sent, review)

def review(message):                        # сей конструкцией мы получаем текст из телеграмма, в нашем случае URL на автора
    message_to_save = message.text
    print(message_to_save)

    one_post = pars_one_post(message_to_save)   # модуль парсера для поиска отдного первого поста 

    json_now_post(message_to_save, one_post)    # модуль, добавдяющий в json нового автора (в качестве аргумента передаётся URL и первый пост автора)

    bot.send_message(message.chat.id, "команда add выполнена")




@bot.message_handler(commands=['remove'])    # команда берёт текст, который мы отправляем после команды '/remove'
def remove(message):
    sent = bot.reply_to(message, 'команда на удаление автора')
    bot.register_next_step_handler(sent, review1)

def review1(message):                        # сей конструкцией мы получаем текст из телеграмма, в нашем случае URL на автора
    message_to_save1 = message.text
    print(message_to_save1)

    json_remove_avtor(message_to_save1)     # модуль, удаляющий в json автора (в качестве аргумента передаётся URL)

    

    bot.send_message(message.chat.id, "команда remove выполнена")












@bot.message_handler(commands=['help'])    # конструкция для кнопок
def knopka(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    add = types.KeyboardButton ('/add')                         # добавляет конпку с командой ('/add')
    remove = types.KeyboardButton ('/remove')                   # добавляет конпку с командой ('/rEMOVE')
    markup.add(add, remove)                                     # в толбар добавялет объектами кнопок
    bot.send_message(message.chat.id, "help - тупо разворот для бара + обновление кнопок(команд)", reply_markup=markup)






@bot.message_handler()      # обработчик рандомных команд
def error(message):
    bot.send_message(message.chat.id, "введена неверная команда")

bot.polling()
# "/post/5294088"
