def get_base_blocks(text):
    base_block = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": text
            }
        }
    ]
    return base_block


def get_base_context_blocks(text):
    blocks = [
        {
            "type": "context",
            "elements": [
                {"type": "mrkdwn", "text": text}
            ]
        }
    ]
    return blocks


def get_action_blocks_by(user_info):
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
                "text": "앞으로 메이트 매칭에 참여할 수 없습니다."
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
    action_blocks = {
        "type": "actions",
        "block_id": "command_view_blocks",
        "elements": []
    }
    user_state = user_info['state']
    if user_state == "registered":
        action_blocks['elements'] = [join_action, unregister_action]
    elif user_state == "joined":
        action_blocks['elements'] = [unjoin_action, unregister_action]
    elif user_state == "unjoined":
        action_blocks['elements'] = [join_action, unregister_action]
    elif user_state == "unregistered":
        action_blocks['elements'] = [register_action]
    return action_blocks


def get_command_view_blocks(user_info):
    blocks = get_base_blocks(user_info['intra_id'] + "님, 안녕하세요! 무엇을 도와드릴까요?")
    action_blocks = get_action_blocks_by(user_info)
    blocks.append(action_blocks)
    return blocks


def get_evaluation_blocks(evaluation):
    evaluation_blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text":"*" + evaluation.user.intra_id + "* 님, 어제 메이트 *" + evaluation.mate.intra_id + "* 님과의 시간은 얼마나 만족스러우셨나요? :ghost:"
            }
        },
        {
            "type": "actions",
            "block_id": "evaluation_blocks_" + str(evaluation.index),
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": ":star:",
                        "emoji": True
                    },
                    "value": "10"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": ":star::star:",
                        "emoji": True
                    },
                    "value": "20"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": ":star::star::star:",
                        "emoji": True
                    },
                    "value": "30"
                },
                {
                    "action_id": "evaluation",
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": ":star::star::star::star:",
                        "emoji": True
                    },
                    "value": "40"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": ":star::star::star::star::star:",
                        "emoji": True
                    },
                    "value": "50"
                }
            ]
        }
    ]
    return evaluation_blocks


def get_match_blocks(match):
    text = "따-단! *" + match.users[0].intra_id + "* 님과 *" + match.users[1].intra_id + "* 님은 오늘의 메이트입니다. \n" \
        + "온라인 미션과 함께 서로에 대해 알아가며 흥미로운 시간을 만들어보세요. \n" \
        + "곧 클러스터에서 만나면 반갑게 인사할 수 있게요!"
    blocks = get_base_blocks(text)
    blocks.append({"type": "divider"})
    content = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*우리를 가깝게 만들 온라인 미션 : " + match.activity.subject + "* :sunglasses:\n" + match.activity.content
            }
    }
    blocks.append(content)
    blocks.append({"type": "divider"})
    return blocks


def get_info_blocks(user_info):
    if user_info['current_mate']:
        text = "오늘의 메이트는 *" + user_info['current_mate'] + "* 님입니다. "
    else:
        text = "오늘은 메이트가 없습니다."
    if user_info['state'] == 'joined':
        text += "내일 참여가 예약되어 있습니다."
    elif user_info['state'] == 'unjoined':
        text += "내일 참여가 예약되어 있지 않습니다."
    elif user_info['state'] == 'unregistered':
        text += "앞으로 메이트 매칭이 진행되지 않습니다."
    blocks = [{"type": "context", "elements": [{"type": "mrkdwn", "text": text}]}]
    # blocks += get_command_view_blocks(user_info)
    return blocks


def get_invitation_blocks():
    invitaion_blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "안녕하세요. 내일, 당신의 메이트와 만나보시겠어요? :smile:"
            }
        },
        {
            "type": "actions",
            "block_id": "invitation_blocks",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "응! 만나고 싶어."
                    },
                    "style": "primary",
                    "value": "join"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "아니, 내일은 스킵-"
                    },
                    "style": "danger",
                    "value": "unjoin"
                }
            ]
        }
    ]
    return invitaion_blocks