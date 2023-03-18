import time

from dop import *
from work_with_json import *
from config import *


def hello(message):
    while True:
        print(message.from_user.id, "начало цикла")
        with open('json_folder/'+str(message.from_user.id) + '.json',
                  'r') as file:  # открываем файл на чтение и достаём значение json файла
            meta = json.load(file)
        file.close()

        meta_list = list(meta.keys())  # делаем из словаря список с ключами, в нашем случае это URL ссылки

        for URL in meta_list:
            list_exit = pars_new_post(URL, str(message.from_user.id))  # пишем в переменную list_exit наш список постов, которые надо выгрузить (значение приходит из парсера функции pars_new_post)
            if list_exit:
                bot.send_message(message.chat.id, URL)
            for item in list_exit:

                try:
                    r = requests.get("https://joyreactor.cc" + item)
                    if r.status_code != 200:  # статус обработки (200) - всё заебок, сайт читается
                        print(f"ошибка парсера requests - r.status_code != 200", r.status_code)
                        continue
                except requests.exceptions.RequestException:
                    print("глобальная ошибка requests")
                    time.sleep(120)
                    continue

                soup = b(r.text, 'html.parser')

                if valid_page_2_video(
                        soup) == 1:  # обращение к функции из файла dop - функция чекает строчку ниже на читаемость и оборачивыает в try except - смотрит есть ли в блоке с медиа файлы на ютуб если есть, то выгружает только ссылки на ютуб, игнарируя весь остальной контент в посте
                    print("youtube-link")
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
                        print('Метод сортировки 1')
                        list_href.append('https:' + page_4)

                    elif page_3 != 0 and page_4 == 0:
                        print('Метод сортировки 2')
                        list_src.append('https:' + page_3)

                    elif page_3 != 0 and page_4 != 0 and page_4 == "javascript:":
                        print('Метод сортировки 3')
                        list_src.append('https:' + page_3)

                # print(list_href)
                # print(list_src)

                push_telegramm(list_href, list_src, message)

            list_exit.clear()  # чистим список после выгрузки постов
        time.sleep(timer)
