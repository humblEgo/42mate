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


def get_command_view_blocks(value):
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
    blocks = get_base_blocks("42MATE에 오신걸 환영합니다!!")
    actions = {
        "type": "actions",
        "block_id": "command_view_blocks",
        "elements": []
    }

    if value == "register" or value == "registered" or value is None:
        actions['elements'] = [join_action, unregister_action]
    elif value == "join" or value == "joined":
        actions['elements'] = [unjoin_action, unregister_action]
    elif value == "unjoin" or value == "unjoined":
        actions['elements'] = [join_action, unregister_action]
    elif value == "unregister" or value == "unregistered":
        actions['elements'] = [register_action]

    blocks.append(actions)

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

def get_invitation_blocks():
    invitaion_blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "내일, 당신의 메이트와 만나보시겠어요? :smile:"
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
                        "text": "응응~"
                    },
                    "style": "primary",
                    "value": "join"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "아니, 내일은 스킵~"
                    },
                    "style": "danger",
                    "value": "unjoin"
                }
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "!매칭권유 구독을 원치 않으시면 /42mate 입력 후 '휴식하기' 선택!"
            }
        }
    ]
    return invitaion_blocks