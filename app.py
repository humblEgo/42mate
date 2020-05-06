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
from db_manage import join_user, create_user, unjoin_user, get_user_state, register_user, unregister_user, \
                      update_evaluation, is_overlap_evaluation, get_user_info, get_user_record

@app.route("/")
def ftmate_main_route():
    return "This is ftmate_main_route"


def is_readytime():
    """
    :return boolean: True if the current time is between 23:42 and 23:59 KST
    """
    utctime = datetime.utcnow()
    if utctime.hour == 14 and utctime.minute >= 42:
        # TODO HOUR TO 14, MINUTE TO 42
        return True
    return False


def send_guide_message(form):
    """
    send message that guide where to check direct message
    :param form: payload from slack slash command 
    """
    slack_id = form.getlist('user_id')[0]
    call_channel = form.getlist('channel_id')
    eph_blocks = get_base_context_blocks("메시지가 전송되었습니다. Apps에서 '42mate'를 확인해주세요!")
    slack.chat.post_ephemeral(channel=call_channel, text="", user=[slack_id], blocks=json.dumps(eph_blocks))


def send_direct_message(user_info):
    """
    send message that user's information and possible action buttons
    :param user_info: dictionary which contains user information
    """
    info_blocks = get_info_blocks(user_info)
    command_view_blocks = get_command_view_blocks(user_info)
    blocks = info_blocks + command_view_blocks
    response = slack.conversations.open(users=[user_info['slack_id']], return_im=True)
    dm_channel = response.body['channel']['id']
    slack.chat.post_message(channel=dm_channel, blocks=json.dumps(blocks))


def send_excuse_message(form):
    """
    send excuese message to called channel if called channel is public
    send excusse message to app channel if called channel is not public
    :param form: payload from slack slash command 
    """
    slack_id = form.getlist('user_id')[0]
    blocks = get_base_context_blocks("매칭 준비 중입니다. 자정 12시 이후에 다시 시도해주세요.")
    call_channel = form.getlist('channel_id')[0]
    if call_channel.startswith("C"):
        channel = call_channel
    else:
        response = slack.conversations.open(users=slack_id, return_im=True)
        channel = response.body['channel']['id']
    slack.chat.post_ephemeral(channel=channel, text="", user=[slack_id], blocks=json.dumps(blocks))


@app.route("/slack/command", methods=['POST'])
def command_main():
    """
    Send a response message according to the input time
    when entering 42mate command in Slack.
    :return: http 200 status code
    """
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
            send_guide_message(form, service_enable_time)
    else:
        send_excuse_message(form)
    return ("", 200)


def update_user(data):
    """
    :param data: payload from command callback
    """
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
    """
    :param user_action: 
    :return string: update message by user action
    """
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


def callback_invitation_message(user_action):
    """
    :param user_action: 
    :return string: update message by user action
    """
    update_message = "적용되었습니다."
    if user_action == 'join':
        update_message += " " + "내일의 메이트는 자정 12시에 공개됩니다."
    elif user_action == 'unjoin':
        update_message += " " + "오후 11시 42분까지 다시 신청이 가능합니다."
    return update_message


def callback_evaluation_message(input_blocks_type):
    """
    :param input_blocks_type: 
    :return string: update message based on evaluation duplication
    """
    if is_overlap_evaluation(input_blocks_type):
        update_message = "이미 응답된 설문입니다."
    else:
        update_message = "응답해주셔서 감사합니다."
    return update_message


def get_update_message(data):
    """
    :param data: payload from command callback
    :return string: update message based on callback case
    """
    user_action = data['actions'][0]['value']
    input_blocks_type = data['actions'][0]['block_id']
    if input_blocks_type == "command_view_blocks":
        update_message = callback_command_view_message(user_action)
    elif input_blocks_type == "invitation_blocks":
        update_message = callback_invitation_message(user_action)
    elif input_blocks_type.startswith("evaluation_blocks"):
        update_message = callback_evaluation_message(input_blocks_type)
    return update_message


def update_command_view(data, service_enable_time):
    """
    update message based on whether current time is service enable time
    :param data: payload from command callback
    :param service_enable_time: boolean
    """
    ts = data['message']['ts']
    channel = data['channel']['id']
    if service_enable_time:
        update_message = get_update_message(data)
    else:
        update_message = "매칭 준비중입니다. 자정 12시 이후에 다시 시도해주세요."
    blocks = get_base_context_blocks(update_message)
    slack.chat.update(channel=channel, ts=ts, text="edit-text", blocks=json.dumps(blocks))


def update_database(data):
    """
    update database based on callback case
    :param data: payload from command callback
    """
    input_blocks_type = data['actions'][0]['block_id']
    if input_blocks_type in ["command_view_blocks", "invitation_blocks"]:
        update_user(data)
    elif input_blocks_type.startswith("evaluation_blocks"):
        update_evaluation(data)


@app.route("/slack/callback", methods=['POST'])
def command_callback():
    """
    update sent message
    update database when service enable time
    :return: http 200 status code
    """
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

