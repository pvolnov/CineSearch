import os
from threading import Thread
from unittest import TestCase

import requests
from app import app

from models import db, Users


class TestUserHandler(TestCase):
    def setUp(self):
        os.environ.setdefault("TEST", "Handler")

        def run():
            app.run(host="localhost", port=9091, debug=True)

        Thread(target=run, daemon=True).start()

    def tearDownModule(self):
        os.environ.pop("TEST")

    def test_get(self):
        r = requests.get('http://localhost:9091/user', params={
            "user_id": 542373574,
            "type": "get_predict",
            "predict_size": 1
        })
        self.assertIsInstance(r.json(), list)

        r = requests.get('http://localhost:9091/user', params={
            "user_id": 542373574,
            "type": "get_liked",
        })
        self.assertIsInstance(r.json(), list)

    def test_post(self):
        r = requests.post('http://localhost:9091/user', json={
            "user_id": 10000000,
        })
        self.assertEqual(r.text, "ok")

    def test_patch(self):
        u=Users.get()
        r = requests.patch('http://localhost:9091/user', json={
            "user_id": u.user_id,
            "unliked_film_id":u.liked[0]
        })
        self.assertEqual(r.text, "ok")