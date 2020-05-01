from slacker import Slacker
from flask import Flask, request, make_response
from flask_sqlalchemy import SQLAlchemy
import json
import os

from datetime import datetime
import requests

token = os.environ['SLACK_TOKEN']
slack = Slacker(token)

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from blocks import get_command_view_blocks, get_base_blocks, get_eval_callback_blocks
from db_manage import join_user, create_user, unjoin_user, get_user_state, register_user, unregister_user, create_evaluation
from scheduled_actions import make_match

@app.route("/")
def hello():
    return "Hello! Let's test!"


def is_readytime():
    utctime = datetime.utcnow()
    if utctime.hour == 14 and utctime.minute > 42:
        # TODO HOUR TO 14, MINUTE TO 42
        return True
    return False


def send_eph_message(form, service_enable_time):
    slack_id = form.getlist('user_id')[0]
    call_channel = form.getlist('channel_id')
    if service_enable_time:
        eph_blocks = get_base_blocks("디엠을 확인해주세요!")
    else:
        eph_blocks = get_base_blocks("지금은 매칭을 준비중입니다.")
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
    form = request.form
    service_enable_time = not is_readytime()
    if service_enable_time:
        send_direct_message(form)
    if not(service_enable_time and form.getlist('channel_name')[0] == "directmessage"):
        send_eph_message(form, service_enable_time)
    return ("", 200)


def change_user_state_by_action(data):
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


def update_command_view(data, input_blocks_type, service_enable_time):
    ts = data['message']['ts']
    channel = data['channel']['id']
    user_action = data['actions'][0]
    if service_enable_time:
        if input_blocks_type == "command_view_blocks":
            update_blocks = get_base_blocks(user_action['value'] + "가 성공적으로 수행되었습니다!") #추후 get_cmnd_view_callback_blocks 로 변경 예정
        elif input_blocks_type == "evaluation_blocks":
            update_blocks = get_eval_callback_blocks(data)
    else:
        update_blocks = get_base_blocks("지금은 매칭을 준비중입니다.")
    slack.chat.update(channel=channel, ts=ts, text="edit-text", blocks=json.dumps(update_blocks))


@app.route("/slack/callback", methods=['POST'])
def command_callback():
    data = json.loads(request.form['payload'])
    input_blocks_type = data['actions'][0]['block_id']
    service_enable_time = not is_readytime()
    update_command_view(data, input_blocks_type, service_enable_time)
    if service_enable_time:
        if input_blocks_type == "command_view_blocks":
            change_user_state_by_action(data)
        elif input_blocks_type == "evaluation_blocks":
            create_evaluation(data)
    return ("", 200)


@app.route("/testmatch", methods=['GET'])
def testmatch():
    make_match()
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

