# -*- coding: utf-8 -*-
import re
import sys

from playhouse.shortcuts import model_to_dict
from telebot.apihelper import ApiException

from models.Config import Config
from models.Films import Films
from models.Messages import Messages
from models.Users import Users

sys.path.append('../')
sys.path.append('./')

from datetime import datetime, timedelta

import requests
from telebot.types import InputMediaPhoto

from models import *
import telebot
from telebot import types
from TextConstants import *
from bs4 import BeautifulSoup

import logging

filename = "bot.log"
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

# CONFIG["TELEGRAM_TOKEN"] = "1046892377:AAFw28YUJDaMD1s-n_GhpXsQKS9oqNOsi3U"
CONFIG["SERVER_URL"] = "http://s1.neafiol.site:9091"
# CONFIG["SERVER_URL"] = "http://localhost:9091"

# BOT CODE
bot = telebot.TeleBot(CONFIG["TELEGRAM_TOKEN"])

base_keyboard_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
base_button_1 = types.KeyboardButton(text=BTN_1_TEXT)
base_button_2 = types.KeyboardButton(text=BTN_2_TEXT)

base_keyboard_menu.row(base_button_1, base_button_2)

base_keyboard_search = types.ReplyKeyboardMarkup(resize_keyboard=True)

base_button_1 = types.KeyboardButton(text=BTN_1_SEARCH)
base_button_2 = types.KeyboardButton(text=BTN_S_SEARCH)
base_button_3 = types.KeyboardButton(text=BTN_2_SEARCH)
base_button_4 = types.KeyboardButton(text=BTN_3_SEARCH)

base_keyboard_search.row(base_button_1, base_button_2, base_button_3, base_button_4)


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

            try:
                bot.edit_message_caption(chat_id=message_id,
                                         message_id=edit,
                                         caption=text,
                                         parse_mode="HTML",
                                         reply_markup=markup)
            except ApiException as tge:
                logger.info("Bad text parsing" + str(tge))
                text = text.replace("</b>", "").replace("<b>", "").replace("</br>", "\n")
                bot.edit_message_caption(chat_id=message_id,
                                         message_id=edit,
                                         caption=text,
                                         reply_markup=markup)

            return edit
        except:
            logger.error("Can't edit message")

    try:
        m = bot.send_photo(chat_id=message_id,
                           photo=film.img,
                           parse_mode="HTML",
                           caption=text,
                           reply_markup=markup)
    except ApiException as tge:
        logger.info("Bad Film")
        logger.error(str(tge))
        text = text.replace("</b>", "").replace("<b>", "").replace("</br>", "\n")
        m = bot.send_photo(chat_id=message_id,
                           photo="https://diamedica.by/uploads/no-image.jpg",
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

    text = "Выбери фильмы, которые ты смотрел или точно знаешь, что хотел бы посмотреть."
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
        except Exception as e:
            logger.info("Cant edit list of films " + str(e))

    m = bot.send_message(chat_id=message_id,
                         parse_mode="HTML",
                         text=text,
                         reply_markup=markup)
    Messages.create(mes_id=str(m.chat.id) + "_" + str(m.message_id), text=text, reply_markup=marks)

    return m.message_id


def predict_film_list(tel_id):
    dtime = datetime.now()

    r = requests.get(CONFIG["SERVER_URL"] + '/user', params={
        "user_id": tel_id,
        "type": "get_predict",
        "predict_size": 20
    })

    logger.info("Predicting: " + str(datetime.now() - dtime))
    return r.json()


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
    logger.info("next_films_collections " + str(len(u.predict_films)))
    return u


# Start Fanction
@bot.message_handler(commands=['start'])
def startf(message):
    u = Users.get_or_none(Users.tel_id == message.chat.id)
    if u == None:
        Users.create(tel_id=message.chat.id, name=str(message.from_user.first_name) + " " + str(
            message.from_user.last_name), cms=0,  # 1 - enter age
                     nicname=str(message.from_user.username))

        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton(text="🙍‍♂️", callback_data="info_sex_0"),
                   types.InlineKeyboardButton(text="🙍‍♀️", callback_data="info_sex_1"))

        requests.post(CONFIG["SERVER_URL"] + '/user', json={
            "user_id": message.chat.id,
        })

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


@bot.message_handler(commands=['help'])
def menu(message):
    u = Users.get_or_none(Users.tel_id == message.chat.id)
    if u != None:
        u.cms = 5
        bot.send_message(message.chat.id, HELP_TEXT)
        u.save()


@bot.callback_query_handler(
    func=lambda call: "like" in call.data)
def likefilm(call):
    logger.info("like " + call.data)
    fid = int(call.data.split("_")[1])
    u = Users.get(Users.tel_id == call.message.chat.id)

    if fid == -1:
        liked = requests.get(CONFIG["SERVER_URL"] + '/user', params={
            "user_id": u.tel_id,
            "type": "get_liked",
        }).json()
        print("liked", liked)
        if len(liked) >= 5:
            u.ustatus = 1
            bot.delete_message(chat_id=call.message.chat.id,
                               message_id=call.message.message_id)
            bot.send_message(call.message.chat.id,
                             "Настройка алгоритма окончена, теперь бот работает в штатном режиме,"
                             " чтобы вернуться в главное меню отпрвьте команду /menu",
                             reply_markup=base_keyboard_search)
            u = next_film(u)
            u.save()
            return
        else:
            mes = Messages.get_or_none(
                Messages.mes_id == str(call.message.chat.id) + "_" + str(call.message.message_id))
            ids = [id.split("_")[1] for id in mes.reply_markup.keys()]
            for f in ids:
                requests.post(CONFIG["SERVER_URL"] + '/mark', json={
                    "user_id": u.tel_id,
                    "film_id": f,
                    "result": -1,
                })
            logger.info("Next menu")
            u = next_films_collections(u)

            u.save()
            return
    else:
        requests.post(CONFIG["SERVER_URL"] + '/mark', json={
            "user_id": u.tel_id,
            "film_id": fid,
            "result": 1,
        })

        mes = Messages.get_or_none(Messages.mes_id == str(call.message.chat.id) + "_" + str(call.message.message_id))
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        if call.data in mes.reply_markup:
            mes.text += "\n<b>" + mes.reply_markup[call.data] + "</b>"
            del mes.reply_markup[call.data]
        else:
            mes.text += "\n"
            logger.info("Error " + call.data)

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
            try:
                text = mes.text.replace("</b>", "").replace("<b>", "").replace("</br>", "\n")
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    text=text,
                    reply_markup=markup,
                    message_id=call.message.message_id
                )
            except:
                logger.info("Can't edit message")
                u = next_films_collections(u)

    u.just_marked += 1
    u.save()
    bot.answer_callback_query(call.id, text="Фильм добавлен")
    return True


@bot.callback_query_handler(
    func=lambda call: "checkvk" in call.data)
def checkvk(call):
    logger.info("checkvk " + str(call.message.chat.id))

    u = Users.get(Users.tel_id == call.message.chat.id)
    if u.vk_id > 0:
        u.cms = 2
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        bot.send_message(call.message.chat.id,
                         "Авторизация успешно пройдена, больше мы Вас не побеспокоим",
                         reply_markup=base_keyboard_menu)
        u.save()

    else:
        bot.send_message(call.message.chat.id,
                         "Сообщение от вас не обнаружено")

    bot.answer_callback_query(call.id, text="")
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
                requests.post(CONFIG["SERVER_URL"] + '/mark', json={
                    "film_id": film_id,
                    "event": "open",
                })

                film = Films.get(Films.film_id == film_id)
                text = "<b>" + film.name + "</b>\n\n" + film.discr + "\n"
                for i in film.info:
                    text += "<b>" + i + "</b>:  " + film.info[i] + "\n"

                text = text[:1000]
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
                    text = text.replace("</b>", "").replace("<b>", "").replace("</br>", "\n")
                    try:
                        bot.edit_message_caption(chat_id=call.message.chat.id,
                                                 message_id=call.message.message_id,
                                                 reply_markup=markup,
                                                 caption=text)
                    except:
                        answer_callback_query = "Слишком старый пост, не могу отредактировать"

            if cal.find("film") >= 0:
                film_id = cal.split("_")[1]
                u = Users.get(Users.tel_id == call.message.chat.id)
                markup = types.InlineKeyboardMarkup(row_width=2)
                buttons = []

                film = Films.get(Films.film_id == film_id)
                buttons.append(types.InlineKeyboardButton(text="Подробнее", callback_data="more_" + str(film_id)))
                buttons.append(types.InlineKeyboardButton(text="Трейлер", callback_data="youtube_" + str(film_id)))

                liked = requests.get(CONFIG["SERVER_URL"] + '/user', params={
                    "user_id": u.tel_id,
                    "type": "get_liked",
                }).json()

                if int(film_id) in liked:
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
                u = Users.get(Users.tel_id == call.message.chat.id)
                film_id = int(cal.split("_")[1])

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

                u = Users.get(Users.tel_id == call.message.chat.id)
                requests.patch(CONFIG["SERVER_URL"] + '/user', json={
                    "user_id": u.tel_id,
                    "unliked_film_id": film_id
                })

                bot.edit_message_caption(chat_id=call.message.chat.id,
                                         caption="Фильм удален.",
                                         message_id=call.message.message_id)

            if cal.find("addstars") >= 0:
                film_id = cal.split("_")[1]
                stars = int(cal.split("_")[2])
                u = Users.get(Users.tel_id == call.message.chat.id)
                if stars > 7:
                    requests.post(CONFIG["SERVER_URL"] + '/mark', json={
                        "user_id": u.tel_id,
                        "film_id": film_id,
                        "result": 1,
                    })
                else:
                    requests.post(CONFIG["SERVER_URL"] + '/mark', json={
                        "user_id": u.tel_id,
                        "film_id": film_id,
                        "result": -1,
                    })

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
                requests.post(CONFIG["SERVER_URL"] + '/mark', json={
                    "film_id": film_id,
                    "event": "error",
                })
                answer_callback_query = "Ваш отзыв учтен"
            if cal.find("full") >= 0:
                film_id = cal.split("_")[1]
                requests.post(CONFIG["SERVER_URL"] + '/mark', json={
                    "film_id": film_id,
                    "event": "open",
                })
                send_film(film_id, call.message.chat.id, True)

            if cal.find("youtube") >= 0:
                film_id = cal.split("_")[1]
                requests.post(CONFIG["SERVER_URL"] + '/mark', json={
                    "film_id": film_id,
                    "event": "trailer",
                })

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
                        ypage = ypage.find_all("a", href=re.compile("watch"))
                        if len(ypage) == 0:
                            film.youtube = "https://www.youtube.com"
                        else:
                            film.youtube = "https://www.youtube.com" + \
                                           ypage[min(len(ypage) - 1, film.errors // 7)]["href"]

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
                    u.cms = 1
                    requests.patch(CONFIG["SERVER_URL"] + '/user', json={
                        "user_id": u.tel_id,
                        "sex": int(val)
                    })
                    bot.send_message(call.message.chat.id, START_ENTER_AGE_TEXT)
                if info == "age":
                    requests.patch(CONFIG["SERVER_URL"] + '/user', json={
                        "user_id": u.tel_id,
                        "age": int(val)
                    })
                try:
                    bot.edit_message_text(chat_id=call.message.chat.id,
                                          text="Ответ принят",
                                          message_id=call.message.message_id)
                except:
                    bot.delete_message(chat_id=call.message.chat.id,
                                       message_id=call.message.message_id)
                    bot.send_message(call.message.chat.id, "Ответ принят")
                u.save()

        except Exception as e:
            logger.error(e)

        try:
            bot.answer_callback_query(call.id, text=answer_callback_query)
        except:
            pass
        return True


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    u = Users.get_or_none(Users.tel_id == message.chat.id)
    if u == None:
        """the user is not in the database """
        bot.send_message(message.chat.id, "Вначале пройдите авторизацию, для этого отправьте команду /start")
        return

    logger.info(u.name + ": " + message.text)
    u.last_visit = datetime.now()

    if u.cms == 5:
        alarm(u.name + " need help: " + message.text)
        bot.send_message(message.chat.id, "Отзыв добавлен, мы рассмотрим его в ближайшее время",
                         reply_markup=base_keyboard_menu)
        u.cms = 2
        u.save()
        return

    if u.cms == 0:
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
        bot.send_message(message.chat.id, "Чтобы вернуться в главное меню отпрвьте команду /menu",
                         reply_markup=base_keyboard_search)
        u = next_film(u)
        u.cms = 3

    elif message.text == BTN_2_TEXT and u.cms == 2:
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = []

        liked = requests.get(CONFIG["SERVER_URL"] + '/user', params={
            "user_id": u.tel_id,
            "type": "get_liked",
        }).json()

        films = Films.select().where(Films.film_id.in_(liked)).execute()
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

        result = 0
        if message.text == BTN_S_SEARCH:
            result = -2
        elif message.text == BTN_1_SEARCH:
            result = -1
        elif message.text == BTN_2_SEARCH:
            result = 1
        elif message.text == BTN_3_SEARCH:
            result = 2

        requests.post(CONFIG["SERVER_URL"] + '/mark', json={
            "user_id": u.tel_id,
            "film_id": u.cfid,
            "result": result,
        })

        u = next_film(u, True)
        u.just_marked += 1
        bot.delete_message(chat_id=message.chat.id,
                           message_id=message.message_id)

    else:
        print("Unknown message")
        menu(message)
        bot.delete_message(chat_id=message.chat.id,
                           message_id=message.message_id)

    Messages.create(mes_id=str(message.chat.id) + "_" + str(message.message_id), text=message.text, user=u.tel_id,
                    btime=datetime.now())
    u.save()


if __name__ == '__main__':
    if "SERVER" in os.environ:
        logger.info("Starting on server 1.0")
    else:
        logger.info("DEBAG Starting")

    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logger.info(str(e))
