
from peewee import *
from config import *
from playhouse.postgres_ext import PostgresqlExtDatabase, JSONField, ArrayField

db = PostgresqlExtDatabase(bdname, user=bduser, password=bdpassword,
                           host=bdhost, port=bdport)
class Users(Model):
    tel_id=IntegerField(index=True)
    name = TextField()
    nicname = TextField(null=True)
    ustatus=IntegerField(default=0)
    info=JSONField(default={})

    cms=IntegerField(default=0)
    cfid=IntegerField(default=0)
    cfmes=IntegerField(default=0)
    ctmes=IntegerField(default=0)
    liked=ArrayField(IntegerField,default=[])
    viewed=ArrayField(IntegerField,default=[])
    disliked=ArrayField(IntegerField,default=[])
    predict_films=ArrayField(IntegerField,default=[])
    selections=JSONField(default={})

    class Meta:
        database = db
        db_table='Users'

class Films(Model):
    film_id=IntegerField(unique=True,index=True)
    name = TextField()
    discr = TextField(null=True)
    img = TextField(null=True)
    youtube=TextField(default="")
    stars = FloatField(default=0)
    info=JSONField(default={})
    selections=ArrayField(IntegerField,default=[])
    likes=IntegerField(default=0)
    dislikes=IntegerField(default=0)

    class Meta:
        database = db
        db_table='Films'

class Selections(Model):
    name = TextField()
    user_id = IntegerField(default=0)
    stars = FloatField(default=0)
    films = ArrayField(IntegerField,default=[])

    class Meta:
        database = db
        db_table='Selections'

# Selections.drop_table()
# Films.drop_table()
# Users.drop_table()

Selections.create_table()
Films.create_table()
Users.create_table()

