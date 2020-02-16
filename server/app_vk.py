import logging
import os
import re
import sys
import warnings
from datetime import datetime

import requests

sys.path.append('../')
sys.path.append('./')

import config
import json
import vk
from flask import Flask, request
from vk_api.keyboard import VkKeyboard
import  time
warnings.simplefilter('ignore')
from models import *
import httplib2

CONFIG = {
    'CONFORMATION_TOKEN': '660117c3',
    'VK_TOKEN': '2e8b7f2be8fa24d73731028d9627e5ef5822b50253aa2a84161fd9ee9b9ea435b48903292be36be70ea53',
    "ALAMER_KEY": "df548f-61ac83-624ea4",
    "IDENT_REFIX":"#42621"
}
filename = None
if "SERVER" in os.environ:
    filename = "bot.log"

logging.basicConfig(format=u'[LINE:%(lineno)d] # %(levelname)s [%(asctime)s]: %(message)s', level=logging.INFO,
                    filename=filename
                    )
logger = logging.getLogger("cs")

app = Flask(__name__)
session = vk.Session(CONFIG['VK_TOKEN'])
api = vk.API(session, v=5.69)




def alarm(text):
    logger.info(text)
    requests.get("https://alarmerbot.ru/?key={}&message= ".format(CONFIG["ALAMER_KEY"]) + str(text))


@app.route('/')
def hello_world():
    return 'CS server bot 1.1'




@app.route('/', methods=['POST'])
def processing():
    # Распаковываем json из пришедшего POST-запроса

    data = json.loads(request.data)

    if 'type' not in data.keys():
        return 'not vk'

    if data['type'] == 'confirmation':
        return CONFIG['CONFORMATION_TOKEN']


    if 'user_id' in data['object']:
        user_id = data['object']['user_id']
    else:
        user_id = data['object']['from_id']

    if data['type'] == 'message_new':
        try:
            text = data['object']['body']
            logger.info(text)
            if text.find(CONFIG["IDENT_REFIX"])>-1:
                uid=int(text.replace(CONFIG["IDENT_REFIX"],""))
                logger.info("ID: "+str(uid))
                u = Users.get_by_id(uid)

                user = api.users.get(user_id=user_id, v='5.92', fields="sex,photo_200,contacts,bdate")[0]
                name=str(user["first_name"])+" "+str(user["last_name"])
                u.vk_id=user_id
                u.save()
                api.messages.send(user_id=user_id, message="Авторизация пройдена, нажмите в боте 'Проверить' ", random_id=int(time.time()) )
                alarm(name+" прошел авторизацию")
                return 'ok'

        except Exception as e:
            logger.info("Error "+str(e))
            pass

    api.messages.send(user_id=user_id, message="Я не отвечаю на сообщения", random_id=int(time.time()))

    return 'ok'


if __name__ == '__main__':
    port = os.environ.get('PORT', 5000)
    app.run(host='0.0.0.0', port=port)
    # app.run(host='127.0.0.1', port=port, debug=True)
