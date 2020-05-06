from app import slack
from blocks import get_base_blocks, get_match_blocks
from models import Match, Evaluation, Activity
from random import sample
import json


def create_evaluations_for(match):
    """
    :param match: Match
    :return list: list of Evaluation for each user of match
    """
    evaluations = []
    for i, user in enumerate(match.users):
        if i == 0:
            mate = match.users[1]
        else:
            mate = match.users[0]
        evaluation = Evaluation(match, user, mate)
        evaluations.append(evaluation)
    return evaluations


def create_evaluations(matches):
    """
    :param matches: list of Match
    :return list: list of Evaluation for matches
    """
    total_evaluations = []
    for match in matches:
        evaluations = create_evaluations_for(match=match)
        total_evaluations += evaluations
    return total_evaluations


def is_match_enable_day(unmatched_users):
    """
    :param unmatched_users: list of User
    :return boolean: True if unmatched users are equal to or more than 2 people
    """
    if unmatched_users and len(unmatched_users) >= 2:
        return True
    return False


def get_matched_group(unmatched_users):
    """
    create a match with a historyless relationship first.
    remove matched user from unmatched_users.
    :param unmatched_users: list of User
    :return list: user and mate
    """
    user = unmatched_users[0]
    unmatched_users.remove(user)
    for i in range(len(unmatched_users)):
        mate = sample(unmatched_users, 1)[0]
        match_history = Evaluation.query.filter_by(user=user, mate=mate).first()
        if not match_history or (i == len(unmatched_users) - 1):
            unmatched_users.remove(mate)
            matched_group = [user, mate]
            return matched_group


def get_matched_groups(unmatched_users):
    """
    create matched user groups while there are enough unmatched users to create new match
    :param unmatched_users: list of User
    :return list: list of matched_group
    """
    count_unmatched_users = len(unmatched_users)
    matched_groups = []
    while count_unmatched_users >= 2:
        matched_groups += [get_matched_group(unmatched_users)]
        count_unmatched_users -= 2
    return matched_groups


def create_match(matched_group, activities):
    """
    :param matched_group: list of matched user group
    :param activities: list of Activity
    :return Match:
    """
    activity = sample(activities, 1)[0]
    match = Match(
        user1=matched_group[0],
        user2=matched_group[1],
        activity=activity
    )
    return match


def create_matches_of(matched_groups):
    """
    :param matched_groups: list of matched user group
    :return list: list of Match
    """
    matches = []
    activities = Activity.query.all()
    for matched_group in matched_groups:
        matches += [create_match(matched_group, activities)]
    return matches


def update_user_field(unmatched_users):
    """
    update user field before change the list of unmatched user to create matches
    :param unmatched_users: list of User
    """
    for user in unmatched_users:
        user.joined = False
        user.match_count += 1


def let_matched_users_meet(matches):
    """
    create match channel in Slack and invite users in match
    :param matches: list of Match
    """
    print("MATCH_SUCCESSED_HANDLING")
    for match in matches:
        slack_id = [match.users[0].slack_id, match.users[1].slack_id]
        print("_SLACK_ID: " + str(slack_id[0]) + " & " + str(slack_id[1]))
        response = slack.conversations.open(users=slack_id, return_im=True)
        channel = response.body['channel']['id']
        blocks = get_match_blocks(match)
        slack.chat.post_message(channel=channel, blocks=json.dumps(blocks))


def send_match_fail_message(unmatched_user):
    """
    send a match fail message to an unmatched user in the end
    :param unmatched_user: User
    """
    print("MATCH_FAILED_HANDLING")
    slack_id = unmatched_user.slack_id
    print("_SLACK_ID: " + str(slack_id))
    intra_id = unmatched_user.intra_id
    response = slack.conversations.open(users=slack_id, return_im=True)
    channel = response.body['channel']['id']
    blocks = get_base_blocks("앗, 이를 어쩌죠? 오늘은 *" + intra_id + "* 님과 만날 메이트가 없네요:thinking_face:\n"
                             + "42메이트를 주변에 알려주시면 메이트를 만날 확률이 올라가요!:thumbsup_all:")
    slack.chat.post_message(channel=channel, blocks=json.dumps(blocks))
