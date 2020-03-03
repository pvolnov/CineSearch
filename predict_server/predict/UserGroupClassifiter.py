import os
import sys
from collections import OrderedDict
import numpy as np
import peewee

from predict import logger, not_test, test

sys.path.append('../')
sys.path.append('./')
from playhouse.shortcuts import model_to_dict
from models import Users, Films, db

import xgboost as xgb
from catboost import Pool, CatBoostClassifier
import sklearn

PATH_TO_DIR = os.path.dirname(__file__) + "/"


class UserGroupClassifiter(object):

    def user_preparation(self, data: dict):
        """
        Transform the model into a feature vector for learning
        :param <User_fp.Model> as json:
        :return list of Int:
        """
        data = data.copy()

        del data["group"]
        del data["just_marked"]
        del data["predict_films"]
        del data["user_id"]
        del data["id"]

        msex = 0
        mage = 0
        myers = 0
        liked_films = Films.select().where(Films.film_id.in_(data["liked"] + data["viewed"])).execute()
        for f in liked_films:
            msex += f.sex
            mage += f.meanage
            myers += 2019 - f.year

        data["myers"] = myers / (len(liked_films) + 1)
        data["mage"] = mage / (len(liked_films) + 1)
        data["msex"] = msex / (len(liked_films) + 1)

        del data["viewed"]
        del data["disliked"]
        del data["liked"]

        vb = data["ganres"] + data["liked_vector"]
        del data["ganres"]
        del data["liked_vector"]
        del data["disliked_vector"]

        res = list(OrderedDict(data).values()) + vb
        return res

    def get_group(self, user: Users):
        """
        Recalculate user's group
        :param user:
        :return user class:
        """
        import os.path
        assert os.path.exists(PATH_TO_DIR + 'clustering'), "clustering model is not in catalog"
        assert isinstance(user, Users)

        import pickle
        with open(PATH_TO_DIR + "clustering", "rb") as f:
            clustering = pickle.load(f)

        ujson = model_to_dict(user)
        data = self.user_preparation(ujson)
        data = np.nan_to_num(data)
        result = clustering.predict([data])[0]
        return int(result)

    def upload_all_groups(self, ):
        """
        upload AffinityPropagation model for to define a users' group and updating all users
        :return None:
        """
        dataset = []
        users = []
        count = Users.select().count()
        for i in range(0, count, 100):
            usrs = Users.select().offset(i).limit(100).execute()
            for u in usrs:
                users.append(model_to_dict(u))

        for u in users:
            dataset.append(self.user_preparation(u))

        from sklearn.cluster import AffinityPropagation

        clustering = AffinityPropagation(affinity='euclidean', convergence_iter=15, copy=True,
                                         damping=0.5, max_iter=200, preference=None, verbose=False).fit(dataset)

        all_users = Users.select().execute()
        for u in all_users:
            u.group = self.get_group(u)

        with db.atomic() as txn:
            try:
                Users.bulk_update(all_users, fields=[Users.group])
            except peewee.Error as e:
                logger.error(str(e))
                db.rollback()

            @test
            def unsave():
                txn.rollback()

        @not_test
        def save():
            import pickle
            pickle.dump(clustering, open(PATH_TO_DIR + "clustering", "wb"))
