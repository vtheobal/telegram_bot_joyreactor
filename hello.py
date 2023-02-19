import json
import time

import telebot

from telebot import types

from dop import *
from work_with_json import *

API_KEY = '6027340474:AAG4dJ79uYBwtXHGdmKlSSKLAYC8p1Qe9oo'
bot = telebot.TeleBot(API_KEY)

def hello(message):
    while True:
        print("начало цикла")
        with open(str(message.from_user.id) + '.json',
                  'r') as file:  # открываем файл на чтение и достаём значение json файла
            meta = json.load(file)
        file.close()

        meta_list = list(meta.keys())  # делаем из словаря список с ключами, в нашем случае это URL ссылки

        # if len(meta) == 0:  # проверка списка на пустоту. если пустой - завершает команду
        #     bot.send_message(message.chat.id, "ваш список пуст, добавьте автора или тег, чтобы команда /go заработала")
        #     return 0

        for URL in meta_list:
            list_exit = pars_new_post(URL,
                                      str(message.from_user.id))  # пишем в переменную list_exit наш список постов, которые надо выгрузить (значение приходит из парсера функции pars_new_post)
            if list_exit:
                # bot.send_message(message.chat.id, " 👉🏻 " + separator_name(URL) + " 👈🏻 ")
                bot.send_message(message.chat.id, URL)
            for item in list_exit:

                r = requests.get("https://joyreactor.cc" + item)
                # print(r.status_code)     # статус обработки (200) - всё заебок, сайт читается

                soup = b(r.text, 'html.parser')

                if valid_page_2_video(
                        soup) == 1:  # обращение к функции из файла dop - функция чекает строчку ниже на читаемость и оборачивыает в try except - смотрит есть ли в блоке с медиа файлы на ютуб если есть, то выгружает только ссылки на ютуб, игнарируя весь остальной контент в посте
                    print("111")
                    page_2 = soup.find_all("iframe", class_="youtube-player")
                    r = list()

                    if len(page_2) != 0:
                        for g in page_2:
                            r.append(g.get("src"))
                        bot.send_message(message.chat.id, '\n'.join(r))
                        # continue

                if valid_page_2(soup) == 0:
                    bot.send_message(message.chat.id,
                                     "https://joyreactor.cc" + item + " не удаётся распарсить контейнер с данными. Возможно контент заблокирован администрацией")
                    continue

                page_2 = soup.find("div", class_="post_top").find("div", class_="post_content").find_all("div",
                                                                                                         class_="image")

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

                    page_3 = pars_param_src(page_2[i])
                    page_4 = pars_param_href(page_2[i])
                    print("src = ", page_3)
                    print("href = ", page_4)
                    i += 1

                    if page_3 != 0 and page_4 != 0 and page_4 != "javascript:":
                        print('1111')
                        list_href.append('https:' + page_4)

                    elif page_3 != 0 and page_4 == 0:
                        list_src.append('https:' + page_3)

                    elif (page_3 != 0 and page_4 != 0 and page_4 == "javascript:"):
                        list_src.append('https:' + page_3)

                # print(list_href)
                # print(list_src)

                try:

                    if len(list_href) == 0:
                        print("список list_href пуст")

                    elif len(
                            list_href) > 10:  # данный блок собирает специальный список "r" по объёму подходящий для метода InputMediaPhoto и отправляет в чат
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

                    elif len(
                            list_src) > 10:  # данный блок собирает специальный список "r" по объёму подходящий для метода InputMediaPhoto и отправляет в чат
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

                    else:  # если list_src меньше 10, то выполняется эта часть блока - без танцев с бубном
                        r = list()
                        for item in list_src:
                            r.append(types.InputMediaPhoto(item))

                        bot.send_media_group(message.chat.id, r)

                except Exception as _ex:
                    print("не прочиталось!")

            list_exit.clear()  # чистим список после выгрузки постов
        time.sleep(10)
