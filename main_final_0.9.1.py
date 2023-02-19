import time
from ast import Try
from atexit import register
from email import message
from http.client import responses
from os import remove
from tabnanny import check
import requests
from bs4 import BeautifulSoup as b
import json
import threading
import telebot
import threading

from telebot import types

from dop import *
from work_with_json import *
from hello import *

API_KEY = '5324085182:AAGOgFlXmC691d9ItR2vhy28l2nhaYYDJ48'
bot = telebot.TeleBot(API_KEY)


# Основная функция. Парсит значения из json и выдаёт посты

@bot.message_handler(commands=['go'])
def test(message):
    thr = threading.Thread(target=hello, args=(message,), name="osnova")
    thr.start()


@bot.message_handler(commands=['add'])  # команда берёт текст, который мы отправляем после команды '/add'
def add(message):
    sent = bot.reply_to(message, 'пришлите мне нового автора')
    bot.register_next_step_handler(sent, review)


def review(message):  # сей конструкцией мы получаем текст из телеграмма, в нашем случае URL на автора
    message_to_save_add = message.text
    print(message_to_save_add)

    if (
            message_to_save_add == "https://joyreactor.cc/tag/" or message_to_save_add == "https://joyreactor.cc/user/"):  # исключение для пустого тега
        bot.send_message(message.chat.id, "Передан не верный URL. URL имеет тип https://joyreactor.cc/tag/ник_автора")
        return 0

    elif (message_to_save_add.find("/post/") != -1):
        bot.send_message(message.chat.id, "вы передали пост, а не тег или автора")
        return 0

    elif (message_to_save_add.find(
            "reactor.cc/") != -1):  # ищем подстроку в строке и возвращаем индекс первого вхождения. для нас достаточно определить что эта подстрока впринципе есть

        one_post = pars_one_post(message_to_save_add)  # модуль парсера для поиска отдного первого поста
        if (one_post == "404"):
            bot.send_message(message.chat.id, "такого автора/тега не существует")
            return 0

        if (chek_list_key_json(message_to_save_add,
                               str(message.from_user.id)) == 1):  # проверяет есть ли поданый телегой автор в СПИСКЕ авторов json
            bot.send_message(message.chat.id, "такой автор уже есть в списке")
            return 0

        json_now_post(message_to_save_add, one_post,
                      str(message.from_user.id))  # модуль, добавдяющий в json нового автора (в качестве аргумента передаётся URL и первый пост автора)
        bot.send_message(message.chat.id, "команда add выполнена")

    else:  # в случае если URL пришёл биты - выводим ошибку - выходим
        bot.send_message(message.chat.id, "Передан не верный URL. URL имеет тип https://joyreactor.cc/tag/ник_автора")
        return 0


@bot.message_handler(commands=['remove'])  # команда берёт текст, который мы отправляем после команды '/remove'
def remove(message):
    sent = bot.reply_to(message, 'какого автора надо удалить?')
    bot.register_next_step_handler(sent, review1)


def review1(message):  # сей конструкцией мы получаем текст из телеграмма, в нашем случае URL на автора
    message_to_save_remove = message.text
    print(message_to_save_remove)

    if (
            message_to_save_remove == "https://joyreactor.cc/tag/" or message_to_save_remove == "https://joyreactor.cc/user/"):
        bot.send_message(message.chat.id, "Передан не верный URL. URL имеет тип https://joyreactor.cc/tag/ник_автора")
        return 0

    elif (message_to_save_remove.find("/post/") != -1):
        bot.send_message(message.chat.id, "вы передали пост, а не тег или автора")
        return 0

    elif (message_to_save_remove.find(
            "reactor.cc/tag/") != -1):  # ищем подстроку в строке и возвращаем индекс первого вхождения. для нас достаточно определить что эта подстрока впринципе есть

        if (chek_list_key_json(message_to_save_remove,
                               str(message.from_user.id)) == 0):  # проверяет есть ли поданый телегой автор в СПИСКЕ авторов json
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
    with open(str(message.from_user.id) + '.json',
              'r') as file:  # открываем файл на чтение и достаём значение json файла
        meta = json.load(file)
    file.close()

    if len(meta) == 0:  # проверка списка на пустоту. если пустой - завершает команду
        bot.send_message(message.chat.id, "Ваш список пуст")
        return 0

    list_chek = list(meta.keys())  # делаем из словаря список с ключами, в нашем случае это URL ссылки
    print(list_chek)

    bot.send_message(message.chat.id, '\n'.join(list_chek))

    buf = str(message.from_user.id)
    print(type(buf))

    # print(threading.active_count())
    # print(threading.enumerate())
    # print(threading)


@bot.message_handler(commands=['one_post'])
def one_post(message):
    buf = bot.reply_to(message, 'в ответ скинь мне ссылку на пост')
    bot.register_next_step_handler(buf, pull)


def pull(message):  # сей конструкцией мы получаем текст из телеграмма, в нашем случае URL на автора
    message_to_save_pul = message.text
    print(message_to_save_pul)

    if (message_to_save_pul.find(
            "reactor.cc/post/") == -1):  # защита входящих ссылок на соответствие шаблону ниже, если не соотвектствует, то выдаёт ошибку
        bot.send_message(message.chat.id, "Передан не верный URL. URL имеет тип https://joyreactor.cc/post/...")
        return 0

    one_post = pars_one_post(
        message_to_save_pul)  # защита от битых ссылок      # модуль парсера для поиска отдного первого поста
    if one_post == "404":
        bot.send_message(message.chat.id, "такого поста не существует")
        return 0

    r = requests.get(message_to_save_pul)
    # print(r.status_code)     # статус обработки (200) - всё заебок, сайт читается

    soup = b(r.text, 'html.parser')

    if (valid_page_2_video(
            soup) == 1):  # ссылка на ютуб!  обращение к функции из файла dop - функция чекает строчку ниже на читаемость и оборачивыает в try except
        # print ("111")
        page_2 = soup.find_all("iframe", class_="youtube-player")
        r = list()

        if len(page_2) != 0:
            for g in page_2:
                r.append(g.get("src"))
            bot.send_message(message.chat.id, '\n'.join(r))
            # return 0

    #     bot.send_message(message.chat.id, '\n'.join(r))

    if (valid_page_2(
            soup) == 0):  # обращение к функции из файла dop - функция чекает строчку ниже на читаемость и оборачивыает в try except
        bot.send_message(message.chat.id,
                         message_to_save_pul + " не удаётся распарсить контейнер с данными. Возможно контент заблокирован администрацией")
        return 0

    page_2 = soup.find("div", class_="post_top").find("div", class_="post_content").find_all("div", class_="image")

    # for g in page_2:    #показыват все списки class_="link"
    #     print(g)

    def pars_param_src(
            buff):  # функция для проверки класса на возможность пропарсить объекты класса тегом "src"  # если не парситься, то return 0

        try:
            page_3 = buff.img.get("src")
            return page_3

        except Exception as _ex:
            return 0

    def pars_param_href(
            buff):  # функция для проверки класса на возможность пропарсить объекты класса тегом "src"  # если не парситься, то return 0

        try:
            page_3 = buff.a.get("href")
            return page_3

        except Exception as _ex:
            return 0

    i = 0
    list_href = list()
    list_src = list()
    print(len(page_2))
    while i < (len(page_2)):

        object_src = pars_param_src(page_2[i])
        object_href = pars_param_href(page_2[i])
        print("src = ", object_src)
        print("href = ", object_href)
        i += 1

        if object_src != 0 and object_href != 0 and object_href != "javascript:":
            print('111')
            list_href.append('https:' + object_href)

        elif object_src != 0 and object_href == 0:
            print('111')
            list_src.append('https:' + object_src)

        elif object_src != 0 and object_href != 0 and object_href == "javascript:":
            print('111')
            list_src.append('https:' + object_src)

    print(list_href)
    print(list_src)

    try:

        if len(list_href) == 0:
            print("список list_href пуст")

        elif len(list_href) > 10:  # собирает специальный список "r" по объёму подходящий для метода InputMediaPhoto и отправляет в чат
            i = 1
            r = list()
            r.append(types.InputMediaDocument(list_href[0]))
            while i < len(list_href):
                r.append(types.InputMediaDocument(list_href[i]))
                # print(i)
                print(types.InputMediaDocument(list_href[i]))
                if (i % 9) == 0:
                    bot.send_media_group(message.chat.id, r)
                    r = []
                    print('девяточка')
                i += 1

            bot.send_media_group(message.chat.id, r)

        else:  # если list_href меньше 10, то выполняется эта чать блока - без танцев с бубном
            r = list()
            for item in list_href:
                r.append(types.InputMediaDocument(item))

            bot.send_media_group(message.chat.id, r)

        if len(list_src) == 0:
            print("список list_src пуст")

        elif len(list_src) > 10:  # данный блок собирает специальный список "r" по объёму подходящий для метода InputMediaPhoto и отправляет в чат
            i = 1
            r = list()
            r.append(types.InputMediaPhoto(list_src[0]))
            while i < len(list_src):
                r.append(types.InputMediaPhoto(list_src[i]))
                # print(i)
                print(types.InputMediaPhoto(list_src[i]))
                if (i % 9) == 0:
                    bot.send_media_group(message.chat.id, r)
                    r = []
                    print('девяточка')
                i += 1

            bot.send_media_group(message.chat.id, r)

        else:  # если list_src меньше 10, то выполняется эта чать блока - без танцев с бубном
            r = list()
            for item in list_src:
                r.append(types.InputMediaPhoto(item))

            bot.send_media_group(message.chat.id, r)


    except Exception as _ex:
        print("не прочиталось!")

@bot.message_handler(commands=['test_href'])




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
    bot.send_message(message.chat.id, "введите /help чтобы увидеть список команд")


bot.polling()


# https://anime.reactor.cc/post/2831065

# пост с 3 видео https://joyreactor.cc/post/5299310

# пост , в котором есть и href, и src файл !!! https://joyreactor.cc/post/5015308
