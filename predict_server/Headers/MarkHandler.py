from datetime import datetime

from playhouse.shortcuts import model_to_dict
from sanic import response
from sanic.views import HTTPMethodView
import logging

from Headers import not_test
from Headers.BaseHandler import BaseHandler
from models.Dataset import Dataset
from models.Films import Films
from predict.UserGroupClassifiter import UserGroupClassifiter

logger = logging.getLogger("server")

from models.Users import Users


class MarkHandler(BaseHandler):

    def post(self, request):
        """
        Add new mark for user and recomute models
        Resalt:
            2 - like
            1 - viewed
            -1 - dislike
            -2 - shit
        :param request:
        :return:
        """
        r = request.json
        assert "film_id" in r
        film = Films.get_or_none(Films.film_id == r["film_id"])

        assert film is not None, "Film not found!"

        if "event" in r:
            event = r["event"]

            if event == "error":
                film.errors += 1
            elif event == "open":
                film.opening += 1
            elif event == "trailer":
                film.count_triler += 1
            else:
                return response.text("unknown event type")

            @not_test
            def save():
                film.save()

            return response.text("ok")

        assert "user_id" in r
        assert "result" in r
        user = Users.get(Users.user_id == r["user_id"])
        result = r["result"]

        if user.mark_wight is not None and user.just_marked is not None:
            mark_wight = 1.5 - user.mark_wight / 2
        else:
            user.mark_wight = 1
            mark_wight = 1

        if result > 0:
            film.meanage = film.meanage + (film.meanage - user.age) / (film.likes + 1)
            film.sex = film.sex + (film.sex - user.sex) / (film.likes + 1)
            film.likes += 1

            if result == 1:
                user.ganres = [x + y * 2 for x, y in zip(user.ganres, film.ganres)]
                film.stars = film.stars + ((10 - film.stars) * mark_wight) / (film.marks + 1)
                user.liked.append(film.film_id)

            if result == 2:
                user.ganres = [x + y for x, y in zip(user.ganres, film.ganres)]
                film.stars = film.stars + ((9 - film.stars) * mark_wight) / (film.marks + 1)
                user.viewed.append(film.film_id)

        if result < 0:
            if result == -1:
                user.ganres = [x + y * -1 for x, y in zip(user.ganres, film.ganres)]
                film.stars = film.stars + ((6 - film.stars) * mark_wight) / (film.marks + 1)
                user.disliked.append(film.film_id)
                film.dislikes += 1

            if result == -2:
                film.stars = film.stars + ((1 - film.stars) * mark_wight) / (film.marks + 1)
                user.disliked.append(film.film_id)
                film.shit += 1

        user.mark_wight = user.mark_wight + result / (user.just_marked + 1)
        user.just_marked += 1
        film.marks += 1

        import random
        a = random.random()
        if a < 0.15:
            user.group = UserGroupClassifiter().get_group(user)
        if a < 0.3:
            u = self.upload_users_vectors(model_to_dict(user))
            Users.update(**u).where(Users.user_id == u["user_id"]).execute()

        @not_test
        def save():
            Dataset.create(data=datetime.now(), user_value=model_to_dict(user),
                           film_value=model_to_dict(film), result=result)

            film.save()
            user.save()

        return response.text("ok")

    @staticmethod
    def upload_users_vectors(u: dict):
        """
        This function uploading like-dislike vector fot rhis user
        :param u:
        :return:
        """
        # assert not isinstance(u, <class dict> ), "User is not in dict format "+ str(type(u))
        import numpy as np

        fids = u["disliked"] + u["liked"]
        all_films = {f.film_id: model_to_dict(f) for f in Films.select().where(Films.film_id.in_(fids)).execute()}

        if len(u["disliked"]) == 0:
            u["disliked"].append(1900)
        vectors = []

        for f in u["disliked"]:
            vectors.append(all_films[f]["vector"])

        vectors = np.array(vectors)
        vectors = vectors.mean(axis=0)
        u["disliked_vector"] = vectors
        vectors = []
        for f in u["liked"]:
            vectors.append(all_films[f]["vector"])

        vectors = np.array(vectors)
        vectors = vectors.mean(axis=0)
        if isinstance(vectors, np.float64):
            vectors = [0 for i in range(len(u["disliked_vector"]))]
        u["liked_vector"] = vectors
        return u
