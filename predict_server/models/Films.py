from models import *


class Films(Model):
    id = IdentityField()
    film_id = IntegerField(unique=True, index=True)
    stars = FloatField(default=0)
    level = IntegerField(default=0)
    year = IntegerField(default=2000)
    vector = ArrayField(FloatField, default=[])

    ganres = ArrayField(FloatField, default=[])
    meanage = FloatField(default=20)
    sex = FloatField(default=0.5)

    likes = IntegerField(default=10)
    dislikes = IntegerField(default=10)
    shit = IntegerField(default=0)
    marks = IntegerField(default=0)

    errors = IntegerField(default=0)
    opening = IntegerField(default=0)
    count_triler = IntegerField(default=0)

    class Meta:
        database = db
        db_table = 'Films_fp'
