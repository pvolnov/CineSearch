
from peewee import *
from config import *
from playhouse.postgres_ext import PostgresqlExtDatabase, JSONField, ArrayField

db = PostgresqlExtDatabase(bdname, user=bduser, password=bdpassword,
                           host=bdhost, port=bdport)
class Users(Model):
    tel_id=IntegerField(index=True)
    vk_id=IntegerField()
    name = TextField()
    nicname = TextField(null=True)
    ustatus=IntegerField(default=0)
    age=IntegerField(default=20)
    sex=IntegerField(default=0)
    ganres=JSONField(default={})
    group=IntegerField(default=-1)
    info=JSONField(default={})
    last_visit=DateField(null=True)
    mark_wight=FloatField(default=0)
    just_marked = IntegerField(default=1)

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
    level=IntegerField(default=0)
    selections=ArrayField(IntegerField,default=[])
    year=IntegerField(default=2000)

    ganres=ArrayField(IntegerField,default=[])
    meanage=FloatField(default=20)
    sex=FloatField(default=0.5)

    likes=IntegerField(default=10)
    dislikes=IntegerField(default=10)
    shit=IntegerField(default=0)
    errors=IntegerField(default=0)
    opening=IntegerField(default=0)
    treilers=IntegerField(default=0)

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

class Messages(Model):
    mes_id = TextField(unique=True)
    text = TextField(default="")
    reply_markup = JSONField(default={})
    user = IntegerField(default=0)
    btime = DateField(null=True)

    class Meta:
        database = db
        db_table='Messages'

class Config(Model):
    name = TextField()
    value = TextField()
    json=JSONField(default={})

    class Meta:
        database = db
        db_table='Config'

class Dataset(Model):
    user_value = JSONField()
    film_value = JSONField()
    result = IntegerField(default=0)
    data = DateField()

    class Meta:
        database = db
        db_table='Dataset'

# Selections.drop_table()
# Films.drop_table()
# Users.drop_table()
# Config.drop_table()
# Messages.drop_table()


Selections.create_table()
Films.create_table()
Users.create_table()
Config.create_table()
Messages.create_table()
Dataset.create_table()

