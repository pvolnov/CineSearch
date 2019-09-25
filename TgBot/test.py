import random
import time
from datetime import datetime

# import telebot

# from config import TELEGRAM_TOKEN
# from models import Films, Users, Selections, Config

# bot = telebot.TeleBot(TELEGRAM_TOKEN)
# from models import Config
# from models import Messages
from models import Films, Users, Config

# Films.update({Films.shit:0,Films.errors:0}).execute()
# Config.create(name="TELEGRAM_TOKEN",value="975424883:AAGrrjwk-rD_tacFlZH4H2cojDpS5hTT5no")
# Config.create(name="ALAMER_KEY",value="df548f-61ac83-624ea4")
# Config.create(name="WEIGHT_COS",value=10)
# Config.create(name="GANRES",json=['Боевик', 'Комедия', 'Детектив', 'Ужасы', 'Триллер', 'Драма', 'Исторический', 'Военный', 'Криминал', 'Приключения', 'Фэнтези', 'Фантастика', 'Вестерн', 'Мелодрама', 'Мультфильм', 'Биография', 'Семейный', 'Музыка', 'Документальный', 'Мюзикл', 'Мистика', 'Психологический', 'Спорт', 'Романтический', 'Детский', 'Разное'],value="json")

Users.update({Users.mark_wight:1}).execute()