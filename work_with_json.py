import json

def json_now_post(URL, post):
    with open('spisok.json', 'r') as file: 
        meta = json.load(file)
    file.close()

    meta[URL] = post

    with open('spisok.json', 'w') as file:
        json.dump(meta, file, indent=4)
    file.close()


def json_remove_avtor(URL):
    with open('spisok.json', 'r') as file: 
        meta = json.load(file)
    file.close()

    del meta[URL]

    with open('spisok.json', 'w') as file:
        json.dump(meta, file, indent=4)
    file.close()