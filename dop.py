from bs4 import BeautifulSoup as b
import json
import requests

def pars_new_post(URL, user_id):

    # парснг часть, которая пробегается по всем постам (на выходе есть список)
    r = requests.get(URL)
    # print(r.status_code)     # статус обработки (200) - всё заебок, сайт читается

    soup = b(r.text, 'html.parser')


    page_2 = soup.find_all("a", class_="link")
    # for g in page_2:    #показыват все списки class_="link"
    #     print(g)

    list =[]                                        # данный блок собирает ссылки на посты для команды /go по url указанным в json
    for item in page_2:
        item_url = item.get("href")
        list.append(item_url)

    # print(list)        # показывает список всех постов на странице


    # открытие файла в переменную мета и его вывод
    with open(user_id+'.json', 'r') as file:  
        meta = json.load(file)
    file.close()

    # print(meta)

    # в переменную закидываем значение последнего поста
    last_post = meta[URL]
    # print(last_post)


    # проверка всех постов на странице на соответствие посту из json (если находит совпадение с постом из json - завершает цыкл)
    list_exit =[]  #создание списка для выгрузки всех постов до последнего из ссылок в json
    for item in page_2:
        item_url = item.get("href")
        if (item_url != last_post):
            list_exit.append(item_url)
            print(item_url)
        if (item_url == last_post):
            print("good job")
            break


    # в словаре, выгруженном из json меням у конкретного ключа значение на первый пост
    meta[URL] = list[0]
    print(meta)

    # переписываем последний пост в json файле
    with open(user_id+'.json', 'w') as file:  
        json.dump(meta, file, indent=4)
    file.close()
    return (list_exit)



def pars_one_post(message_to_save):
    r = requests.get(message_to_save)       # модуль парсера для поиска отдного первого поста 
    
    if(r.status_code == 200):

    # print(r.status_code)     # статус обработки (200) - всё заебок, сайт читается
        soup = b(r.text, 'html.parser')

        page_2 = soup.find("a", class_="link")
        item_url = page_2.get("href")
        print (item_url)
        return (item_url)

    else:
        return ("404")




def separator_name(URL):
        buf = URL.split("/")
        # print(len(buf))
        if (len(buf) > 3):
            # print(buf[4])
            return (buf[4])
        else:
            # print(buf[2]) 
            return (buf[2])


def valid_page_2(soup):         # блок для проверки сайта на наличие контейнера (тегов) с контентом в посте

    try:
        page_2 = soup.find("div", class_="post_top").find("div", class_="post_content").find_all("div", class_="image")
        return (1)

    except Exception as _ex:
        return (0)


def valid_page_2_video(soup):
    try:
        page_2 = soup.find_all("iframe", class_="youtube-player")
        return (1)

    except Exception as _ex:
        return (0)

def valid_page_2_gif(soup):
    try:
        page_2 = soup.find_all("a", class_="video_gif_source")
        if (len(page_2) > 0):
            return (1)
        else:
            return (0)

    except Exception as _ex:
        return (0)