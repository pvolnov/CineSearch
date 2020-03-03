from models import *


class Users(Model):
    user_id = IntegerField(index=True, null=False)
    age = IntegerField(default=20)
    sex = IntegerField(default=0)

    ganres = ArrayField(FloatField, default=[])
    group = IntegerField(default=-1)
    mark_wight = FloatField(default=0)
    just_marked = IntegerField(default=1)

    liked = ArrayField(IntegerField, default=[])
    viewed = ArrayField(IntegerField, default=[])
    disliked = ArrayField(IntegerField, default=[])

    disliked_vector = ArrayField(FloatField, default=[])
    liked_vector = ArrayField(FloatField, default=[])

    predict_films = ArrayField(IntegerField, default=[])

    class Meta:
        database = db
        db_table = 'Users_fp'