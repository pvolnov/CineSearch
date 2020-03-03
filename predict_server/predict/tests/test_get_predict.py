import os
from unittest import TestCase

from models import db


class TestGet_predict(TestCase):

    def setUp(self):
        # db.session_start()
        db.manual_commit()
        db.begin()
        os.environ.setdefault("TEST", "Predict")

    def tearDownModule(self):
        db.rollback()
        db.close()
        os.environ.pop("TEST")

    def test_get_predict(self):
        from models.Users import Users
        from predict.get_predict import get_predict

        user = Users.get()
        res = get_predict(user, n=10)

        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 10)
        self.assertIsInstance(res[0], int)
