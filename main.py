from dop import *
from work_with_json import *
from hello import *
from config import *


@bot.message_handler(commands=['go'])
def test(message):

    if os.path.isfile('json_folder/' + str(message.chat.id) + '.json'):
        with open('json_folder/user_id.json', 'r') as file:
            meta = json.load(file)
        file.close()
        print(meta)

        if meta[str(message.chat.id)] == 0:
            globals()[message.from_user.id] = threading.Thread(target=hello, args=(message,), name=message.from_user.id)
            globals()[message.from_user.id].start()
            meta[str(message.chat.id)] = 1
            with open('json_folder/user_id.json', 'w') as file:
                json.dump(meta, file, indent=4)
            file.close()
            bot.send_message(message.chat.id, "Включаю поток")
        else:
            print(f"поток {message.from_user.id} запущен")
            bot.send_message(message.chat.id, "Поток уже запущен!")

    else:
        print("json файл пользователя не найден")


@bot.message_handler(commands=['add'])  # команда берёт текст, который мы отправляем после команды '/add'
def add(message):
    sent = bot.reply_to(message, 'пришли ссылку тега/автора, которого хочешь отслеживать')
    bot.register_next_step_handler(sent, review)


def review(message):  # сей конструкцией мы получаем текст из telegram, в нашем случае URL на автора
    message_to_save_add = message.text
    print(message_to_save_add)

    if (
            message_to_save_add == "https://joyreactor.cc/tag/" or message_to_save_add == "https://joyreactor.cc/user/"):  # исключение для пустого тега
        bot.send_message(message.chat.id, "Передан не верный URL. URL имеет тип https://joyreactor.cc/tag/..." +
                                                                                " или https://joyreactor.cc/user/... ")
        return 0

    elif message_to_save_add.find("/post/") != -1:
        bot.send_message(message.chat.id, "вы передали пост, а не тег или автора")
        return 0

    elif (message_to_save_add.find(
            "reactor.cc/") != -1):  # Ищем подстроку в строке и возвращаем индекс первого вхождения. для нас достаточно определить что эта подстрока в принципе есть

        try:
            session = get_session()
            r = session.get(message_to_save_add)
            if r.status_code != 200:  # статус обработки (200) - всё заебок, сайт читается
                print(f"ошибка парсера requests - r.status_code != 200", r.status_code)
                return
        except requests.exceptions.RequestException:
            print("глобальная ошибка requests")
            time.sleep(120)
            return

        one_post = pars_one_post(r)  # модуль парсера для поиска одного первого поста
        if one_post == "404":
            bot.send_message(message.chat.id, "такого автора/тега не существует")
            return 0

        if (chek_list_key_json(message_to_save_add,
                               str(message.from_user.id)) == 1):  # проверяет есть ли поданный телегой автор в СПИСКЕ авторов json
            bot.send_message(message.chat.id, "такой автор уже есть в списке")
            return 0

        json_now_post(message_to_save_add, one_post,
                      str(message.from_user.id))  # модуль, добавляющий в json нового автора (в качестве аргумента передаётся URL и первый пост автора)
        bot.send_message(message.chat.id, "автор/тег добавлен")

    else:  # в случае если URL пришёл биты - выводим ошибку - выходим
        bot.send_message(message.chat.id, "Передан не верный URL. URL имеет тип https://joyreactor.cc/tag/..." +
                         " или https://joyreactor.cc/user/... ")
        return 0


@bot.message_handler(commands=['remove'])  # команда берёт текст, который мы отправляем после команды '/remove'
def remove(message):
    sent = bot.reply_to(message, 'какой тег/автора надо удалить?')
    bot.register_next_step_handler(sent, review1)


def review1(message):  # сей конструкцией мы получаем текст из telegram, в нашем случае URL на автора
    message_to_save_remove = message.text
    print(message_to_save_remove)

    if (
            message_to_save_remove == "https://joyreactor.cc/tag/" or message_to_save_remove == "https://joyreactor.cc/user/"):
        bot.send_message(message.chat.id, "Передан не верный URL. URL имеет тип https://joyreactor.cc/tag/..." +
                         " или https://joyreactor.cc/user/... ")
        return 0

    elif message_to_save_remove.find("/post/") != -1:
        bot.send_message(message.chat.id, "вы передали пост, а не тег или автора")
        return 0

    elif (message_to_save_remove.find(
            "reactor.cc/tag/") != -1):  # Ищем подстроку в строке и возвращаем индекс первого вхождения. Достаточно определить что эта подстрока в принципе есть

        if (chek_list_key_json(message_to_save_remove,
                               str(message.from_user.id)) == 0):  # проверяет есть ли поданный телегой автор в СПИСКЕ авторов json
            bot.send_message(message.chat.id, "такого автора нет в списке")
            return 0

        json_remove_avtor(message_to_save_remove,
                          str(message.from_user.id))  # модуль, удаляющий в json автора (в качестве аргумента передаётся URL)
        bot.send_message(message.chat.id, "тег/автор удалён из списка")

    else:
        bot.send_message(message.chat.id, "Передан не верный URL. URL имеет тип https://joyreactor.cc/tag/..." +
                         " или https://joyreactor.cc/user/... ")
        return 0


@bot.message_handler(commands=['list'])
def list_chek(message):
    with open('json_folder/'+str(message.from_user.id) + '.json',
              'r') as file:  # открываем файл на чтение и достаём значение json файла
        meta = json.load(file)
    file.close()

    if len(meta) == 0:  # Проверка списка на пустоту. Если пустой - завершает команду
        bot.send_message(message.chat.id, "Ваш список пуст")
        return 0

    list_chek = list(meta.keys())  # делаем из словаря список с ключами, в нашем случае это URL ссылки
    print('\n'.join(list_chek))
    bot.send_message(message.chat.id, '\n'.join(list_chek))


@bot.message_handler(commands=['one_post'])
def one_post(message):
    buf = bot.reply_to(message, 'пришли ссылку на пост, чтобы увидеть его контент')
    bot.register_next_step_handler(buf, pull)


def pull(message):  # сей конструкцией мы получаем текст из telegram, в нашем случае URL на автора
    message_to_save_pul = message.text
    print(message_to_save_pul)

    if (message_to_save_pul.find(
            "reactor.cc/post/") == -1):  # защита входящих ссылок на соответствие шаблону ниже, если не соответствует, то выдаёт ошибку
        bot.send_message(message.chat.id, "Передан не верный URL. URL имеет тип https://joyreactor.cc/post/...")
        return 0

    try:
        session = get_session()
        r = session.get(message_to_save_pul)
        if r.status_code != 200:
            print(f"ошибка парсера requests - r.status_code != 200", r.status_code)
            return
    except requests.exceptions.RequestException:
        print("глобальная ошибка requests")
        time.sleep(120)
        return

    one_post = pars_one_post(r)  # защита от битых ссылок модуль для поиска одного первого поста
    if one_post == "404":
        bot.send_message(message.chat.id, "такого поста не существует")
        return 0

    soup = b(r.text, 'html.parser')

    if valid_link_and_video_link(soup=soup, message_text=message_to_save_pul, message=message) == 0:
        return

    page_2 = soup.find("div", class_="post_top").find("div", class_="post_content").find_all("div", class_="image")

    sort_content(page_2, message)


@bot.message_handler(commands=['random_post'])
def random_post(message):
    buf = bot.reply_to(message, 'пришли ссылку автора чтобы увидеть рандомный пост')
    bot.register_next_step_handler(buf, random_post_next)


def random_post_next(message):  # сей конструкцией мы получаем текст из telegram, в нашем случае URL на автора
    message_to_save_pul = message.text
    print(message_to_save_pul)

    if (message_to_save_pul.find("reactor.cc/tag/") == -1) and (message_to_save_pul.find("reactor.cc/user/") == -1):  # защита входящих ссылок на соответствие шаблону ниже, если не соответствует, то выдаёт ошибку
        bot.send_message(message.chat.id, "Передан не верный URL. URL имеет тип https://joyreactor.cc/tag/..." +
                                                                                " или https://joyreactor.cc/user/... ")
        return 0

    try:
        session = get_session()
        r = session.get(message_to_save_pul)
        if r.status_code != 200:
            print(f"ошибка парсера requests - r.status_code != 200", r.status_code)
            return
    except requests.exceptions.RequestException:
        print("глобальная ошибка requests")
        time.sleep(120)
        return

    one_post = pars_one_post(r)  # защита от битых ссылок модуль для поиска одного первого поста
    if one_post == "404":
        bot.send_message(message.chat.id, "такого поста не существует")
        return 0

    soup = b(r.text, 'html.parser')
    page_5 = soup.find("div", class_="pagination_expanded").find("span", class_="current")

    max_tabs = int(page_5.text)
    print("max количество вкладок: ", max_tabs)

    random_tabs = random.randint(1, int(max_tabs))
    random_tabs_utter = message_to_save_pul + "/" + str(random_tabs)
    print(random_tabs_utter)

    try:
        session = get_session()
        r = session.get(random_tabs_utter)
        if r.status_code != 200:    # статус обработки (200) - всё заебок, сайт читается
            print(f"ошибка парсера requests - r.status_code != 200", r.status_code)
            return
    except requests.exceptions.RequestException:
        print("глобальная ошибка requests")
        time.sleep(120)
        return

    soup = b(r.text, 'html.parser')
    page_2 = soup.find_all("a", class_="link")

    list_post = []
    for item in page_2:
        item_url = item.get("href")
        list_post.append(item_url)
    print(list_post)

    list_post_random = random.choice(list_post)
    print("https://joyreactor.cc" + list_post_random)

    try:
        session = get_session()
        r = session.get("https://joyreactor.cc" + list_post_random)
        if r.status_code != 200:
            print(f"ошибка парсера requests - r.status_code != 200", r.status_code)
            return
    except requests.exceptions.RequestException:
        print("глобальная ошибка requests")
        time.sleep(120)
        return

    soup = b(r.text, 'html.parser')

    if valid_link_and_video_link(soup=soup, message_text=message_to_save_pul, message=message) == 0:
        return

    # собирает весь контент в посте и сортирует на обработку
    page_2 = soup.find("div", class_="post_top").find("div", class_="post_content").find_all("div", class_="image")

    sort_content(page_2, message)


@bot.message_handler(commands=['random_post_10'])
def random_post(message):
    buf = bot.reply_to(message, 'пришли ссылку автора чтобы увидеть 10 рандомных пост')
    bot.register_next_step_handler(buf, random_post_next_10)


def random_post_next_10(message):  # сей конструкцией мы получаем текст из telegram, в нашем случае URL на автора
    message_to_save_pul = message.text
    print(message_to_save_pul)

    if (message_to_save_pul.find("reactor.cc/tag/") == -1) and (message_to_save_pul.find("reactor.cc/user/") == -1):  # защита входящих ссылок на соответствие шаблону ниже, если не соответствует, то выдаёт ошибку
        bot.send_message(message.chat.id, "Передан не верный URL. URL имеет тип https://joyreactor.cc/tag/..." +
                                                                                " или https://joyreactor.cc/user/... ")
        return 0

    try:
        session = get_session()
        r = session.get(message_to_save_pul)
        if r.status_code != 200:    # статус обработки (200) - всё заебок, сайт читается
            print(f"ошибка парсера requests - r.status_code != 200", r.status_code)
            return
    except requests.exceptions.RequestException:
        print("глобальная ошибка requests")
        time.sleep(120)
        return

    one_post = pars_one_post(r)  # защита от битых ссылок модуль для поиска одного первого поста
    if one_post == "404":
        bot.send_message(message.chat.id, "такого поста не существует")
        return 0
    soup = b(r.text, 'html.parser')

    # ищет максимальное количество вкладок автора
    page_5 = soup.find("div", class_="pagination_expanded").find("span", class_="current")

    max_tabs = int(page_5.text)
    print("max количество вкладок: ", max_tabs)

    for _ in range(10):

        # берём случайный номер страницы с постами
        random_tabs = random.randint(1, int(max_tabs))
        random_tabs_utter = message_to_save_pul + "/" + str(random_tabs)
        print(random_tabs_utter)

        try:
            session = get_session()
            r = session.get(random_tabs_utter)
            if r.status_code != 200:  # статус обработки (200) - всё заебок, сайт читается
                print(f"ошибка парсера requests - r.status_code != 200", r.status_code)
                return
        except requests.exceptions.RequestException:
            print("глобальная ошибка requests")
            time.sleep(120)
            return

        # собирает все ссылки на посты в приделах одной странице
        soup = b(r.text, 'html.parser')
        page_2 = soup.find_all("a", class_="link")

        list_post = []
        for item in page_2:
            item_url = item.get("href")
            list_post.append(item_url)
        print(list_post)

        list_post_random = random.choice(list_post)

        print("https://joyreactor.cc" + list_post_random)

        try:
            session = get_session()
            r = session.get("https://joyreactor.cc" + list_post_random)
            if r.status_code != 200:  # статус обработки (200) - всё заебок, сайт читается
                print(f"ошибка парсера requests - r.status_code != 200", r.status_code)
                return
        except requests.exceptions.RequestException:
            print("глобальная ошибка requests")
            time.sleep(120)
            return

        soup = b(r.text, 'html.parser')

        if valid_link_and_video_link(soup=soup, message_text=message_to_save_pul, message=message) == 0:
            continue

        # собирает весь контент в посте и отправляем на сортировку
        page_2 = soup.find("div", class_="post_top").find("div", class_="post_content").find_all("div", class_="image")

        sort_content(page_2, message)


@bot.message_handler(commands=['start'])
def start_bot(message):
    list1 = {}
    print(type(list1))
    with open('json_folder/'+str(message.from_user.id)+'.json', 'w') as file:
        json.dump(list1, file, indent=4)
        print("создан json файле пользователя")
    file.close()

    if os.path.isfile('json_folder/' + str(message.chat.id) + '.json'):
        with open('json_folder/user_id.json', 'r') as file:
            meta = json.load(file)
        file.close()
        print(meta)

        if meta.get(str(message.chat.id)):
            print("ключ в виде id есть в списке")
        else:
            globals()[message.from_user.id] = threading.Thread(target=hello, args=(message,), name=message.from_user.id)
            globals()[message.from_user.id].start()
            meta[str(message.chat.id)] = 1
            with open('json_folder/user_id.json', 'w') as file:
                json.dump(meta, file, indent=4)
            file.close()
            bot.send_message(message.chat.id, "Включаю поток")
    else:
        print("json файл пользователя не найден")


@bot.message_handler(commands=['help'])  # конструкция для кнопок
def knopka(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    add = types.KeyboardButton('/add')  # добавляет кнопку с командой ('/add')
    remove = types.KeyboardButton('/remove')  # добавляет кнопку с командой ('/remove')
    go = types.KeyboardButton('/go')  # добавляет кнопку с командой ('/go')
    list = types.KeyboardButton('/list')  # добавляет кнопку с командой ('/list')
    one_post = types.KeyboardButton('/one_post')
    random_post = types.KeyboardButton('/random_post')
    random_post_10 = types.KeyboardButton('/random_post_10')
    markup.add(add, remove, go, list, one_post, random_post, random_post_10)  # в толбар добавляет объектами кнопок
    bot.send_message(message.chat.id, "help - разворот кнопок", reply_markup=markup)


@bot.message_handler()  # обработчик случайных команд
def error(message):
    bot.send_message(message.chat.id, "введите /help чтобы увидеть список команд")


if __name__ == '__main__':
    with open('json_folder/user_id.json', 'r') as file:
        meta = json.load(file)
    file.close()

    for _ in meta:
        gg = 'https://api.telegram.org/bot' + API_KEY + '/sendMessage?chat_id='+_+'&text=На боте проводились технические работы. Для возобновления работы нажмите /go'
        requests.get(gg)
        meta[_] = 0

    with open('json_folder/user_id.json', 'w') as file:
        json.dump(meta, file, indent=4)
    file.close()

bot.polling()
