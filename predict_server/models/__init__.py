import json

from peewee import *
from config import *
from playhouse.postgres_ext import PostgresqlExtDatabase, JSONField, ArrayField

db = PostgresqlExtDatabase(bdname, user=bduser, password=bdpassword,
                           host=bdhost, port=bdport, autoconnect=True, autorollback=True)


from models.Films import Films
from models.Users import Users
from models.Dataset import Dataset



# Films.create_table()
# Users.create_table()
# Dataset.create_table()