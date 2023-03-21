from config import *

def pars_new_post(URL, user_id):

    # парснг часть, которая пробегается по всем постам (на выходе есть список,  но чуть ниже не могу его обработать в for цикле)
    try:
        session = get_session()
        r = session.get(URL)
        print("try")
        if r.status_code != 200:    # статус обработки (200) - всё заебок, сайт читается
            print(f"ошибка парсера requests - r.status_code != 200", r.status_code)
            return 0
    except requests.exceptions.RequestException:
        print("глобальная ошибка requests")
        time.sleep(120)
        return 0

    # r = requests.get(URL)
    # print(r.status_code)     # статус обработки (200) - всё заебок, сайт читается

    soup = b(r.text, 'html.parser')

    page_2 = soup.find_all("a", class_="link")
    # for g in page_2:    #показыват все списки class_="link"
    #     print(g)

    list = []
    for item in page_2:
        item_url = item.get("href")
        list.append(item_url)
    # print(list)        # показывает список всех постов на странице

    # открытие файла в переменную мета и его вывод
    with open('json_folder/'+user_id+'.json', 'r') as file:
        meta = json.load(file)
    file.close()

    # в переменную закидываем значение последнего поста
    last_post = meta[URL]

    # проверка всех постов на странице на соответствие посту из json (если находит совпадение с постом из json - завершает цыкл)
    list_exit = []  #создание списка для выгрузки всех постов до последнего из ссылок в json
    for item in page_2:
        item_url = item.get("href")
        if item_url != last_post:
            list_exit.append(item_url)
            print(item_url)
        if item_url == last_post:
            # print("good job")
            break


    # в словаре, выгруженном из json меням у конкретного ключа значение на первый пост
    meta[URL] = list[0]

    # переписываем последний пост в json файле
    with open('json_folder/'+user_id+'.json', 'w') as file:
        json.dump(meta, file, indent=4)
    file.close()
    return list_exit


def pars_one_post(r):
    # r = requests.get(message_to_save)       # модуль парсера для поиска отдного первого поста
    
    if r.status_code == 200:
    # print(r.status_code)     # статус обработки (200) - всё заебок, сайт читается
        soup = b(r.text, 'html.parser')

        page_2 = soup.find("a", class_="link")
        item_url = page_2.get("href")
        print(item_url)
        return item_url
    else:
        return "404"


def valid_page_2(soup):         # блок для проверки сайта на наличие контейнера (тегов) с контентом в посте
    try:
        page_2 = soup.find("div", class_="post_top").find("div", class_="post_content").find_all("div", class_="image")
        return 1

    except Exception as _ex:
        return 0


def valid_page_2_video(soup):
    try:
        page_2 = soup.find_all("iframe", class_="youtube-player")
        return 1

    except Exception as _ex:
        return 0


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

def push_telegramm(list_href, list_src, message):
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

        else:  # если list_href меньше 10, то выполняется эта чаcть блока - без танцев с бубном
            r = list()
            for item in list_href:
                r.append(types.InputMediaDocument(item))

            bot.send_media_group(message.chat.id, r)

        if len(list_src) == 0:
            print("список list_src пуст")

        elif len(list_src) > 10:  # собирает список ссылок "r" по объёму подходящий для метода InputMediaPhoto и отправляет в чат
            i = 1
            r = list()
            r.append(types.InputMediaDocument(list_src[0]))
            while i < len(list_src):
                r.append(types.InputMediaDocument(list_src[i]))
                # print(i)
                print(types.InputMediaDocument(list_src[i]))
                if (i % 9) == 0:
                    bot.send_media_group(message.chat.id, r)
                    r = []
                    print('девяточка')
                i += 1

            bot.send_media_group(message.chat.id, r)

        else:  # если list_src меньше 10, то выполняется эта сборка ссылок - без танцев с бубном
            r = list()
            for item in list_src:
                r.append(types.InputMediaDocument(item))

            bot.send_media_group(message.chat.id, r)

    except Exception as _ex:
        print("не прочиталось!")

def get_session():
    session = requests.Session()
    session.headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0)   Gecko/20100101 Firefox/69.0',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language':'ru,en-US;q=0.5',
        'Accept-Encoding':'gzip, deflate, br',
        'DNT':'1',
        'Connection':'keep-alive',
        'Upgrade-Insecure-Requests':'1',
        'Pragma':'no-cache',
        'Cache-Control':'no-cache'}
    return cfscrape.create_scraper(sess=session)

def cort_content(page_2, message):
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
            print('Метод сортировки 1')
            list_href.append('https:' + object_href)

        elif object_src != 0 and object_href == 0:
            print('Метод сортировки 2')
            list_src.append('https:' + object_src)

        elif object_src != 0 and object_href != 0 and object_href == "javascript:":
            print('Метод сортировки 3')
            list_src.append('https:' + object_src)

    print('list_href = ', list_href)
    print('list_src = ', list_src)

    push_telegramm(list_href, list_src, message)