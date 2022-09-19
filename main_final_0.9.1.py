from ast import Try
from atexit import register
from email import message
from http.client import responses
from os import remove
from tabnanny import check
import requests
from bs4 import BeautifulSoup as b
import json
import telebot

from telebot import types

from dop import *
from work_with_json import *
from main_algorithm import *

API_KEY = '5324085182:AAGOgFlXmC691d9ItR2vhy28l2nhaYYDJ48'
bot = telebot.TeleBot(API_KEY)


# Основная функция. Парсит значения из json и выдаёт посты
@bot.message_handler(commands=['go'])
def hello(message):
    with open(str(message.from_user.id) + '.json', 'r') as file:  # открываем файл на чтение и достаём значение json файла
        meta = json.load(file)
    file.close()

    # делаем из словаря список с ключами 
    # в нашем случае это URL ссылки
    meta_list = list(meta.keys())

    # проверка списка на пустоту. 
    # если пустой - завершает команду
    if len(meta) == 0:
        bot.send_message(message.chat.id, "В вашем списке авторов, добавьте автора в список авторов, чтобы команда /go заработала")
        return 0

    for URL in meta_list:
        list_exit = pars_new_post(URL, str(message.from_user.id))  # пишем в переменную list_exit наш список постов, которые надо выгрузить (значение приходит из парсера функции pars_new_post)
        if (list_exit):
            bot.send_message(message.chat.id, " 👉🏻 " + separator_name(URL) + " 👈🏻 ")
        for item in list_exit:

            r = requests.get("https://joyreactor.cc" + item)
            # print(r.status_code)     # статус обработки (200) - всё заебок, сайт читается

            soup = b(r.text, 'html.parser')

            if (valid_page_2(soup) == 0):
                bot.send_message(message.chat.id, "https://joyreactor.cc" + item + " не удаётся распарсить контейнер с данными. Возможно контент заблокирован администрацией")
                continue


            # обращение к функции из файла dop - функция чекает soup на читаемость 
            # и оборачивыает в try except - 
            # смотрит есть ли в блоке с медиа ссылки на ютуб 
            # если есть, то выгружает, игнарируя весь остальной контент в посте

            if (valid_page_2_video(soup) == 1): 
                page_2 = soup.find_all("iframe", class_="youtube-player")
                r = list()

                if len(page_2) != 0:
                    print("video found")
                    for g in page_2:
                        r.append(g.get("src"))
                    bot.send_message(message.chat.id, '\n'.join(r))
                    # continue



            if (valid_page_2_gif(soup) == 1):    
                page_2 = soup.find_all("a", class_="video_gif_source")
                print(page_2)


                if len(page_2) != 0:
                    for g in page_2:
                        push = "https:"+g.get("href")
                        bot.send_message (message.chat.id, push)
                continue

            page_2 = soup.find("div", class_="post_top").find("div", class_="post_content").find_all("div", class_="image")

            # основной алгоритм по обработке пикчей
            main_algorithm(soup, message)

    list_exit.clear()  # чистим список после выгрузки постов


@bot.message_handler(commands=['add'])  # команда берёт текст, который мы отправляем после команды '/add'
def add(message):
    sent = bot.reply_to(message, 'команда на добавление нового автора')
    bot.register_next_step_handler(sent, review)


# сей конструкцией мы получаем текст из телеграмма, в нашем случае URL на автора
def review(message):
    message_to_save_add = message.text
    print(message_to_save_add)

# исключение для пустых тегов
    if (message_to_save_add == "https://joyreactor.cc/tag/" or message_to_save_add == "https://joyreactor.cc/user/"):
        bot.send_message(message.chat.id, "Передан не верный URL. URL имеет тип https://joyreactor.cc/tag/ник_автора")
        return 0

# защита на подаваемый аргумен - отсеивает посты 
    elif (message_to_save_add.find("/post/") != -1):
        bot.send_message(message.chat.id, "вы передали пост, а не автора или тег")
        return 0

# ищем подстроку в строке и возвращаем индекс первого вхождения. 
# Для нас достаточно определить что эта подстрока впринципе есть
    elif (message_to_save_add.find("reactor.cc/") != -1):

# модуль парсера для поиска отдного первого поста
        one_post = pars_one_post(message_to_save_add) 
        if (one_post == "404"):
            bot.send_message(message.chat.id, "такого автора/тега не существует")
            return 0

# проверяет есть ли поданый автор в СПИСКЕ авторов в json файле   --- уточнить в чём защита
        if (chek_list_key_json(message_to_save_add, str(message.from_user.id)) == 1):
            bot.send_message(message.chat.id, "такой автор уже есть в списке")
            return 0

# модуль, добавдяющий в json нового автора (в качестве аргумента передаётся URL и первый пост автора)
        json_now_post(message_to_save_add, one_post, str(message.from_user.id))
        bot.send_message(message.chat.id, "команда add выполнена")

# в случае если URL пришёл биты - выводим ошибку - выходим
    else:
        bot.send_message(message.chat.id, "Передан не верный URL. URL имеет тип https://joyreactor.cc/tag/ник_автора-тег")
        return 0


# функция на удаление автора из списка отслеживаемых авторов 
# команда берёт текст, который мы отправляем в ответ после команды '/remove'
@bot.message_handler(commands=['remove'])
def remove(message):
    sent = bot.reply_to(message, 'команда на удаление автора')
    bot.register_next_step_handler(sent, review1)

# перекладываем текст нашего ответного сообщения в переменную
def review1(message):
    message_to_save_remove = message.text
    print(message_to_save_remove)

# исключение для пустых тегов
    if (message_to_save_remove == "https://joyreactor.cc/tag/" or message_to_save_remove == "https://joyreactor.cc/user/"):
        bot.send_message(message.chat.id, "Передан не верный URL. URL имеет тип https://joyreactor.cc/tag/ник_автора")
        return 0

# защита на подаваемый аргумен - отсеивает посты 
    elif (message_to_save_remove.find("/post/") != -1):
        bot.send_message(message.chat.id, "вы передали пост, а не тег автора или автора")
        return 0

# Ищем подстроку в строке и возвращаем индекс первого вхождения. 
# Для нас достаточно определить что эта подстрока впринципе есть
    elif (message_to_save_remove.find("reactor.cc/tag/") != -1):

        if (chek_list_key_json(message_to_save_remove, str(message.from_user.id)) == 0):  # проверяет есть ли поданый телегой автор в СПИСКЕ авторов json
            bot.send_message(message.chat.id, "такого автора нет в списке")
            return 0

        json_remove_avtor(message_to_save_remove,
                          str(message.from_user.id))  # модуль, удаляющий в json автора (в качестве аргумента передаётся URL)
        bot.send_message(message.chat.id, "команда remove выполнена")

    else:
        bot.send_message(message.chat.id, "Передан не верный URL. URL имеет тип https://joyreactor.cc/tag/ник_автора")
        return 0


@bot.message_handler(commands=['list'])
def list_chek(message):

    # открываем файл на чтение и достаём значение json файла
    with open(str(message.from_user.id) + '.json','r') as file:
        meta = json.load(file)
    file.close()

    # проверка списка на пустоту. если пустой - завершает команду
    if len(meta) == 0:
        bot.send_message(message.chat.id, "Ваш список пуст")
        return 0

    # делаем из словаря список с ключами, в нашем случае это URL ссылки
    list_chek = list(meta.keys())
    print(list_chek)

    bot.send_message(message.chat.id, '\n'.join(list_chek))

    buf = str(message.from_user.id)
    print(type(buf))


@bot.message_handler(commands=['one_post'])
def one_post(message):
    buf = bot.reply_to(message, 'в ответ скинь мне ссылку на пост')
    bot.register_next_step_handler(buf, pull)

# перекладываем текст нашего ответного сообщения в переменную
def pull(message):
    message_to_save_pul = message.text
    print(message_to_save_pul)

    # защита входящих ссылок на соответствие шаблону ниже, если не соотвектствует, то выдаёт ошибку
    if (message_to_save_pul.find("reactor.cc/post/") == -1):
        bot.send_message(message.chat.id, "Передан не верный URL. URL имеет тип https://joyreactor.cc/post/...")
        return (0)

    # защита от битых ссылок      
    # модуль парсера для поиска отдного первого поста
    one_post = pars_one_post(message_to_save_pul)
    if (one_post == "404"):
        bot.send_message(message.chat.id, "такого поста не существует")
        return (0)

    r = requests.get(message_to_save_pul)
    # print(r.status_code)     # статус обработки (200) - всё заебок, сайт читается

    soup = b(r.text, 'html.parser')


# обработка ссылок на ютуб
# обращение к функции из файла dop - функция чекает строчку ниже на читаемость
# и оборачивыает в try except
# вывод осужествляется через сообщения в чате

    if (valid_page_2_video(soup) == 1):
        page_2 = soup.find_all("iframe", class_="youtube-player")
        r = list()

        if len(page_2) != 0:
            for g in page_2:
                r.append(g.get("src"))
            bot.send_message(message.chat.id, '\n'.join(r))
            # return 0

# обработка gif
# обращение к функции из файла dop - функция чекает строчку ниже на читаемость
# и оборачивыает в try except
# вывод осужествляется через сообщения в чате

    if (valid_page_2_gif(soup) == 1):
        page_2 = soup.find_all("a", class_="video_gif_source")
        print(page_2)

        if len(page_2) != 0:
            for g in page_2:
                push = "https:"+g.get("href")
                bot.send_message (message.chat.id, push)
        return 0

    # чекает soup на читаемость и оборачивыает в try except
    if (valid_page_2(soup) == 0):
        bot.send_message(message.chat.id, message_to_save_pul + " не удаётся распарсить контейнер с данными. Возможно контент заблокирован администрацией")
        return 0

    # основной алгоритм по обработке пикчей
    main_algorithm(soup, message)



@bot.message_handler(commands=['help'])  # конструкция для кнопок
def knopka(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    add = types.KeyboardButton('/add')  # добавляет кнопку с командой ('/add')
    remove = types.KeyboardButton('/remove')  # добавляет кнопку с командой ('/remove')
    go = types.KeyboardButton('/go')  # добавляет кнопку с командой ('/go')
    list = types.KeyboardButton('/list')  # добавляет кнопку с командой ('/list')
    one_post = types.KeyboardButton('/one_post')
    test = types.KeyboardButton('/test_href')
    markup.add(add, remove, go, list, one_post, test)  # в толбар добавялет объектами кнопок
    bot.send_message(message.chat.id, "help - тупо разворот для бара + обновление кнопок(команд)", reply_markup=markup)


@bot.message_handler()  # обработчик рандомных команд
def error(message):
    bot.send_message(message.chat.id, "введите команду /help чтобы увидеть список команд")


bot.polling()
# https://anime.reactor.cc/post/2831065

# пост с 3 видео https://joyreactor.cc/post/5299310

# пост , в котором есть и href, и src файл !!! https://joyreactor.cc/post/5015308

# работа с асинхронкой https://telegra.ph/Zapusk-funkcij-v-bote-po-tajmeru-11-28