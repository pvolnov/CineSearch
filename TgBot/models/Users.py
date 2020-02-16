from peewee import IntegerField

from peewee import *
from config import *
from playhouse.postgres_ext import PostgresqlExtDatabase, JSONField, ArrayField

from models import db


class Users(Model):
    tel_id = IntegerField(index=True)
    vk_id = IntegerField(null=True,default=0)
    name = TextField(null=True)
    nicname = TextField(null=True)
    ustatus = IntegerField(default=0)
    info = JSONField(default={})
    last_visit = DateTimeField(null=True)
    just_marked = IntegerField(default=1)
    predict_films=ArrayField(IntegerField,default=[])

    cms = IntegerField(default=0)
    cfid = IntegerField(default=0)
    cfmes = IntegerField(default=0)
    ctmes = IntegerField(default=0)

    class Meta:
        database = db
        db_table = 'UsersTG'
