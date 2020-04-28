from slacker import Slacker
from flask import Flask, request, make_response
from flask_sqlalchemy import SQLAlchemy
import json
import os

from datetime import datetime
from pytz import timezone
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
    return "Hello! Let's test!"


def register(slack_id, intra_id):
    try:
        user=User(
            slack_id=slack_id,
            intra_id=intra_id,
        )
        db.session.add(user)
        db.session.commit()
        return "Success"
    except Exception as e:
            return(str(e))


def get_blocks(value):
    register_action = {
        "type": "button",
        "text": {
            "type": "plain_text",
            "text": "42mate 등록하기"
        },
        "style": "primary",
        "value": "register"
    }

    join_action = {
        "type": "button",
        "text": {
            "type": "plain_text",
            "text": "내일 만나기"
        },
        "style": "primary",
        "value": "join"
    }

    unjoin_action = {
        "type": "button",
        "text": {
            "type": "plain_text",
            "text": "내일 만나지 않기"
        },
        "style": "danger",
        "value": "unjoin"
    }

    unregister_action = {
        "type": "button",
        "text": {
            "type": "plain_text",
            "text": "42mate 휴식하기"
        },
        "style": "danger",
        "value": "unregister",
        "confirm": {
            "title": {
                "type": "plain_text",
                "text": "정말 휴식하시겠어요?"
            },
            "text": {
                "type": "mrkdwn",
                "text": "언제라도 다시 돌아오세요"
            },
            "confirm": {
                "type": "plain_text",
                "text": "휴식하기"
            },
            "deny": {
                "type": "plain_text",
                "text": "더 생각해보기"
            }
        }
    }
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "42MATE에 오신걸 환영합니다!!"
            }
        }
    ]
    actions = {
        "type": "actions",
        "elements": []
    }

    if value == "register" or value == "registered" or value is None:
        actions['elements'] = [join_action, unregister_action]
    elif value == "join" or value == "joined":
        actions['elements'] = [unjoin_action, unregister_action]
    elif value == "unjoin" or value == "unjoined":
        actions['elements'] = [join_action, unregister_action]
    elif value == "unregister" or value == "unregistered":
        actions['elements'] = [register_action]

    blocks.append(actions)

    return json.dumps(blocks)


def get_user_state(slack_id):
    if isinstance(slack_id, list):
        slack_id = slack_id[0]
    user = User.query.filter_by(slack_id=slack_id).first()
    if user is None:
        return None
    if user.register is True:
        if user.joined is True:
            return "joined"
        else:
            return "unjoined"
    else:
        return "unregistered"


@app.route("/slack/command", methods=['POST'])
def command_view():
    slack_id = request.form.getlist('user_id')
    user_name = request.form.getlist('user_name')

    user_state = get_user_state(slack_id)
    blocks = get_blocks(user_state)
    response = slack.conversations.open(users=slack_id, return_im=True)
    channel = response.body['channel']['id']
    if user_state is None:  # 처음 등록했을 경우
        register(slack_id[0], user_name[0])
    slack.chat.post_message(channel=channel, blocks=blocks)
    return ("", 200)


@app.route("/test/make_match")
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
        utc = match.match_day
        return str(utc.astimezone(timezone(os.environ['TIME_ZONE'])))
    except Exception as e:
            return(str(e))


@app.route("/test/match_list")
def match_list():
    match = Match.query.all()[0]
    print(match.users)
    return (match.users, 200)


@app.route("/slack/callback", methods=['POST'])
def command_callback():
    data = json.loads(request.form['payload'])
    action_time = datetime.utcfromtimestamp(int(float(data['actions'][0]['action_ts'])))
    # 23시 42분 ~ 24시 사이에 callback할 경우 별도 event 없이 return 합니다.
    if (action_time.hour == 14):
        if (action_time.minute > 42):
            return ("", 200)
    user_id = data['user']['id']
    user_name = data['user']['username']
    user_action = data['actions'][0]
    if user_action['value'] == 'register':
        register(user_id, user_name)
    #elif user_action['value'] == 'unregister':
    #    unregister_user(user_id)
    # elif user_action['value'] == 'join':
    #      join_user(user_id)
    #elif user_aciton['value'] == 'unjoin':
    #    unjoin_user(user_id)
    channel = data['channel']['id']
    # 한글에 markdown 적용하는 방법 확인
    success_message = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": user_action['value'] + "가 *성공*적으로 수행되었습니다!"
            }
        }
    ]
    ts = data['message']['ts']
    slack.chat.update(channel=channel, ts=ts, text="edit-text", blocks=json.dumps(success_message))
    return ("", 200)


if __name__ == "__main__":
    app.run()

#슬랙 event subscriber
# @app.route("/slack/command", methods=["GET", "POST"])
# def hears():
#      slack_event = json.loads(request.data)
#      if "challenge" in slack_event:
#          return make_response(slack_event["challenge"], 200,
#                               {"content_type": "application/json"})
#      if "event" in slack_event:
#          event_type = slack_event["event"]["type"]
#          return event_handler(event_type, slack_event)
#      return make_response("슬랙 요청에 대한 이벤트가 없습니다.", 404,
#                           {"X-Slack-No-Retry": 1})

