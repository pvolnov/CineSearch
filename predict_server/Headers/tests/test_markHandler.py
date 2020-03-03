import os
from threading import Thread
from unittest import TestCase

import requests

from app import app
from models import Users, Films


class TestMarkHandler(TestCase):

    def setUp(self):
        os.environ.setdefault("TEST", "Handler")

        def run():
            app.run(host="localhost", port=9091, debug=True)

        Thread(target=run, daemon=True).start()

    def tearDownModule(self):
        os.environ.pop("TEST")
        app.stop()

    def test_post(self):
        u=Users.get()
        f=Films.get()
        r = requests.post('http://localhost:9091/mark', json={
            "user_id": u.user_id,
            "film_id": f.film_id,
            "result": 1,
        })
        self.assertEqual(r.text, "ok")

        r = requests.post('http://localhost:9091/mark', json={
            "film_id": f.film_id,
            "event": "trailer",
        })
        self.assertEqual(r.text, "ok")


