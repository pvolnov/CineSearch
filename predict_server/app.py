import logging
import os
from threading import Thread

import requests
from sanic import Sanic, response
from sanic.server import HttpProtocol
from sanic.response import text
from Headers.MarkHandler import MarkHandler
from Headers.UserHandler import UserHandler
from config import ALARMER
from predict.FilmMarksRegression import FilmMarksRegression
from predict.UserGroupClassifiter import UserGroupClassifiter

filename = None
log_level = logging.INFO
if "SERVER" in os.environ:
    filename = "predserver.log"
    log_level = logging.INFO

logging.basicConfig(format=u'[LINE:%(lineno)d] #%(name)s %(levelname)s [%(asctime)s]: %(message)s',
                    level=log_level,
                    filename=filename
                    )

logger = logging.getLogger("server")
app = Sanic('mbk server 1.2')

app.add_route(MarkHandler.as_view(), '/mark')
app.add_route(UserHandler.as_view(), '/user')


class CustomHttpProtocol(HttpProtocol):

    def __init__(self, *, loop, request_handler, error_handler,
                 signal, connections, request_timeout, request_max_size):
        super().__init__(
            loop=loop, request_handler=request_handler,
            error_handler=error_handler, signal=signal,
            connections=connections, request_timeout=request_timeout,
            request_max_size=request_max_size)

    def write_response(self, response):
        if isinstance(response, str):
            response = text(response)
        self.transport.write(
            response.output(self.request.version)
        )
        self.transport.close()


@app.route("/")
async def route(request):
    return response.text("Server is running")

@app.route("/update_classifiter")
async def route(request):
    def lern():
        r = FilmMarksRegression().update_model()
        requests.get("https://alarmerbot.ru/?key={}&message= ".format(ALARMER) + "New score: "+str(r))

        UserGroupClassifiter().upload_all_groups()
        requests.get("https://alarmerbot.ru/?key={}&message= ".format(ALARMER) + "All groups aploaded")

    Thread(target=lern(), daemon=True).start()
    return response.text("Updating is running ")

if __name__ == '__main__':
    SERVER_PORT = 9091
    if "SERVER" in os.environ:
        app.run(host="0.0.0.0", port=SERVER_PORT, debug=False)
        logger.info("Run on server")
    else:
        app.run(host="localhost", port=SERVER_PORT, debug=False)
        logger.info("Run debag mode")
