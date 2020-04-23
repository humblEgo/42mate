from slacker import Slacker
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import os

import requests

token = os.environ['SLACK_TOKEN']
slack = Slacker(token)

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import User, Match

@app.route("/")
def hello():
    slack.chat.post_message("#random", "Slacker test")
    return "Hello World!!"

@app.route("test/register/<id_>")
def register(id_):
    try:
        user=User(
            slack_id=id_,
            intra_id=id_,
        )
        db.session.add(user)
        db.session.commit()
        return "Success"
    except Exception as e:
            return(str(e))

@app.route("test/make_match")
def make_match():
    users = User.query.all()
    print(users)
    print(users[0])
    print(users[1])
    try:
        match=Match(
            user1 = users[0],
            user2 = users[1]
        )
        db.session.add(match)
        db.session.commit()
        return "Success"
    except Exception as e:
            return(str(e))

@app.route("test/match_list")
def match_list():
    match = Match.query.all()[0]
    print(match.users)
    return (match.users, 200)


#data = request.get_data()
@app.route("/slack/command", methods=['POST'])
def command_main():
    #data = request.form.getlist('text')
    #print(data)
    data = request.get_json(force=True)
    print(data['text'])
    # data = request.get_data()
    #text = data['text']
    #print(text)
    #command = parsing(text)

    command = parsing()
    if command == 'register':
        register(data)
    elif command == 'list':
        list

    return ('', 200)

if __name__ == "__main__":
    app.run()

#
# @app.route("/slack", methods=["GET", "POST"])
# def hears():
#     slack_event = json.loads(request.data)
#     if "challenge" in slack_event:
#         return make_response(slack_event["challenge"], 200,
#                              {"content_type": "application/json"})
#     if "event" in slack_event:
#         event_type = slack_event["event"]["type"]
#         return event_handler(event_type, slack_event)
#     return make_response("슬랙 요청에 대한 이벤트가 없습니다.", 404,
#                          {"X-Slack-No-Retry": 1})
