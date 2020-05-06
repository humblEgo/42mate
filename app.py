from slacker import Slacker
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

token = os.environ['SLACK_TOKEN']
slack = Slacker(token)

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from db_manage import join_user, create_user, unjoin_user, register_user, unregister_user, \
                      update_evaluation, get_user_info, get_user_record
from send_message_functions import *
from callback_message_functions import *


def is_readytime():
    """
    :return boolean: True if the current time is between 23:42 and 23:59 KST
    """
    utctime = datetime.utcnow()
    if utctime.hour == 14 and utctime.minute >= 42:
        return True
    return False


@app.route("/")
def ftmate_main_route():
    return "This is ftmate_main_route"


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

#슬랙 event subscriber for local test
# from flask import make_response
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

