import time
import requests
from bs4 import BeautifulSoup as b
import json
import threading
import telebot
import random
from telebot import types
import os.path
import cfscrape

API_KEY = '6027340474:AAG4dJ79uYBwtXHGdmKlSSKLAYC8p1Qe9oo'  # основной ключ
# API_KEY = '5776307867:AAHKJoOA-J8wYFetuLwX9vWsc9mIjl8hPkE'  # тестовый ключ
bot = telebot.TeleBot(API_KEY)

# таймер задержки для потока (hello.py), что парcит авторов/теги из библиотеки
timer = 900
