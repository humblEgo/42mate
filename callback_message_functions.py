from db_manage import is_overlap_evaluation


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


