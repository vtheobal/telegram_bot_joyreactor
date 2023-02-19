import json

def json_now_post(URL, post, user_id):
    with open('json_folder/'+user_id+'.json', 'r') as file:
        meta = json.load(file)
    file.close()

    meta[URL] = post

    with open('json_folder/'+user_id+'.json', 'w') as file:
        json.dump(meta, file, indent=4)
    file.close()


def json_remove_avtor(URL, user_id):
    with open('json_folder/'+user_id+'.json', 'r') as file:
        meta = json.load(file)
    file.close()

    del meta[URL]

    with open('json_folder/'+user_id+'.json', 'w') as file:
        json.dump(meta, file, indent=4)
    file.close()


def chek_list_key_json(URL, user_id):
    with open('json_folder/'+user_id+'.json', 'r') as file:      # открываем файл на чтение и достаём значение json файла
        meta = json.load(file)
    file.close()

    meta_list = list(meta.keys())               # храним список всех ключей из json файла 

    for item in meta_list:
        if item == URL:
            return 1
    
    return 0
        