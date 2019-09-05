import telebot

from config import TELEGRAM_TOKEN
from models import Films, Users, Selections

bot = telebot.TeleBot(TELEGRAM_TOKEN)

Selections.create(name=str("test"), user_id=445330281)

Selections.select().execute()

