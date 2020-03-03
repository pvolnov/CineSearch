from playhouse.shortcuts import model_to_dict
from sanic import response

from Headers import logger, test, not_test
from Headers.BaseHandler import BaseHandler
from config import GANRES_LENGHT
from models import db, Films
from models.Users import Users
from predict.UserGroupClassifiter import UserGroupClassifiter
from predict.get_predict import get_predict


class UserHandler(BaseHandler):

    def get(self, request):

        r = {}
        for k in request.args:
            r[k] = request.args[k][0]

        assert "user_id" in r
        assert "type" in r

        if r["type"] == "get_predict":
            if "predict_size" in r:
                count = int(r["predict_size"])
            else:
                count = 1

            user = Users.get(Users.user_id == r["user_id"])
            predict = user.predict_films

            if len(predict) < count:
                predict += get_predict(user, 20)

            with db.atomic() as txn:
                user.predict_films = predict[count:]
                user.save()

                @test
                def not_save():
                    txn.rollback()

            return response.json(predict[:count])

        elif r["type"] == "get_liked":
            user = Users.get(Users.user_id == r["user_id"])
            return response.json(user.liked)
        else:
            response.text("error")

    def post(self, request):
        r = request.json
        assert "user_id" in r

        r["ganres"] = [0 for _ in range(GANRES_LENGHT)]

        @not_test
        def save():
            user = Users.create(**r)
            logger.info("New user FP: " + str(user.id))

        return response.text("ok")

    def patch(self, request):
        r = request.json
        assert "user_id" in r

        if "unliked_film_id" in r:
            user = Users.get(Users.user_id == r["user_id"])
            try:
                user.liked.remove(int(r["unliked_film_id"]))
            except:
                logger.error("FILM IS NOT IN USER LIKED")
                return response.text("film is not in user's liked")

            @not_test
            def save():
                user.save()
        else:
            @not_test
            def save():
                Users.update(r).where(Users.user_id == r["user_id"]).execute()

        return response.text("ok")


