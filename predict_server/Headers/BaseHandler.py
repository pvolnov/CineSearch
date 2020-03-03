from playhouse.shortcuts import model_to_dict
from sanic import response
from sanic.views import HTTPMethodView


from models.Users import Users
from Headers import *


class BaseHandler(HTTPMethodView):

    def options(self,request):
        r =  response.text("")
        r.headers['Access-Control-Allow-Origin'] = "*"
        # response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        r.headers['Access-Control-Allow-Headers'] = '*, content-type'
        r.headers['Access-Control-Allow-Credentials'] = "true"
        r.headers["Access-Control-Allow-Methods"] = "POST, PUT, GET, OPTIONS, DELETE, PATCH"
        return r
