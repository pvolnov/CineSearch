import os
import unittest
from unittest import TestCase

from playhouse.shortcuts import model_to_dict

from models import Users, Films, db
from predict.FilmMarksRegression import FilmMarksRegression


class TestFilmMarksRegression(TestCase):
    def setUp(self):
        db.manual_commit()
        db.begin()
        os.environ.setdefault("TEST", "Predict")
        self.fm = FilmMarksRegression()

    def tearDownModule(self):
        db.rollback()
        db.close()
        os.environ.pop("TEST")

    def test_lite_data(self):
        u = Users.get()
        f = Films.get()
        res = self.fm.lite_data(model_to_dict(f), model_to_dict(u))
        self.assertIsInstance(res, list)
        self.assertIsInstance(res[0], float)

    def test_get_film_marks(self):
        u = Users.get()
        films = Films.select().limit(5).execute()
        films = [model_to_dict(f) for f in films]
        res = self.fm.get_film_marks(model_to_dict(u), films)
        self.assertEqual(len(films),len(res))

    @unittest.skip("lererning skipping")
    def test_update_model(self):
        self.fm.update_model()
        self.fail()
