import time
import requests
from bs4 import BeautifulSoup as b
import json
import threading
import telebot
import random
from telebot import types

API_KEY = '6027340474:AAG4dJ79uYBwtXHGdmKlSSKLAYC8p1Qe9oo'
bot = telebot.TeleBot(API_KEY)
timer = 10
