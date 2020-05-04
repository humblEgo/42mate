from apscheduler.schedulers.blocking import BlockingScheduler
from app import db, slack
from blocks import get_base_blocks, get_match_blocks, get_evaluation_blocks, get_invitation_blocks
from models import User, Match, user_identifier, Evaluation, Activity
from random import sample
from sqlalchemy import and_
import json
from datetime import datetime, timedelta


def create_evaluations_for(match):
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
    total_evaluations = []
    for match in matches:
        evaluations = create_evaluations_for(match=match)
        total_evaluations += evaluations
    return total_evaluations


def is_match_enable_day(unmatched_users):
    if unmatched_users and len(unmatched_users) >= 2:
        return True
    return False


def get_matched_group(unmatched_users):
    user = unmatched_users[0]
    unmatched_users.remove(user)
    for i in range(len(unmatched_users)):
        mate = sample(unmatched_users, 1)[0]
        history = Evaluation.query.filter_by(user=user, mate=mate).first()
        if not history or (i == len(unmatched_users) - 1):
            unmatched_users.remove(mate)
            matched_group = [user, mate]
            return matched_group


def get_matched_groups(unmatched_users):
    count_unmatched_users = len(unmatched_users)
    matched_groups = []
    while count_unmatched_users >= 2:
        matched_groups += [get_matched_group(unmatched_users)]
        count_unmatched_users -= 2
    return matched_groups


def create_match(matched_group, activities):
    activity = sample(activities, 1)[0]
    match = Match(
        user1=matched_group[0],
        user2=matched_group[1],
        activity=activity
    )
    return match


def update_user_field(unmatched_users):
    for user in unmatched_users:
        user.joined = False
        user.match_count += 1


def match_successed_handling(matches):
    print("MATCH_SUCCESSED_HANDLING")
    for match in matches:
        slack_id = [match.users[0].slack_id, match.users[1].slack_id]
        print("_SLACK_ID: " + str(slack_id[0]) + " & " + str(slack_id[1]))
        response = slack.conversations.open(users=slack_id, return_im=True)
        channel = response.body['channel']['id']
        blocks = get_match_blocks(match)
        slack.chat.post_message(channel=channel, blocks=json.dumps(blocks))


def match_failed_handling(unmatched_user):
    print("MATCH_FAILED_HANDLING")
    slack_id = unmatched_user.slack_id
    print("_SLACK_ID: " + str(slack_id))
    intra_id = unmatched_user.intra_id
    response = slack.conversations.open(users=slack_id, return_im=True)
    channel = response.body['channel']['id']
    blocks = get_base_blocks("앗, 이를 어쩌죠? 오늘은 *" + intra_id + "* 님과 만날 메이트가 없네요:thinking_face:\n"
                             + "42메이트를 주변에 알려주시면 메이트를 만날 확률이 올라가요!:thumbsup_all:")
    slack.chat.post_message(channel=channel, blocks=json.dumps(blocks))
    unmatched_user.match_count -= 1


def match_make_schedule():
    print("MATCH_MAKE_SCHEDULE_START")
    unmatched_users = db.session.query(User).filter_by(joined=True).order_by('match_count').all()
    update_user_field(unmatched_users)
    match_enable_day = is_match_enable_day(unmatched_users)
    if match_enable_day:
        matched_groups = get_matched_groups(unmatched_users)
        matches = []
        activities = Activity.query.all()
        for matched_group in matched_groups:
            matches += [create_match(matched_group, activities)]
        match_successed_handling(matches)
        evaluations = create_evaluations(matches)
        db.session.add_all(matches)
        db.session.add_all(evaluations)
    if unmatched_users:
        match_failed_handling(unmatched_users[0])
    print("MATCH_MAKE_SCHEDULE_ADD_AND_COMMIT_START")
    db.session.commit()
    print("MATCH_MAKE_SCHEDULE_END")


def send_evaluation_schedule():
    today = datetime.date(datetime.utcnow())
    yesterday = today - timedelta(days=1)
    matches = db.session.query(Match).filter(Match.match_day >= yesterday, Match.match_day < today).all()
    for match in matches:
        for evaluation in match.evaluations:
            evaluation.send_time = datetime.utcnow()
            blocks = json.dumps(get_evaluation_blocks(evaluation))
            slack_id = evaluation.user.slack_id
            response = slack.conversations.open(users=slack_id, return_im=True)
            channel = response.body['channel']['id']
            slack.chat.post_message(channel=channel, blocks=blocks)
    db.session.commit()


def send_join_invitation_schedule():
    blocks = get_invitation_blocks()
    unjoined_users = db.session.query(User).filter(and_(User.register == True, User.joined == False)).all()
    for user in unjoined_users:
        slack_id = user.slack_id
        response = slack.conversations.open(users=slack_id, return_im=True)
        channel = response.body['channel']['id']
        slack.chat.post_message(channel=channel, blocks=json.dumps(blocks))


if __name__ == "__main__":
    match_make_schedule()
    # sched = BlockingScheduler()
    # sched.add_job(send_evaluation_schedule, 'cron', hour=1)
    # sched.add_job(send_join_invitation_schedule, 'cron', hour=9)
    # sched.add_job(match_make_schedule, 'cron', hour=15)
    # sched.start()