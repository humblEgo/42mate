from slacker import Slacker
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import os
import json
from datetime import datetime

token = os.environ['SLACK_TOKEN']
slack = Slacker(token)

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from db_manage import create_user, get_user_info, get_user_record
from send_message_functions import send_guide_message, send_direct_message, send_excuse_message
from command_callback_functions import update_command_view, update_database


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
            send_guide_message(form)
    else:
        send_excuse_message(form)
    return ("", 200)


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

