# from models import Config
import os

TELEGRAM_TOKEN = "975424883:AAEJMK2C7U77zZ9NHBe4bl_M5M7wmUFBmtk"
ALAMER_KEY="df548f-61ac83-624ea4"
INVITE_PASS="csbeta4"


bdname='sinesearch_db'
bduser = 'postgres'
bdpassword = 'nef441'
bdhost = '51.79.69.179'
if "SERVER" in os.environ:
    bdhost = '127.0.0.1'

bdport = 5432
AUTO_KILL="aotokill556@admin"
#
# CONFIG={}
# for c in Config.select():
#     if c.value =="json":
#         CONFIG[c.name]=c.json
#     else:
#         CONFIG[c.name]=c.value
