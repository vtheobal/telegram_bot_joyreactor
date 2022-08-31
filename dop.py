from bs4 import BeautifulSoup as b
import json
import requests

def pars_new_post(URL):

    # парснг часть, которая пробегается по всем постам (на выходе есть список,  но чуть ниже не могу его обработать в for цикле)
    r = requests.get(URL)
    # print(r.status_code)     # статус обработки (200) - всё заебок, сайт читается

    soup = b(r.text, 'html.parser')


    page_2 = soup.find_all("a", class_="link")
    # for g in page_2:    #показыват все списки class_="link"
    #     print(g)

    list =[]
    for item in page_2:
        item_url = item.get("href")
        list.append(item_url)

    # print(list)        # показывает список всех постов на странице


    # открытие файла в переменную мета и его вывод
    with open('spisok.json', 'r') as file:  
        meta = json.load(file)
    file.close()

    # print(meta)

    # в переменную закидываем значение последнего поста
    last_post = meta[URL]
    # print(last_post)


    # проверка всех постов на странице на соответствие посту из json (если находит совпадение с постом из json - завершает цыкл)
    list_exit =[]  #создание списка для выгрузки всех постов до последнего из json
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
    with open('spisok.json', 'w') as file:  
        json.dump(meta, file, indent=4)
    file.close()
    return (list_exit)


def pars_one_post(message_to_save):
    r = requests.get(message_to_save)       # модуль парсера для поиска отдного первого поста 
    soup = b(r.text, 'html.parser')

    page_2 = soup.find("a", class_="link")
    item_url = page_2.get("href")
    print (item_url)
    return (item_url)