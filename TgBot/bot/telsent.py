# -*- coding: utf-8 -*-
import json
import os
import re
import sys
from cmath import sqrt

from playhouse.shortcuts import model_to_dict

sys.path.append('../')
sys.path.append('./')

from datetime import datetime

import requests
from telebot.types import InputMediaPhoto, InputMediaVideo

from config import *

from models import *
import telebot
from telebot import types
from TextConstants import *
from bs4 import BeautifulSoup

import logging

# add filemode="w" to overwrite
filename = None
if "SERVER" in os.environ:
    filename = "bot.log"

logging.basicConfig(format=u'[LINE:%(lineno)d] # %(levelname)s [%(asctime)s]: %(message)s', level=logging.INFO,
                    filename=filename
                    )

logger = logging.getLogger("cs")

CONFIG = {}
for c in Config.select():
    if c.value == "json":
        CONFIG[c.name] = c.json
    else:
        CONFIG[c.name] = c.value

# BOT CODE
bot = telebot.TeleBot(CONFIG["TELEGRAM_TOKEN"])

base_keyboard_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
base_button_1 = types.KeyboardButton(text=BTN_1_TEXT)
base_button_2 = types.KeyboardButton(text=BTN_2_TEXT)
# base_button_3 = types.KeyboardButton(text=BTN_3_TEXT)
# base_button_4 = types.KeyboardButton(text=BTN_4_TEXT)

base_keyboard_menu.row(base_button_1, base_button_2)
# base_keyboard_menu.row(base_button_3, base_button_4)

base_keyboard_search = types.ReplyKeyboardMarkup(resize_keyboard=True)

base_button_1 = types.KeyboardButton(text=BTN_1_SEARCH)
base_button_2 = types.KeyboardButton(text=BTN_S_SEARCH)
base_button_3 = types.KeyboardButton(text=BTN_2_SEARCH)
base_button_4 = types.KeyboardButton(text=BTN_3_SEARCH)
# base_button_4 = types.KeyboardButton(text=BTN_4_SEARCH)

base_keyboard_search.row(base_button_1, base_button_2, base_button_3, base_button_4)


# base_keyboard_search.row(base_button_4)


def alarm(text):
    logger.info(text)
    requests.get("https://alarmerbot.ru/?key={}&message= ".format(CONFIG["ALAMER_KEY"]) + str(text))


def send_film(film_id, message_id, edit=0):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []

    film = Films.get(Films.film_id == film_id)

    buttons.append(types.InlineKeyboardButton(text="Подробнее", callback_data="more_" + str(film_id)))
    buttons.append(types.InlineKeyboardButton(text="Трейлер", callback_data="youtube_" + str(film_id)))

    markup.add(*buttons)

    text = "<b>" + film.name + "</b>\n" + " ".join(film.discr.split(" ")[:50])
    if len(film.discr.split(" ")) > 50:
        text += "..."
    if edit > 0:
        try:
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
        except:
            logger.error("Can't edit message")

    m = bot.send_photo(chat_id=message_id,
                       photo=film.img,
                       parse_mode="HTML",
                       caption=text,
                       reply_markup=markup)

    return m.message_id


def send_film_collection(films_ids, message_id, cfmes):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    marks = {}

    films = Films.select(Films.name, Films.film_id).where(Films.film_id.in_(films_ids)).execute()

    for f in films:
        buttons.append(types.InlineKeyboardButton(text=f.name, callback_data="like_" + str(f.film_id)))
        marks["like_" + str(f.film_id)] = f.name

    buttons.append(types.InlineKeyboardButton(text=BTN_THEN, callback_data="like_-1"))

    markup.add(*buttons)

    text = "Выбери фильмы, которые ты смотрел или хотел бы посмотреть."
    if cfmes > 0:
        try:
            bot.edit_message_reply_markup(
                chat_id=message_id,
                reply_markup=markup,
                message_id=cfmes
            )
            Messages.update({"reply_markup": marks}).where(
                Messages.mes_id == str(message_id) + "_" + str(cfmes)).execute()
            return cfmes
        except:
            logger.info("Cant edit list of films")
            pass
    m = bot.send_message(chat_id=message_id,
                         parse_mode="HTML",
                         text=text,
                         reply_markup=markup)
    print(m.chat.id * 100000 + m.message_id)
    Messages.create(mes_id=str(m.chat.id) + "_" + str(m.message_id), text=text, reply_markup=marks)

    return m.message_id


def vcos(a, b):
    ch = 0
    znA = 0
    znB = 0
    for c in zip(a, b):
        ch += c[0] * c[1]
        znA += c[0] * c[0]
        znB += c[1] * c[1]
    return ch / ((znA ** 0.5) * (znB ** 0.5))


def predict_film_list(tel_id):
    import numpy as np
    import random
    dtime = datetime.now()

    u = Users.get(Users.tel_id == tel_id)

    if u.ustatus > 0:
        pb = np.array(list(u.selections.values()), dtype='float')
        pb *= pb > 0
        pb /= pb.sum()
        selections = np.random.choice(list(u.selections.keys()), p=pb, size=15)
        selections = [s.item() for s in selections]

        options = Films.select().where(
            (Films.selections.contains_any(selections)) & (Films.film_id.not_in(u.liked))
            & (Films.film_id.not_in(u.viewed)) & (Films.shit < 10) & (Films.film_id.not_in(u.disliked))).order_by(
            Films.stars,
            Films.likes).limit(100).execute()

    if u.ustatus == 0:
        options = Films.select().where(
            (Films.level > 1) & (Films.film_id.not_in(u.liked)) & (Films.stars > 9)
            & (Films.film_id.not_in(u.viewed)) & (Films.shit < 6) & (Films.film_id.not_in(u.disliked))).order_by(
            Films.stars,
            Films.likes).limit(100).execute()

    predict = {}
    sel_sum = sum(u.selections.values()) + 1  # mean selection priority
    ganr_sum = sum(u.ganres.values()) + 1  # mean selection priority

    selections = {s: u.selections[s] / sel_sum for s in u.selections}
    ganres = {g: u.ganres[g] / ganr_sum for g in u.ganres}

    for o in options:  # all avilible films
        predict[o.film_id] = 1
        scount = 0
        for s in o.selections:  # all users fun categories
            if s in selections:  # film is in user`s fun group
                scount += selections[s]  # how important is this group

        gcount = 0
        for g in o.ganres:
            if g in ganres:
                gcount += u.ganres[g]

        g1 = {}
        for g in o.ganres:
            g1[str(g)] = 1

        g2 = u.ganres
        for i in range(25):
            if str(i) not in g1:
                g1[str(i)] = 0
            if str(i) not in g2:
                g2[str(i)] = 0

        g1 = [t[1] for t in sorted(g1.items(), key=lambda kv: int(kv[0]))]
        g2 = [t[1] for t in sorted(g2.items(), key=lambda kv: int(kv[0]))]

        dcos = vcos(g1, g2)

        predict[o.film_id] += (1 - dcos) * int(CONFIG["WEIGHT_COS"])
        predict[o.film_id] += gcount * int(CONFIG["WEIGHT_GANRE"])  # доля жанров фильма в наших фаворитах
        predict[o.film_id] += scount * int(CONFIG["WEIGHT_SELECTION"])  # доля любимых коллеекций среди фильмов
        predict[o.film_id] += o.stars * int(CONFIG["WEIGHT_STARS"])
        predict[o.film_id] += 1 / (abs(o.meanage - u.age) + 1) * int(CONFIG["WEIGHT_AGE"])
        predict[o.film_id] += 1 / (abs(o.sex - u.sex) * 10 + 1) * int(CONFIG["WEIGHT_SEX"])
        predict[o.film_id] += (o.likes) / (o.likes + o.dislikes + 1) * int(CONFIG["WEIGHT_LIKE"])
        predict[o.film_id] += (1 / (2020 - o.year)) * int(CONFIG["WEIGHT_YEAR"])
        predict[o.film_id] -= o.shit * int(CONFIG["WEIGHT_YEAR"])
        if o.year < 2000:
            predict[o.film_id] -= 4

    pb = np.array(list(predict.values()), dtype='float')
    pb /= pb.sum()
    pred = np.random.choice(list(predict.keys()), p=pb, size=20)

    logger.info("Predicting: " + str(datetime.now() - dtime))
    return list(set([p.item() for p in pred]))


def next_film(u, edit=False):
    Send = False
    message_id = u.tel_id
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

    if len(u.predict_films) < 2:
        u.predict_films = predict_film_list(message_id)
        if Send:
            u.cfmes = send_film(u.predict_films[0], message_id)
            u.cfid = u.predict_films[0]
            del u.predict_films[0]

    return u


def next_films_collections(u):
    if len(u.predict_films) < 8:
        u.predict_films += predict_film_list(u.tel_id)

    u.cfmes = send_film_collection(u.predict_films[:8], u.tel_id, u.cfmes)
    u.predict_films = u.predict_films[8:]

    return u


# Start Fanction
@bot.message_handler(commands=['start'])
def startf(message):
    u = Users.get_or_none(Users.tel_id == message.chat.id)
    if u == None:
        Users.create(tel_id=message.chat.id, name=str(message.from_user.first_name) + " " + str(
            message.from_user.last_name), cms=0,  # 1 - enter age
                     nicname=str(message.from_user.username))

        Selections.get_or_create(name=str(message.from_user.username), user_id=message.chat.id)

        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton(text="🙍‍♂️", callback_data="info_sex_0"),
                   types.InlineKeyboardButton(text="🙍‍♀️", callback_data="info_sex_1"))

        bot.send_message(message.chat.id, START_PROFIL_TEXT, reply_markup=markup)
        alarm("New user @" + str(message.from_user.username))

    else:
        bot.send_message(message.chat.id, YOU_THERE_TEXT)


@bot.message_handler(commands=['menu'])
def menu(message):
    u = Users.get_or_none(Users.tel_id == message.chat.id)
    if u != None:
        if u.cms >= 2:
            bot.send_message(message.chat.id, OPEN_MENU_TEXT, reply_markup=base_keyboard_menu)
            u.cms = 2
            u.save()


@bot.callback_query_handler(
    func=lambda call: "like" in call.data)
def likefilm(call):
    logger.info("like " + call.data)
    fid = int(call.data.split("_")[1])
    u = Users.get(Users.tel_id == call.message.chat.id)

    if len(u.viewed) >= 8:
        u.ustatus = 1
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        bot.send_message(call.message.chat.id,
                         "Настройка алгоритма окончена, теперь бот работает в штатном режиме,"
                         " чтобы вернуться в главное меню отпрвьте команду /menu",
                         reply_markup=base_keyboard_search)
        u = next_film(u)

    elif fid == -1:
        mes = Messages.get_or_none(Messages.mes_id == str(call.message.chat.id) + "_" + str(call.message.message_id))
        ids = [id.split("_")[1] for id in mes.reply_markup.keys()]
        films = Films.select().where(Films.film_id.in_(ids)).execute()
        for f in films:
            u.disliked.append(f.film_id)
            f.stars = (f.stars * (f.likes + f.dislikes) + f.stars-3) / (f.likes + f.dislikes + 1)
            f.dislikes += 1

            for sel in f.selections:
                if sel in u.selections:
                    u.selections[sel] -= 1
                else:
                    u.selections[sel] = -1
            f.save()
            u = next_films_collections(u)
        f.save()
        u.save()
        return
    else:
        film = Films.get_or_none(Films.film_id == fid)
        film.likes += 1

        for g in film.ganres:
            if g in u.ganres:
                u.ganres[g] += 2
            else:
                u.ganres[g] = 2

        for s in film.selections:
            if s in u.selections:
                u.selections[g] += 2
            else:
                u.selections[g] = 2
        u.viewed.append(film.film_id)

        film.save()

        mes = Messages.get_or_none(Messages.mes_id == str(call.message.chat.id) + "_" + str(call.message.message_id))
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        mes.text += "\n<b>" + mes.reply_markup[call.data] + "</b>"
        del mes.reply_markup[call.data]

        for m in mes.reply_markup:
            buttons.append(types.InlineKeyboardButton(text=mes.reply_markup[m], callback_data=m))
        buttons.append(types.InlineKeyboardButton(text=BTN_THEN, callback_data="like_-1"))
        mes.save()

        markup.add(*buttons)
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                text=mes.text,
                parse_mode="HTML",
                reply_markup=markup,
                message_id=call.message.message_id
            )
        except:
            logger.info("Can't edit message")
            u = next_films_collections(u)

    u.save()
    bot.answer_callback_query(call.id, text="Фильм добавлен")
    return True


@bot.callback_query_handler(
    func=lambda call: sum([v in call.data for v in
                           ["more", "film", "showed", "drop", "addstars", "full", "delete", "youtube", "info"]]) > 0)
def callback(call):
    if call.from_user:
        cal = str(call.data)
        logger.info(str(call.message.chat.username) + ": " + cal)
        answer_callback_query = ""
        try:
            if cal.find("delete") >= 0:
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.message_id)

            if cal.find("more") >= 0:
                film_id = cal.split("_")[1]
                film = Films.get(Films.film_id == film_id)
                text = "<b>" + film.name + "</b>\n\n" + film.discr + "\n"
                for i in film.info:
                    text += "<b>" + i + "</b>:  " + film.info[i] + "\n"

                text = text[:1023]
                film.opening += 1
                film.save()
                markup = types.InlineKeyboardMarkup(row_width=2)
                buttons = []

                buttons.append(types.InlineKeyboardButton(text="Смотреть", url="https://my-hit.org/film/" + film_id))
                buttons.append(types.InlineKeyboardButton(text="Трейлер", callback_data="youtube_" + str(film_id)))

                markup.add(*buttons)
                try:
                    bot.edit_message_caption(chat_id=call.message.chat.id,
                                             message_id=call.message.message_id,
                                             parse_mode="HTML",
                                             reply_markup=markup,
                                             caption=text)
                except Exception as e:
                    logger.error("Can't edit film" + str(e))
                    answer_callback_query = "Слишком старый пост, не могу отредактировать"

            if cal.find("film") >= 0:
                film_id = cal.split("_")[1]
                u = Users.get(Users.tel_id == call.message.chat.id)
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
                f = Films.get_or_none(Films.film_id == film_id)
                u = Users.get(Users.tel_id == call.message.chat.id)
                u.liked.remove(film_id)
                u.viewed.append(film_id)

                for sel in f.selections:
                    if sel in u.selections:
                        u.selections[sel] += 1
                    else:
                        u.selections[sel] = 1

                u.save()
                markup = types.InlineKeyboardMarkup(row_width=5)
                buttons = []
                for b in range(10):
                    buttons.append(types.InlineKeyboardButton(text=str(b),
                                                              callback_data="addstars_" + str(film_id) + "_" + str(b)))
                markup.add(*buttons)
                try:
                    bot.edit_message_caption(
                        chat_id=call.message.chat.id,
                        reply_markup=markup,
                        caption="Оцените, пожалуйста, фильм",
                        message_id=call.message.message_id)
                except:
                    logger.error("Can't edit film")
                    answer_callback_query = "Слишком старый пост, не могу отредактировать"

            if cal.find("drop") >= 0:
                film_id = int(cal.split("_")[1])
                f = Films.get_or_none(Films.film_id == film_id)
                u = Users.get(Users.tel_id == call.message.chat.id)
                u.liked.remove(film_id)
                u.disliked.append(film_id)

                for sel in f.selections:
                    if sel in u.selections:
                        u.selections[sel] -= 2
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

                for sel in f.selections:
                    if sel in u.selections:
                        u.selections[sel] += (5 - stars) / 2
                u.save()
                try:
                    bot.edit_message_caption(chat_id=call.message.chat.id,
                                             caption="Оценка добавлена",
                                             message_id=call.message.message_id)
                except:
                    logger.error("Can't edit film")
                    bot.delete_message(chat_id=call.message.chat.id,
                                       message_id=call.message.message_id)
                    bot.send_message(call.message.chat.id, "Оценка добавлена")

            if cal.find("error") >= 0:
                film_id = cal.split("_")[1]
                film = Films.get_or_none(Films.film_id == film_id)
                answer_callback_query = "Ваш отзыв учтен"
                film.errors += 1
                film.save()

            if cal.find("full") >= 0:
                film_id = cal.split("_")[1]
                send_film(film_id, call.message.chat.id, True)

            if cal.find("youtube") >= 0:
                film_id = cal.split("_")[1]
                film = Films.get(Films.film_id == film_id)
                markup = types.InlineKeyboardMarkup(row_width=2)
                buttons = []

                buttons.append(types.InlineKeyboardButton(text="Назад", callback_data="delete"))

                if film.errors > 50:
                    markup.add(*buttons)
                    bot.send_message(text="К сожалению, для этого фильма нет трейлера",
                                     chat_id=call.message.chat.id,
                                     reply_markup=markup)

                else:
                    markup.add(
                        types.InlineKeyboardButton(text="Это не трейлер", callback_data="error_" + film_id + "_delete"),
                        types.InlineKeyboardButton(text="Назад", callback_data="delete"))

                    if film.youtube.find("watch") == -1 or film.errors % 7 == 1:
                        ypage = requests.get("https://www.youtube.com/results", params={"search_query": film.name}).text
                        ypage = BeautifulSoup(ypage, features="html.parser")
                        film.youtube = "https://www.youtube.com" + \
                                       ypage.find_all("a", href=re.compile("watch"))[film.errors // 7]["href"]

                    film.treilers += 1
                    film.save()
                    m = bot.send_message(text=film.youtube,
                                         chat_id=call.message.chat.id,
                                         reply_markup=markup)

                    u = Users.get(Users.tel_id == call.message.chat.id)
                    u.ctmes = m.message_id
                    u.save()

            if cal.find("info") >= 0:
                info = cal.split("_")[1]
                val = cal.split("_")[2]
                u = Users.get(Users.tel_id == call.message.chat.id)

                if info == "sex":
                    u.age = int(val)
                    u.cms = 1
                    bot.send_message(call.message.chat.id, START_ENTER_AGE_TEXT)
                if info == "age":
                    u.age = int(val)
                try:
                    bot.edit_message_text(chat_id=call.message.chat.id,
                                          text="Ответ принят",
                                          message_id=call.message.message_id)
                except:
                    logger.error("Can't edit film")
                    bot.delete_message(chat_id=call.message.chat.id,
                                       message_id=call.message.message_id)
                    bot.send_message(call.message.chat.id, "Ответ принят")
                u.save()

        except Exception as e:
            logger.error(e)

        bot.answer_callback_query(call.id, text=answer_callback_query)
        return True


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    u = Users.get_or_none(Users.tel_id == message.chat.id)
    if u == None:
        """the user is not in the database """
        bot.send_message(message.chat.id, "Вначале пройдите авторизацию, для этого отправьте команду /start")
        return

    logger.info(u.name + " " + message.text)
    u.last_visit = datetime.now()

    if u.cms == 0:
        if message.text == CONFIG["INVITE_PASS"]:

            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(types.InlineKeyboardButton(text="🙍‍♂️", callback_data="info_sex_0"),
                       types.InlineKeyboardButton(text="🙍‍♀️", callback_data="info_sex_1"))

            bot.send_message(message.chat.id, START_PROFIL_TEXT, reply_markup=markup)
        else:
            bot.send_message(message.chat.id, START_BAD_PASS_TEXT)

        u.save()
        return

    elif u.cms == 1:

        try:
            u.age = int(message.text)
            if u.age > 0 and u.age < 102:
                u.cms = 2
                u.save()
                bot.send_message(message.chat.id, "Ваш ответ принят, выбирите дальнейшее действие",
                                 reply_markup=base_keyboard_menu)
            else:
                bot.send_message(message.chat.id, PARSING_ERROR)
        except:
            bot.send_message(message.chat.id, PARSING_ERROR)

        return

    elif message.text == BTN_1_TEXT and u.cms == 2:

        if u.ustatus > 0:
            bot.send_message(message.chat.id, "Чтобы вернуться в главное меню отпрвьте команду /menu",
                             reply_markup=base_keyboard_search)
            u = next_film(u)
        else:
            bot.send_message(message.chat.id,
                             text="Давай проведем экспресс подборку, чтобы настроить алгоритм под тебя. "
                                  "Как только ты выберешь 8 фильмов, бот начнет работать в стандартном режиме",
                             reply_markup=types.ReplyKeyboardRemove())

            u = next_films_collections(u)

        u.cms = 3

    elif message.text == BTN_2_TEXT and u.cms == 2:
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        films = Films.select().where(Films.film_id.in_(u.liked)).execute()
        for f in films:
            buttons.append(types.InlineKeyboardButton(text=f.name, callback_data="film_" + str(f.film_id)))

        markup.add(*buttons)
        if len(films) > 0:
            bot.send_message(message.chat.id, "Вот список понравившихся вам фильмов",
                             reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Список понравившихся фильмов пуст")

    elif message.text in [BTN_1_SEARCH, BTN_S_SEARCH, BTN_2_SEARCH, BTN_3_SEARCH] and u.cms == 3:
        if u.cfid == 0:
            alarm(str(u.tel_id) + " Cfid is 0!")

        f = Films.get(Films.film_id == u.cfid)
        mark_wight = 1.5 - u.mark_wight / 2

        if message.text == BTN_3_SEARCH or message.text == BTN_2_SEARCH:

            s = Selections.get(user_id=u.tel_id)
            s.films.append(u.cfid)

            for sel in f.selections:
                if sel in u.selections:
                    u.selections[sel] += 1
                else:
                    u.selections[sel] = 1

            for kk in sorted(u.selections, key=lambda k: u.selections[k])[:-600]:
                del u.selections[kk]

            for g in f.ganres:
                if g in u.ganres:
                    u.ganres[g] += 1
                else:
                    u.ganres[g] = 1

            f.meanage = (f.meanage * f.likes + u.age) / (f.likes + 1)
            f.sex = (f.sex * f.likes + u.sex) / (f.likes + 1)
            f.stars = (f.stars * (f.likes + f.dislikes) + 10 * mark_wight) / (f.likes + f.dislikes + 1)
            f.likes += 1
            f.selections.append(u.tel_id)
            Dataset.create(data=datetime.now(), user_value=model_to_dict(u),
                           film_value=model_to_dict(f), result=1)

        if message.text == BTN_2_SEARCH:
            u.viewed.append(u.cfid)
            u.mark_wight = (u.mark_wight * u.just_marked + 2) / (u.just_marked + 1)
            f.shit -= 1

        if message.text == BTN_3_SEARCH:
            u.liked.append(u.cfid)
            u.mark_wight = (u.mark_wight * u.just_marked + 1) / (u.just_marked + 1)

        if message.text == BTN_1_SEARCH or message.text == BTN_S_SEARCH:
            u.disliked.append(u.cfid)
            f.stars = (f.stars * (f.likes + f.dislikes) + 3.5 * mark_wight) / (f.likes + f.dislikes + 1)
            f.dislikes += 1
            u.mark_wight = (u.mark_wight * u.just_marked + -1) / (u.just_marked + 1)

            for sel in f.selections:
                if sel in u.selections:
                    u.selections[sel] -= 1
                else:
                    u.selections[sel] = -1

            for g in f.ganres:
                if g in u.ganres:
                    u.ganres[g] -= 1
                else:
                    u.ganres[g] = 0

            Dataset.create(data=datetime.now(), user_value=model_to_dict(u),
                           film_value=model_to_dict(f), result=0)

        if message.text == BTN_S_SEARCH:
            f.shit += 2
            f.stars = (f.stars * (f.likes + f.dislikes) + 1 * mark_wight) / (f.likes + f.dislikes + 1)
            u.mark_wight = (u.mark_wight * u.just_marked - 2) / (u.just_marked + 1)

        u = next_film(u, True)
        f.save()

        bot.delete_message(chat_id=message.chat.id,
                           message_id=message.message_id)

    elif message.text == AUTO_KILL:
        bot.send_message(message.chat.id, "Выключение")
        logger.info("Off")
        exit(0)

    else:
        print("Unknown message")
        bot.delete_message(chat_id=message.chat.id,
                           message_id=message.message_id)

    Messages.create(mes_id=str(message.chat.id) + "_" + str(message.message_id), text=message.text, user=u.tel_id,
                    btime=datetime.now())
    u.save()


# Main Fanction

if __name__ == '__main__':

    if "SERVER" in os.environ:
        logger.info("Starting on server")
    else:
        logger.info("DEBAG Starting")

    er = 5
    while er > 0:
        try:
            bot.polling(none_stop=True)

        except Exception as e:
            logger.error(str(e))
            if "SERVER" in os.environ:
                er -= 1
                alarm(e)
            else:
                break
