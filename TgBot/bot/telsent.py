# -*- coding: utf-8 -*-
import json
import re
import sys
from datetime import datetime

import requests
from telebot.types import InputMediaPhoto, InputMediaVideo

from config import TELEGRAM_TOKEN

sys.path.append('../')
sys.path.append('./')

from models import *
import telebot
from telebot import types
from TextConstants import *
from bs4 import BeautifulSoup

import logging

# add filemode="w" to overwrite
logging.basicConfig(filename="sample.log", level=logging.INFO)

# BOT CODE

bot = telebot.TeleBot(TELEGRAM_TOKEN)
base_keyboard_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
base_button_1 = types.KeyboardButton(text=BTN_1_TEXT)
base_button_2 = types.KeyboardButton(text=BTN_2_TEXT)
# base_button_3 = types.KeyboardButton(text=BTN_3_TEXT)
# base_button_4 = types.KeyboardButton(text=BTN_4_TEXT)

base_keyboard_menu.row(base_button_1, base_button_2)
# base_keyboard_menu.row(base_button_3, base_button_4)

base_keyboard_search = types.ReplyKeyboardMarkup(resize_keyboard=True)

base_button_1 = types.KeyboardButton(text=BTN_1_SEARCH)
base_button_2 = types.KeyboardButton(text=BTN_2_SEARCH)
base_button_3 = types.KeyboardButton(text=BTN_3_SEARCH)
# base_button_4 = types.KeyboardButton(text=BTN_4_SEARCH)

base_keyboard_search.row(base_button_1, base_button_2, base_button_3)


# base_keyboard_search.row(base_button_4)


def alarm(text):
    print(text)
    requests.get(f"https://alarmerbot.ru/?key={ALAMER_KEY}&message= " + text)


def send_film(film_id, message_id, edit=0):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []

    film = Films.get(Films.film_id == film_id)

    buttons.append(types.InlineKeyboardButton(text="Подробнее", callback_data="more_" + str(film_id)))
    buttons.append(types.InlineKeyboardButton(text="Трейлер", callback_data="youtube_" + str(film_id)))

    markup.add(*buttons)

    text = "<b>" + film.name + "</b>\n" + " ".join(film.discr.split(" ")[:50]) + "..."
    if edit > 0:
        bot.edit_message_media(InputMediaPhoto(film.img),
                               chat_id=message_id,
                               message_id=edit,
                               reply_markup=markup)
        bot.edit_message_caption(chat_id=message_id,
                                 message_id=edit,
                                 caption=text,
                                 parse_mode="HTML",
                                 reply_markup=markup)

        return (edit)
    else:
        m = bot.send_photo(chat_id=message_id,
                           photo=film.img,
                           parse_mode="HTML",
                           caption=text,
                           reply_markup=markup)

        return m.message_id


def predict_film_list(message_id):
    import numpy as np
    import random

    u = Users.get(Users.tel_id == message_id)
    selections = sorted(u.selections)[-15:] + [random.randint(1, 100) for r in range(3)]

    options = Films.select(Films.film_id, Films.name, Films.selections).where(
        Films.selections.contains(*selections) and Films.film_id.not_in(u.liked)
        and Films.film_id.not_in(u.viewed) and Films.film_id.not_in(u.disliked)).limit(40).execute()

    predict = {}
    for o in options:  # all avilible films
        predict[o.film_id] = 1
        for s in u.selections:  # all users fun categories
            if s in o.selections:  # film is in user`s fun group
                if o.film_id in predict:
                    predict[o.film_id] += u.selections[s]
                else:
                    predict[o.film_id] = u.selections[s]

    pb = np.array(list(predict.values()), dtype='float')
    pb /= pb.sum()
    pred = np.random.choice(list(predict.keys()), p=pb, size=10)
    print("New predict", pred)
    return [p.item() for p in pred]


def next_film(u, message_id, edit=False):
    Send = False
    if len(u.predict_films) > 0:
        if edit:
            u.cfmes = send_film(u.predict_films[0], message_id, u.cfmes)
            if u.ctmes > 0:
                try:
                    bot.delete_message(
                        chat_id=u.tel_id,
                        message_id=u.ctmes
                    )
                except:
                    pass
                u.ctmes = 0
        else:
            u.cfmes = send_film(u.predict_films[0], message_id)

        u.cfid = u.predict_films[0]
        del u.predict_films[0]
    else:
        Send = True

    if len(u.predict_films) < 1:
        u.predict_films = predict_film_list(message_id)
        if Send:
            u.cfmes = send_film(u.predict_films[0], message_id)
            u.cfid = u.predict_films[0]
            del u.predict_films[0]

    return u


# Start Fanction
@bot.message_handler(commands=['start'])
def startf(message):
    u = Users.get_or_none(Users.tel_id == message.chat.id)
    if u == None:
        Users.create(tel_id=message.chat.id, name=str(message.from_user.first_name) + " " + str(
            message.from_user.last_name),
                     nicname=str(message.from_user.username))

        Selections.get_or_create(name=str(message.from_user.username), user_id=message.chat.id)

        bot.send_message(message.chat.id, START_AUTH_TEXT, reply_markup=base_keyboard_menu)

    else:
        bot.send_message(message.chat.id, YOU_THERE_TEXT)


@bot.message_handler(commands=['menu'])
def menu(message):
    bot.send_message(message.chat.id, OPEN_MENU_TEXT, reply_markup=base_keyboard_menu)
    u = Users.get(Users.tel_id == message.chat.id)
    u.cms = 2
    u.save()


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.from_user:
        cal = str(call.data)
        try:
            print(cal)
            if (cal.find("more") >= 0):
                film_id = cal.split("_")[1]
                film = Films.get(Films.film_id == film_id)
                text = "<b>" + film.name + "</b>\n\n" + film.discr + "\n"
                for i in film.info:
                    text += "<b>" + i + "</b>:  " + film.info[i] + "\n"

                markup = types.InlineKeyboardMarkup(row_width=2)
                buttons = []

                buttons.append(types.InlineKeyboardButton(text="Смотреть", url="https://my-hit.org/film/" + film_id))
                buttons.append(types.InlineKeyboardButton(text="Трейлер", callback_data="youtube_" + str(film_id)))

                markup.add(*buttons)

                bot.edit_message_caption(chat_id=call.message.chat.id,
                                         message_id=call.message.message_id,
                                         parse_mode="HTML",
                                         reply_markup=markup,
                                         caption=text)

            if cal.find("film") >= 0:
                film_id = cal.split("_")[1]
                u = Users.get(Users.tel_id==call.message.chat.id)
                markup = types.InlineKeyboardMarkup(row_width=2)
                buttons = []

                film = Films.get(Films.film_id == film_id)
                buttons.append(types.InlineKeyboardButton(text="Подробнее", callback_data="more_" + str(film_id)))
                buttons.append(types.InlineKeyboardButton(text="Трейлер", callback_data="youtube_" + str(film_id)))

                if int(film_id) in u.liked:
                    buttons.append(types.InlineKeyboardButton(text="🗑", callback_data="drop_" + str(film_id)))
                    buttons.append(types.InlineKeyboardButton(text="👁", callback_data="showed_" + str(film_id)))

                markup.add(*buttons)

                text = "<b>" + film.name + "</b>\n" + " ".join(film.discr.split(" ")[:50]) + "..."

                bot.send_photo(
                    photo=film.img,
                    caption=text,
                    parse_mode="HTML",
                    chat_id=call.message.chat.id,
                    reply_markup=markup)


            if cal.find("showed") >= 0:
                film_id = int(cal.split("_")[1])
                u = Users.get(Users.tel_id == call.message.chat.id)
                print(u.liked)
                u.liked.remove(film_id)
                u.viewed.append(film_id)

                selections_with_film = Selections.select().where(Selections.films.contains(u.cfid)).execute()
                for sel in selections_with_film:
                    if sel in u.selections:
                        u.selections[sel.id] += 1
                    else:
                        u.selections[sel.id] = 1

                u.save()
                markup = types.InlineKeyboardMarkup(row_width=5)
                buttons = []
                for b in range(10):
                    buttons.append(types.InlineKeyboardButton(text=str(b),
                                                              callback_data="addstars_" + str(film_id) + "_" + str(b)))
                markup.add(*buttons)
                bot.edit_message_caption(
                    chat_id=call.message.chat.id,
                    reply_markup=markup,
                    caption="Оцените, пожалуйста, фильм",
                    message_id=call.message.message_id)

            if cal.find("drop") >= 0:
                film_id = cal.split("_")[1]
                u = Users.get(Users.tel_id == call.message.chat.id)
                u.liked.remove(film_id)
                u.disliked.append(film_id)

                selections_with_film = Selections.select().where(Selections.films.contains(u.cfid)).execute()
                for sel in selections_with_film:
                    if sel in u.selections:
                        u.selections[sel.id] -= 2
                u.save()

                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.message_id)

            if cal.find("addstars") >= 0:
                film_id = cal.split("_")[1]
                stars = int(cal.split("_")[2])
                u = Users.get(Users.tel_id == call.message.chat.id)
                f = Films.get(Films.film_id == film_id)
                scount = (Films.likes) + (Films.dislikes) - 1
                f.stars = (f.stars * scount + stars) / (f.stars + 1)

                selections_with_film = Selections.select().where(Selections.films.contains(u.cfid)).execute()
                for sel in selections_with_film:
                    if sel in u.selections:
                        u.selections[sel.id] += (5 - stars) / 2
                u.save()

                bot.edit_message_caption(chat_id=call.message.chat.id,
                                         caption="Оценка добавлена",
                                      message_id=call.message.message_id)

            if cal.find("full") >= 0:
                film_id = cal.split("_")[1]
                send_film(film_id, call.message.chat.id, True)

            if cal.find("delete") >= 0:
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.message_id)

            if cal.find("youtube") >= 0:
                film_id = cal.split("_")[1]
                film = Films.get(Films.film_id == film_id)
                markup = types.InlineKeyboardMarkup(row_width=2)
                buttons = []

                buttons.append(
                    types.InlineKeyboardButton(text="Смотреть фильм", url="https://my-hit.org/film/" + film_id))
                buttons.append(types.InlineKeyboardButton(text="Назад", callback_data="delete"))

                markup.add(*buttons)

                if film.youtube.find("watch") == -1:
                    ypage = requests.get("https://www.youtube.com/results", params={"search_query": film.name}).text
                    ypage = BeautifulSoup(ypage, features="html.parser")
                    film.youtube = "https://www.youtube.com" + ypage.find("a", href=re.compile("watch"))["href"]
                    film.save()

                m = bot.send_message(text=film.youtube,
                                     chat_id=call.message.chat.id,
                                     reply_markup=markup)

                u = Users.get(Users.tel_id == call.message.chat.id)
                u.ctmes = m.message_id
                u.save()

        except Exception as e:
            print(e)

        bot.answer_callback_query(call.id, text="")
        return True


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    u = Users.get_or_none(Users.tel_id == message.chat.id)
    print(message.text)
    if u == None:
        """the user is not in the database """
        bot.send_message(message.chat.id, "Вначале пройдите авторизацию")
        return
    elif u.cms == 0:
        if message.text == INVITE_PASS:
            u.cms = 1
            bot.send_message(message.chat.id, START_VK_TEXT)
        else:
            bot.send_message(message.chat.id, START_BAD_PASS_TEXT)

        u.save()
        return
    elif u.cms == 1:
        u.cms = 2
        if re.match(r'.*vk\.com/.*', message.text) != None:
            u.info["vk"] = message.text
            bot.send_message(message.chat.id, START_TEXT, reply_markup=base_keyboard_menu)
        else:
            print(re.match(r'.*vk\.com/.*', message.text))
            print("Error",message.text)
            bot.send_message(message.chat.id, START_BAD_VK_TEXT)

        u.save()
        return

    elif message.text == BTN_1_TEXT and u.cms == 2:
        bot.send_message(message.chat.id, "Чтобы вернуться в главное меню отпрвьте команду /menu",
                         reply_markup=base_keyboard_search)
        u = next_film(u, message.chat.id)
        u.cms = 3

    elif message.text == BTN_2_TEXT and u.cms == 2:
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        films = Films.select().where(Films.film_id.in_(u.liked))
        for f in films:
            buttons.append(types.InlineKeyboardButton(text=f.name, callback_data="film_" + str(f.film_id)))

        markup.add(*buttons)
        if len(films) > 0:
            bot.send_message(message.chat.id, "Вот список понравившихся вам фильмов",
                             reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Список понравившихся фильмов пуст")

    elif message.text in [BTN_1_SEARCH, BTN_2_SEARCH, BTN_3_SEARCH] and u.cms == 3:
        f = Films.get(Films.film_id == u.cfid)

        if message.text == BTN_3_SEARCH:
            u.liked.append(u.cfid)
            s = Selections.get(user_id=u.tel_id)
            s.films.append(u.cfid)
            selections_with_film = Selections.select().where(Selections.films.contains(u.cfid)).execute()
            for sel in selections_with_film:
                if sel in u.selections:
                    u.selections[sel.id] += 1
                else:
                    u.selections[sel.id] = 1
            f.likes += 1
            f.selections.append(u.tel_id)

        if message.text == BTN_2_SEARCH:
            u.viewed.append(u.cfid)
            s = Selections.get(user_id=u.tel_id)
            s.films.append(u.cfid)
            s.save()
            selections_with_film = Selections.select().where(Selections.films.contains(u.cfid)).execute()
            for sel in selections_with_film:
                if sel in u.selections:
                    u.selections[sel.id] += 1
                else:
                    u.selections[sel.id] = 1
            f.likes += 1
            f.selections.append(u.tel_id)

        if message.text == BTN_1_SEARCH:
            u.disliked.append(u.cfid)
            selections_with_film = Selections.select().where(Selections.films.contains(u.cfid)).execute()
            for sel in selections_with_film:
                if sel in u.selections:
                    u.selections[sel.id] -= 1
                else:
                    u.selections[sel.id] = 0
            f.dislikes += 1

        u = next_film(u, message.chat.id, True)
        f.save()

        bot.delete_message(chat_id=message.chat.id,
                           message_id=message.message_id)
    else:
        print("Unknown message")
        bot.delete_message(chat_id=message.chat.id,
                           message_id=message.message_id)
    u.save()


# Main Fanction

if __name__ == '__main__':
    print("Start")
    bot.polling(none_stop=True)
