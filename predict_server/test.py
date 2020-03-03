import requests

from models import Users, Films

u=Users.get()
f=Films.get()

r = requests.post('http://localhost:9091/mark', json={
            "user_id": u.user_id,
            "film_id": f.film_id,
            "result": 1,
        })