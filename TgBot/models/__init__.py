from peewee import *
from config import *
from playhouse.postgres_ext import PostgresqlExtDatabase, JSONField, ArrayField

db = PostgresqlExtDatabase(bdname, user=bduser, password=bdpassword,
                           host=bdhost, port=bdport)


from models.Config import Config
from models.Films import Films
from models.Messages import Messages
from models.Users import Users

# Config.create_table()
# Films.create_table()
# Messages.create_table()
# Users.create_table()