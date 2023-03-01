from dop import *
from work_with_json import *
from hello import *
from config import *

# API_KEY = '6027340474:AAG4dJ79uYBwtXHGdmKlSSKLAYC8p1Qe9oo'
# bot = telebot.TeleBot(API_KEY)


# Основная функция. Парсит значения из json и выдаёт посты

@bot.message_handler(commands=['go'])
def test(message):
    thr = threading.Thread(target=hello, args=(message,), name="osnova")
    thr.start()


@bot.message_handler(commands=['add'])  # команда берёт текст, который мы отправляем после команды '/add'
def add(message):
    sent = bot.reply_to(message, 'пришлите мне нового автора')
    bot.register_next_step_handler(sent, review)


def review(message):  # сей конструкцией мы получаем текст из telegramm, в нашем случае URL на автора
    message_to_save_add = message.text
    print(message_to_save_add)

    if (
            message_to_save_add == "https://joyreactor.cc/tag/" or message_to_save_add == "https://joyreactor.cc/user/"):  # исключение для пустого тега
        bot.send_message(message.chat.id, "Передан не верный URL. URL имеет тип https://joyreactor.cc/tag/ник_автора")
        return 0

    elif message_to_save_add.find("/post/") != -1:
        bot.send_message(message.chat.id, "вы передали пост, а не тег или автора")
        return 0

    elif (message_to_save_add.find(
            "reactor.cc/") != -1):  # ищем подстроку в строке и возвращаем индекс первого вхождения. для нас достаточно определить что эта подстрока впринципе есть

        one_post = pars_one_post(message_to_save_add)  # модуль парсера для поиска одного первого поста
        if (one_post == "404"):
            bot.send_message(message.chat.id, "такого автора/тега не существует")
            return 0

        if (chek_list_key_json(message_to_save_add,
                               str(message.from_user.id)) == 1):  # проверяет есть ли поданный телегой автор в СПИСКЕ авторов json
            bot.send_message(message.chat.id, "такой автор уже есть в списке")
            return 0

        json_now_post(message_to_save_add, one_post,
                      str(message.from_user.id))  # модуль, добавляющий в json нового автора (в качестве аргумента передаётся URL и первый пост автора)
        bot.send_message(message.chat.id, "команда add выполнена")

    else:  # в случае если URL пришёл биты - выводим ошибку - выходим
        bot.send_message(message.chat.id, "Передан не верный URL. URL имеет тип https://joyreactor.cc/tag/ник_автора")
        return 0


@bot.message_handler(commands=['remove'])  # команда берёт текст, который мы отправляем после команды '/remove'
def remove(message):
    sent = bot.reply_to(message, 'какого автора надо удалить?')
    bot.register_next_step_handler(sent, review1)


def review1(message):  # сей конструкцией мы получаем текст из telegramm, в нашем случае URL на автора
    message_to_save_remove = message.text
    print(message_to_save_remove)

    if (
            message_to_save_remove == "https://joyreactor.cc/tag/" or message_to_save_remove == "https://joyreactor.cc/user/"):
        bot.send_message(message.chat.id, "Передан не верный URL. URL имеет тип https://joyreactor.cc/tag/ник_автора")
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
        bot.send_message(message.chat.id, "команда remove выполнена")

    else:
        bot.send_message(message.chat.id, "Передан не верный URL. URL имеет тип https://joyreactor.cc/tag/ник_автора")
        return 0


@bot.message_handler(commands=['list'])
def list_chek(message):
    with open('json_folder/'+str(message.from_user.id) + '.json',
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


@bot.message_handler(commands=['one_post'])
def one_post(message):
    buf = bot.reply_to(message, 'в ответ скинь мне ссылку на пост')
    bot.register_next_step_handler(buf, pull)


def pull(message):  # сей конструкцией мы получаем текст из telegramm, в нашем случае URL на автора
    message_to_save_pul = message.text
    print(message_to_save_pul)

    if (message_to_save_pul.find(
            "reactor.cc/post/") == -1):  # защита входящих ссылок на соответствие шаблону ниже, если не соотвектствует, то выдаёт ошибку
        bot.send_message(message.chat.id, "Передан не верный URL. URL имеет тип https://joyreactor.cc/post/...")
        return 0

    one_post = pars_one_post(
        message_to_save_pul)  # защита от битых ссылок модуль для поиска одного первого поста
    if one_post == "404":
        bot.send_message(message.chat.id, "такого поста не существует")
        return 0

    r = requests.get(message_to_save_pul)
    soup = b(r.text, 'html.parser')

    if valid_page_2_video(soup) == 1:  # ссылка на ютуб!  обращение к функции из файла dop - функция чекает строчку ниже на читаемость и оборачивыает в try except
        page_2 = soup.find_all("iframe", class_="youtube-player")
        r = list()

        if len(page_2) != 0:
            for g in page_2:
                r.append(g.get("src"))
            bot.send_message(message.chat.id, '\n'.join(r))
            # return 0

    #     bot.send_message(message.chat.id, '\n'.join(r))

    if valid_page_2(soup) == 0:  # обращение к функции из файла dop - функция чекает строчку ниже на читаемость и оборачивыает в try except
        bot.send_message(message.chat.id,
                         message_to_save_pul + " не удаётся распарсить контейнер с данными. Возможно контент заблокирован администрацией")
        return 0

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


@bot.message_handler(commands=['random_post'])
def random_post(message):
    buf = bot.reply_to(message, 'кинь ссылку автора чтобы я вернул тебе рандомный пост')
    bot.register_next_step_handler(buf, random_post_next)


def random_post_next(message):  # сей конструкцией мы получаем текст из телеграмма, в нашем случае URL на автора
    message_to_save_pul = message.text
    print(message_to_save_pul)

    if (message_to_save_pul.find("reactor.cc/tag/") == -1) and (message_to_save_pul.find("reactor.cc/user/") == -1):  # защита входящих ссылок на соответствие шаблону ниже, если не соотвектствует, то выдаёт ошибку
        bot.send_message(message.chat.id, "Передан не верный URL. URL имеет тип https://joyreactor.cc/tag/..." +
                                                                                " или https://joyreactor.cc/user/... ")
        return 0

    one_post = pars_one_post(message_to_save_pul)  # защита от битых ссылок. модуль для поиска одного первого поста
    if one_post == "404":
        bot.send_message(message.chat.id, "такого поста не существует")
        return 0

    r = requests.get(message_to_save_pul)
    soup = b(r.text, 'html.parser')

    page_5 = soup.find("div", class_="pagination_expanded").find("span", class_="current")

    max_tabs = int(page_5.text)
    print("max количество вкладок: ", max_tabs)

    random_tabs = random.randint(1, int(max_tabs))
    random_tabs_utter = message_to_save_pul + "/" + str(random_tabs)
    print(random_tabs_utter)

    # парсинг часть, которая пробегается по всем постам (на выходе есть список, но чуть ниже не могу его обработать в for цикле)
    r = requests.get(random_tabs_utter)


    soup = b(r.text, 'html.parser')

    page_2 = soup.find_all("a", class_="link")
    # for g in page_2:    #показывает все списки class_="link"
    #     print(g)

    list_post = []
    for item in page_2:
        item_url = item.get("href")
        list_post.append(item_url)
    print(list_post)

    list_post_random = random.choice(list_post)

    print("https://joyreactor.cc" + list_post_random)
    r = requests.get("https://joyreactor.cc" + list_post_random)
    # # print(r.status_code)     # статус обработки (200) - всё работает, сайт читается

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
        bot.send_message(message.chat.id, "https://joyreactor.cc" + item + " не удаётся распарсить контейнер с данными. Возможно контент заблокирован администрацией")
        return 0


    page_2 = soup.find("div", class_="post_top").find("div", class_="post_content").find_all("div", class_="image")


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


@bot.message_handler(commands=['start'])
def start_bot(message):
    list1 = {}
    print(type(list1))
    with open('json_folder/'+str(message.from_user.id)+'.json', 'w') as file:
        json.dump(list1, file, indent=4)
        print("создан json файле пользователя")
    file.close()

    thr = threading.Thread(target=hello, args=(message,), name="osnova")
    thr.start()


@bot.message_handler(commands=['help'])  # конструкция для кнопок
def knopka(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    add = types.KeyboardButton('/add')  # добавляет кнопку с командой ('/add')
    remove = types.KeyboardButton('/remove')  # добавляет кнопку с командой ('/remove')
    go = types.KeyboardButton('/go')  # добавляет кнопку с командой ('/go')
    list = types.KeyboardButton('/list')  # добавляет кнопку с командой ('/list')
    one_post = types.KeyboardButton('/one_post')
    random_post = types.KeyboardButton('/random_post')
    markup.add(add, remove, go, list, one_post, random_post)  # в толбар добавялет объектами кнопок
    bot.send_message(message.chat.id, "help - разворот кнопок", reply_markup=markup)


@bot.message_handler()  # обработчик рандомных команд
def error(message):
    bot.send_message(message.chat.id, "введите /help чтобы увидеть список команд")

bot.polling()
