import math
import os
from collections import OrderedDict

from playhouse.shortcuts import model_to_dict

from models import Films, Users, Dataset
from predict import not_test

import xgboost as xgb
from catboost import Pool, CatBoostClassifier
import sklearn

PATH_TO_DIR = os.path.dirname(__file__) + "/"
MODEL = "clf"


class FilmMarksRegression(object):

    @staticmethod
    def dotproduct(v1, v2):
        return sum((a * b) for a, b in zip(v1, v2))

    @staticmethod
    def length(v):
        return math.sqrt(FilmMarksRegression.dotproduct(v, v))

    @staticmethod
    def cos(v1, v2):
        l = FilmMarksRegression.length(v1) * FilmMarksRegression.length(v2)
        if l == 0:
            return 0
        return FilmMarksRegression.dotproduct(v1, v2) / l

    @staticmethod
    def filtr(dataset):
        dat = []
        all_users = {}
        # load films from db
        films = {}
        count = Films.select().count()
        for i in range(0, count, 500):
            data = Films.select().order_by(Films.id).offset(i).limit(500).execute()
            for d in data:
                films[d.film_id] = model_to_dict(d)

        # load users from db
        count = Users.select().count()
        users = {}
        for i in range(0, count, 200):
            data = Users.select().order_by(Users.id).offset(i).limit(200).execute()
            for d in data:
                users[d.user_id] = model_to_dict(d)

        # preparing dataset
        for d in dataset:
            limit = 100
            res = {}

            uid = d["user_value"]["tel_id"] if "tel_id" in d["user_value"] else d["user_value"]["user_id"]
            if uid in all_users:
                all_users[uid] += 1
                if all_users[uid] > limit:
                    continue
            else:
                all_users[uid] = 1

            res["user"] = users[uid]
            res["film"] = films[d["film_value"]["film_id"]]

            res["result"] = d["result"]
            dat.append(res)
        return dat

    def lite_data(self, film: dict, user: dict):
        """
        Combines 2 models into a list of key features
        :param film: <Film_fp.Model> as json
        :param user: <User_fp.Model> as json
        :return: list of Float
        """
        assert isinstance(film, dict), "Film is not a dict"
        assert isinstance(user, dict), "Film is not a dict"

        data = {}
        data["gcos"] = FilmMarksRegression.cos(film["ganres"], user["ganres"])
        data["vcos"] = FilmMarksRegression.cos(film["vector"], user["liked_vector"])
        data["dcos"] = FilmMarksRegression.cos(film["vector"], user["disliked_vector"])

        data["year"] = 2019 - film["year"]
        data["meanage"] = abs(film["meanage"] - user["age"])
        data["sex"] = abs(film["sex"] - user["sex"])

        data["likes"] = film["likes"] / (film["marks"] + 1)
        data["dislikes"] = film["dislikes"] / (film["marks"] + 1)
        data["shit"] = film["shit"] / (film["marks"] + 1)
        data["opening"] = film["opening"] / (film["marks"] + 1)
        data["count_triler"] = film["count_triler"] / (film["marks"] + 1)
        data["stars"] = film["stars"]

        res = list(OrderedDict(data).values())
        return [float(i) for i in res]

    def full_data(self, film: dict, user: dict):
        data = {}
        data["gcos"] = self.cos(film["ganres"], user["ganres"])
        data["vcos"] = self.cos(film["vector"], user["liked_vector"])
        data["dcos"] = self.cos(film["vector"], user["disliked_vector"])

        data["year"] = 2019 - film["year"]
        data["meanage"] = abs(film["meanage"] - user["age"])
        data["sex"] = abs(film["sex"] - user["sex"])

        data["likes"] = film["likes"] / (film["marks"] + 1)
        data["dislikes"] = film["dislikes"] / (film["marks"] + 1)
        data["shit"] = film["shit"] / (film["marks"] + 1)
        data["opening"] = film["opening"] / (film["marks"] + 1)
        data["count_triler"] = film["count_triler"] / (film["marks"] + 1)
        data["stars"] = film["stars"]

        res = list(OrderedDict(data).values())

        #     res+=(dis(film["vector"],user["liked_vector"]))

        res += (film["ganres"]) + (user["ganres"])

        return [float(i) for i in res]

    def get_film_marks(self, u: dict, films: list):
        """
        Marks incoming movies by returning a "similarity" array corresponding to the incoming list
        function return array "similarity and user" from the list of movies.
        :param u: user as json
        :param films: list of <Film_fp.Model> in json format
        :return: list of Float
        """
        import os.path
        assert os.path.exists(PATH_TO_DIR + 'model'), "user-film clustering model is not in catalog"

        import pickle
        with open(PATH_TO_DIR + "model", "rb") as f:
            model = pickle.load(f)

        data = []
        for f in films:
            data.append(self.full_data(f, u))

        pred = model.predict_proba(data)[:, 1]
        return pred

    def update_model(self):
        """
        Update XGboost model (gbm), using relevant data.
        This function using model Films and Users, please don't change their.
        :return: accuracy of the new model
        """

        # load the list of users
        count = Users.select().count()
        users = []
        for i in range(0, count, 100):
            usrs = Users.select().offset(i).limit(100).execute()
            for u in usrs:
                users.append(model_to_dict(u))

        # collect dataset
        dataset = []
        for i in range(0, count, 200):
            data = Dataset.select().order_by(Dataset.id).offset(i).limit(200).execute()
            for d in data:
                dataset.append(model_to_dict(d))
        dataset = self.filtr(dataset)
        dataset = [{
            "data": self.full_data(d["film"], d["user"]),
            "result": d["result"]} for d in dataset]

        X = [d["data"] for d in dataset]
        Y = [int(d["result"] > 0) for d in dataset]

        from sklearn.preprocessing import normalize
        X = normalize(X)

        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.1, random_state=42)

        # learning new model
        if MODEL == "gbm":
            model = xgb.XGBClassifier(max_depth=7,
                                      n_estimators=1600,
                                      learning_rate=0.01,
                                      subsample=0.3,
                                      #                         gamma = 300,
                                      colsample_bytree=0.3).fit(X_train, y_train)

        else:
            pool = Pool(X_train, y_train)
            model = CatBoostClassifier(iterations=1600,
                                       learning_rate=0.01,
                                       depth=5,
                                       random_seed=7)
            model.fit(pool)

        @not_test
        def save():  # save model
            import pickle
            pickle.dump(model, open(PATH_TO_DIR + "model", "wb"))

        # compute accuracy
        predictions = model.predict_proba(X_test)[:, 1]
        from sklearn.metrics import roc_auc_score
        test = roc_auc_score(predictions > 0.5, y_test)

        return test
