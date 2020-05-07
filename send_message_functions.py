import json
from app import slack
from blocks import get_command_view_blocks, get_base_context_blocks, get_info_blocks


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