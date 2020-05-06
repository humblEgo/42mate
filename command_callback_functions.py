from app import slack
import json
from blocks import get_base_context_blocks
from db_manage import join_user, unjoin_user, register_user, unregister_user, update_evaluation
from callback_message_functions import *

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