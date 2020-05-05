from slacker import Slacker
from flask import Flask, request, make_response
from flask_sqlalchemy import SQLAlchemy
import json
import os
from datetime import datetime

token = os.environ['SLACK_TOKEN']
slack = Slacker(token)

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from blocks import get_command_view_blocks, get_base_blocks, get_base_context_blocks, get_info_blocks
from db_manage import join_user, create_user, unjoin_user, get_user_state, register_user, unregister_user, update_evaluation, is_overlap_evaluation,  get_user_info, get_user_record

@app.route("/")
def hello():
    return "Hello! Let's test!"


def is_readytime():
    utctime = datetime.utcnow()
    if utctime.hour == 14 and utctime.minute >= 42:
        # TODO HOUR TO 14, MINUTE TO 42
        return True
    return False


def send_eph_message(form, service_enable_time):
    slack_id = form.getlist('user_id')[0]
    call_channel = form.getlist('channel_id')
    if service_enable_time:
        eph_blocks = get_base_context_blocks("메시지가 전송되었습니다. Apps에서 '42mate'를 확인해주세요!")
    else:
        eph_blocks = get_base_context_blocks("매칭 준비중입니다. 12시 이후에 다시 시도해주세요.")
    slack.chat.post_ephemeral(channel=call_channel, text="", user=[slack_id], blocks=json.dumps(eph_blocks))


def send_direct_message(user_info):
    info_blocks = get_info_blocks(user_info)
    command_view_blocks = get_command_view_blocks(user_info)
    blocks = info_blocks + command_view_blocks
    response = slack.conversations.open(users=[user_info['slack_id']], return_im=True)
    dm_channel = response.body['channel']['id']
    slack.chat.post_message(channel=dm_channel, blocks=json.dumps(blocks))


@app.route("/slack/command", methods=['POST'])
def command_main():
    form = request.form
    channel_name = form.getlist('channel_name')[0]
    service_enable_time = not is_readytime()
    if service_enable_time:
        user = get_user_record(form)
        if user is None:
            user = create_user(form)
        user_info = get_user_info(user)
        send_direct_message(user_info)
    if channel_name != "directmessage" and channel_name != "privategroup":
        send_eph_message(form, service_enable_time)
    return ("", 200)


def update_user(data):
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


def callback_command_view_message(user_action):
    update_message = "적용되었습니다."
    if user_action == 'join':
        update_message += " " + "내일의 메이트는 자정 12시에 공개됩니다."
    elif user_action == 'unjoin':
        update_message += " " + "오후 11시 42분까지 다시 신청이 가능합니다."
    elif user_action == 'register':
        update_message += " " + "오후 11시 42분까지 메이트 신청이 가능합니다."
    elif user_action == 'unregister':
        update_message += " " + "언제라도 다시 돌아올 수 있습니다."
    return update_message


def callback_invitation_mesasge(user_action):
    update_message = "적용되었습니다."
    if user_action == 'join':
        update_message += " " + "내일의 메이트는 자정 12시에 공개됩니다."
    elif user_action == 'unjoin':
        update_message += " " + "오후 11시 42분까지 다시 신청이 가능합니다."
    return update_message


def callback_evaluation_message(input_blocks_type):
    if is_overlap_evaluation(input_blocks_type):
        update_message = "오늘의 설문에 대해 이미 응답하셨습니다."
    else:
        update_message = "응답해주셔서 감사합니다."
    return update_message


def get_update_message(data):
    user_action = data['actions'][0]['value']
    input_blocks_type = data['actions'][0]['block_id']
    if input_blocks_type == "command_view_blocks":
        update_message = callback_command_view_message(user_action)
    elif input_blocks_type == "invitation_blocks":
        update_message = callback_invitation_mesasge(user_action)
    elif input_blocks_type.startswith("evaluation_blocks"):
        update_message = callback_evaluation_message(input_blocks_type)
    return update_message


def update_command_view(data, service_enable_time):
    ts = data['message']['ts']
    channel = data['channel']['id']
    if service_enable_time:
        update_message = get_update_message(data)
    else:
        update_message = "매칭 준비중입니다. 12시 이후에 다시 시도해주세요."
    blocks = get_base_context_blocks(update_message)
    slack.chat.update(channel=channel, ts=ts, text="edit-text", blocks=json.dumps(blocks))


def update_database(data):
    input_blocks_type = data['actions'][0]['block_id']
    if input_blocks_type in ["command_view_blocks", "invitation_blocks"]:
        update_user(data)
    elif input_blocks_type.startswith("evaluation_blocks"):
        update_evaluation(data)


@app.route("/slack/callback", methods=['POST'])
def command_callback():
    data = json.loads(request.form['payload'])
    service_enable_time = not is_readytime()
    update_command_view(data, service_enable_time)
    if service_enable_time:
        update_database(data)
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

