from peewee import IntegerField

from peewee import *
from config import *
from playhouse.postgres_ext import PostgresqlExtDatabase, JSONField, ArrayField

from models import db


class Films(Model):
    film_id = IntegerField(unique=True, index=True)
    name = TextField()
    discr = TextField(null=True)
    img = TextField(null=True)
    youtube = TextField(default="")
    stars = FloatField(default=0)
    info = JSONField(default={})
    treilers = IntegerField(default=0)

    class Meta:
        database = db
        db_table = 'Films_fw'


# print(Films.select(fn.array_length(Films.info,0)).where(Films.id<2).execute())
