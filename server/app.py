from sanic import Sanic, Blueprint
from sanic.response import json, text, file

app = Sanic(__name__)
bp = Blueprint('film', url_prefix='/film')


@app.route("/")
async def test(request):
    return text("You are trying to create a user with the following POST: %s" % request.body)

@app.route('/favicon.ico')
async def handle_request(request):
    return await file('favicon.ico ')

@app.route("/film", methods=["POST", ])
def create_user(request):
    print(request)
    return json({"hello": "world"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, workers=4)
    # app.run(host="0.0.0.0", port=8000)
