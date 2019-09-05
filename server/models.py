# all security data

from peewee import *
from playhouse.postgres_ext import PostgresqlExtDatabase, JSONField
from playhouse.shortcuts import model_to_dict

from config import *

pg_db = PostgresqlExtDatabase(bdname, user=bduser, password=bdpassword,
                              host=bdhost, port=bdport)

model_to_dict
class People(Model):
    name = TextField(null=True)
    wiki = TextField(null=True)


class Comment(Model):
    autor = TextField(null=True)
    text = TextField(null=True)
    stars = IntegerField(default=0)


class Film(Model):
    name = TextField()
    avatar = TextField(null=True)
    country = IntegerField(null=True)
    starts = IntegerField(null=True)
    genre = IntegerField(null=True)
    duration = IntegerField(null=True)
    budget = IntegerField(null=True)
    profit = IntegerField(null=True)
    produser = ForeignKeyField(People)
    girector = ForeignKeyField(People)
    screenwriter = ForeignKeyField(People)

    auctors = JSONField(default=[])
    coments = JSONField(default=[])

    iviurl = TextField(null=True)
    kinourl = TextField(null=True)

    views = IntegerField(default=0)
    likes = IntegerField(default=0)
    dislikes = IntegerField(default=0)


    class Meta:
        database = pg_db

Film.create_table()