from peewee import IntegerField

from peewee import *
from config import *
from playhouse.postgres_ext import PostgresqlExtDatabase, JSONField, ArrayField

from models import db


class Messages(Model):
    mes_id = TextField(unique=True)
    text = TextField(default="")
    reply_markup = JSONField(default={})
    user = IntegerField(default=0)
    btime = DateField(null=True)

    class Meta:
        database = db
        db_table='Messages'