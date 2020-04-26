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
    dt_utc = datetime.now()
    dt_kst = datetime.now(timezone(os.environ['TIME_ZONE']))
    slack.chat.post_message("#bot-test", dt_utc)
    slack.chat.post_message("#bot-test", dt_kst)
    return "Compare between utc and kst"


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


#@app.route("/slack/command", methods=['POST'])
def command_view():
    slack_id = request.form.getlist('user_id')
    user_name = request.form.getlist('user_name')
    block_test = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "42MATE에 오신걸 환영합니다!!"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "42mate 등록하기"
                    },
                    "style": "primary",
                    "value": "register"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "내일 만나기"
                    },
                    "style": "primary",
                    "value": "join"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "내일 만나지 않기"
                    },
                    "style": "danger",
                    "value": "unjoin"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
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
            ]
        }
    ]
    block = json.dumps(block_test)
    response = slack.conversations.open(users=slack_id, return_im=True)
    channel = response.body['channel']['id']
    if User.query.filter_by(slack_id=slack_id[0]).count():
        slack.chat.post_message(channel=channel, text="re-visit text", blocks=block)
    else:
        register(slack_id[0], user_name[0])
        slack.chat.post_message(channel=channel, text="first-visit-text", blocks=block)
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
    ## 하단은 아직 조건문 밑에 수행될 함수가 구현되지 않아서 주석처리 해뒀습니다.
    # elif user_action['value'] == 'unregister':
    #      unregister_user(user_id)
    # elif user_action['value'] == 'join':
    #      join_user(user_id)
    # elif user_aciton['value'] == 'unjoin':
    #      unjoin_user(user_id)
    channel = data['channel']['id']
    # get_blocks함수가 구현되기 전이라 block_test함수를 하드코딩하여 테스트했습니다.
    # block = get_blocks(data)
    block_test = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "내일 매칭에 **참가**하셨습니다! 누구와 만나게 될까요~? :)"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "내일 만나지 않기"
                    },
                    "style": "danger",
                    "value": "unjoin"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
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
            ]
        }
    ]
    block = json.dumps(block_test)
    ts = data['message']['ts']
    slack.chat.update(channel=channel, ts=ts, text="edit-text", blocks=block)
    return ("", 200)


if __name__ == "__main__":
    app.run()

슬랙 event subscriber
@app.route("/slack/command", methods=["GET", "POST"])
def hears():
     slack_event = json.loads(request.data)
     if "challenge" in slack_event:
         return make_response(slack_event["challenge"], 200,
                              {"content_type": "application/json"})
     if "event" in slack_event:
         event_type = slack_event["event"]["type"]
         return event_handler(event_type, slack_event)
     return make_response("슬랙 요청에 대한 이벤트가 없습니다.", 404,
                          {"X-Slack-No-Retry": 1})

