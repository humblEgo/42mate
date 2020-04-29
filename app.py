from slacker import Slacker
from flask import Flask, request, make_response
from flask_sqlalchemy import SQLAlchemy
import json
import os

from datetime import datetime
import requests
from blocks import get_command_view_blocks, get_base_blocks

token = os.environ['SLACK_TOKEN']
slack = Slacker(token)

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


from db_manage import join_user, create_user, unjoin_user, get_user_state, register_user, unregister_user

@app.route("/")
def hello():
    return "Hello! Let's test!"


def send_eph_message(form, command_time):
    slack_id = form.getlist('user_id')[0]
    call_channel = form.getlist('channel_id')
    if command_time.hour == 14 and command_time.minute > 42:
        #TODO HOUR TO 14, MINUTE TO 42
        eph_blocks = get_base_blocks("지금은 매칭을 준비중입니다.")
    else:
        eph_blocks = get_base_blocks("디엠을 확인해주세요!")
    slack.chat.post_ephemeral(channel=call_channel, text="", user=[slack_id], blocks=json.dumps(eph_blocks))


def send_direct_message(form):
    slack_id = form.getlist('user_id')[0]
    user_name = form.getlist('user_name')[0]
    user_state = get_user_state(slack_id)
    blocks = get_command_view_blocks(user_state)
    response = slack.conversations.open(users=[slack_id], return_im=True)
    dm_channel = response.body['channel']['id']
    if user_state is None:  # 처음 등록했을 경우
        create_user(slack_id, user_name)
    slack.chat.post_message(channel=dm_channel, blocks=json.dumps(blocks))


@app.route("/slack/command", methods=['POST'])
def command_main():
    command_time = datetime.utcnow()
    send_eph_message(request.form, command_time)
    if not (command_time.hour == 14 and command_time.minute > 42):
        # TODO HOUR TO 14, MINUTE TO 42
        send_direct_message(request.form)
    return ("", 200)


@app.route("/slack/callback", methods=['POST'])
def command_callback():
    data = json.loads(request.form['payload'])
    action_time = datetime.utcfromtimestamp(int(float(data['actions'][0]['action_ts'])))
    # 23시 42분 ~ 24시 사이에 callback할 경우 별도 event 없이 return 합니다.
    if (action_time.hour == 14):
        if (action_time.minute > 42):
            return ("", 200)
    user_slack_id = data['user']['id']
    user_action = data['actions'][0]
    if user_action['value'] == 'register':
        register_user(user_slack_id)
    elif user_action['value'] == 'unregister':
        unregister_user(user_slack_id)
    elif user_action['value'] == 'join':
        join_user(user_slack_id)
    elif user_action['value'] == 'unjoin':
        unjoin_user(user_slack_id)
    channel = data['channel']['id']
    # 한글에 markdown 적용하는 방법 확인
    success_message = get_base_blocks(user_action['value'] + "가 성공적으로 수행되었습니다!")

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

