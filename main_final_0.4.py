from atexit import register
from email import message
from os import remove
import requests
from bs4 import BeautifulSoup as b
import json
import telebot
from telebot import types

from dop import pars_new_post, pars_one_post, separator_name, chek_list_key_json
from work_with_json import json_now_post, json_remove_avtor

API_KEY = '5324085182:AAGOgFlXmC691d9ItR2vhy28l2nhaYYDJ48'
bot = telebot.TeleBot(API_KEY)


# Основная функция. Парсит значения из json и выдаёт посты

@bot.message_handler(commands=['go'])
def hello(message):

    with open('spisok.json', 'r') as file:      # открываем файл на чтение и достаём значение json файла
        meta = json.load(file)
    file.close()

    meta_list = list(meta.keys())               # делаем из словаря список с ключами, в нашем случае это URL ссылки


    for URL in meta_list:
        list_exit = pars_new_post(URL)             # пишем в переменную list_exit наш список постов, которые надо выгрузить (значение приходит из парсера функции pars_new_post)
        if (list_exit):
            bot.send_message(message.chat.id, " 👉🏻 "+separator_name(URL)+" 👈🏻 ")
        for item in list_exit:
            bot.send_message(message.chat.id, "https://joyreactor.cc"+item)
    list_exit.clear()                                                         # чистим список после выгрузки постов




@bot.message_handler(commands=['add'])    # команда берёт текст, который мы отправляем после команды '/add'
def add(message):
    sent = bot.reply_to(message, 'команда на добавление нового автора')
    bot.register_next_step_handler(sent, review)

def review(message):                        # сей конструкцией мы получаем текст из телеграмма, в нашем случае URL на автора
    message_to_save_add = message.text
    print(message_to_save_add)

    if (message_to_save_add == "https://joyreactor.cc/tag/"):
        bot.send_message(message.chat.id, "Передан не верный URL. URL имеет тип https://joyreactor.cc/tag/ник_автора")
        return 0        
    elif (message_to_save_add.startswith("https://joyreactor.cc/tag/") == True):

        one_post = pars_one_post(message_to_save_add)   # модуль парсера для поиска отдного первого поста 
        if (one_post == "404"):
            bot.send_message(message.chat.id, "такого автора/тега не существует")
            return 0


        if (chek_list_key_json(message_to_save_add) == 1):      # проверяет есть ли поданый телегой автор в СПИСКЕ авторов json
            bot.send_message(message.chat.id, "такой автор уже есть в списке")
            return 0



        json_now_post(message_to_save_add, one_post)    # модуль, добавдяющий в json нового автора (в качестве аргумента передаётся URL и первый пост автора)
        bot.send_message(message.chat.id, "команда add выполнена")

    else:
        bot.send_message(message.chat.id, "Передан не верный URL. URL имеет тип https://joyreactor.cc/tag/ник_автора")
        return 0




@bot.message_handler(commands=['remove'])    # команда берёт текст, который мы отправляем после команды '/remove'
def remove(message):
    sent = bot.reply_to(message, 'команда на удаление автора')
    bot.register_next_step_handler(sent, review1)

def review1(message):                        # сей конструкцией мы получаем текст из телеграмма, в нашем случае URL на автора
    message_to_save_remove = message.text
    print(message_to_save_remove)

    if (message_to_save_remove == "https://joyreactor.cc/tag/"):
        bot.send_message(message.chat.id, "Передан не верный URL. URL имеет тип https://joyreactor.cc/tag/ник_автора")
        return 0        
    
    elif (message_to_save_remove.startswith("https://joyreactor.cc/tag/") == True):



        if (chek_list_key_json(message_to_save_remove) == 0):      # проверяет есть ли поданый телегой автор в СПИСКЕ авторов json
            bot.send_message(message.chat.id, "такого автора нет в списке")
            return 0




        json_remove_avtor(message_to_save_remove)     # модуль, удаляющий в json автора (в качестве аргумента передаётся URL)
        bot.send_message(message.chat.id, "команда remove выполнена")

    else:
        bot.send_message(message.chat.id, "Передан не верный URL. URL имеет тип https://joyreactor.cc/tag/ник_автора")
        return 0



@bot.message_handler(commands=['list'])
def list_chek(message):

    with open('spisok.json', 'r') as file:      # открываем файл на чтение и достаём значение json файла
        meta = json.load(file)
    file.close()

    list_chek = list(meta.keys())               # делаем из словаря список с ключами, в нашем случае это URL ссылки
    bot.send_message(message.chat.id, '\n'.join(list_chek))






@bot.message_handler(commands=['help'])    # конструкция для кнопок
def knopka(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    add = types.KeyboardButton ('/add')                         # добавляет кнопку с командой ('/add')
    remove = types.KeyboardButton ('/remove')                   # добавляет кнопку с командой ('/remove')
    go = types.KeyboardButton ('/go')                           # добавляет кнопку с командой ('/go')
    list = types.KeyboardButton ('/list')                           # добавляет кнопку с командой ('/list')
    markup.add(add, remove, go, list)                                 # в толбар добавялет объектами кнопок
    bot.send_message(message.chat.id, "help - тупо разворот для бара + обновление кнопок(команд)", reply_markup=markup)






@bot.message_handler()      # обработчик рандомных команд
def error(message):
    bot.send_message(message.chat.id, "введите команду /help чтобы увидеть список команд")

bot.polling()
# "/post/5294088"
