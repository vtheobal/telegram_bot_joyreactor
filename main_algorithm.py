from dop import *
from telebot import types
import telebot

API_KEY = '5324085182:AAGOgFlXmC691d9ItR2vhy28l2nhaYYDJ48'
bot = telebot.TeleBot(API_KEY)


def main_algorithm(soup, message):

    page_2 = soup.find("div", class_="post_top").find("div", class_="post_content").find_all("div", class_="image")

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

        if (object_src != 0 and object_href != 0 and object_href != "javascript:"):
            print('-1-')
            list_href.append('https:' + object_href)

        elif (object_src != 0 and object_href == 0):
            print('-2-')
            list_src.append('https:' + object_src)

        elif (object_src != 0 and object_href != 0 and object_href == "javascript:"):
            print('-3-')
            list_src.append('https:' + object_src)

    print(list_href)
    print(list_src)

    if (len(list_href) == 0):
        print("список list_href пуст")

    elif (len(list_href) > 10):  # данный блок собирает специальный список "r" по объёму подходящий для метода InputMediaPhoto и отправляет в чат
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

    if (len(list_src) == 0):
        print("список list_src пуст")

    elif (len(list_src) > 10):  # данный блок собирает специальный список "r" по объёму подходящий для метода InputMediaPhoto и отправляет в чат
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

