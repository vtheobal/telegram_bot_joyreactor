import time
import requests
from bs4 import BeautifulSoup as b
import json
import threading
import telebot
import random
from telebot import types
import os.path

API_KEY = '5776307867:AAHKJoOA-J8wYFetuLwX9vWsc9mIjl8hPkE'
bot = telebot.TeleBot(API_KEY)

# таймер задержки для потока (hello.py), что парcит авторов/теги из библиотеки
timer = 10
