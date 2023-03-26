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
            list_exit = pars_new_post(URL, str(message.from_user.id), message)  # пишем в переменную list_exit наш список постов, которые надо выгрузить (значение приходит из парсера функции pars_new_post)
            if list_exit == 0:
                continue

            if list_exit:
                bot.send_message(message.chat.id, URL)
            for item in list_exit:

                try:
                    session = get_session()
                    r = session.get("https://joyreactor.cc" + item)
                    if r.status_code != 200:
                        print(f"ошибка парсера requests - r.status_code != 200", r.status_code)
                        continue
                except requests.exceptions.RequestException:
                    print(f"глобальная ошибка requests", message.from_user.id)
                    time.sleep(120)
                    continue

                soup = b(r.text, 'html.parser')

                if valid_link_and_video_link(soup=soup, message_text=item, message=message) == 0:
                    continue

                page_2 = soup.find("div", class_="post_top").find("div", class_="post_content").find_all("div",
                                                                                                         class_="image")
                sort_content(page_2, message)

            list_exit.clear()  # чистим список после выгрузки постов
        time.sleep(timer)
