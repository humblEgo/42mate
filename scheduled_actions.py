from apscheduler.schedulers.blocking import BlockingScheduler
from app import db, slack
from models import User, Match, Evaluation
from random import sample
import json
from blocks import get_base_blocks, get_evaluation_blocks
from sqlalchemy import extract
from datetime import datetime, timedelta


def match_failed_handling(unmatched_user):
    slack_id = unmatched_user.slack_id
    intra_id = unmatched_user.intra_id
    response = slack.conversations.open(users=slack_id, return_im=True)
    channel = response.body['channel']['id']
    blocks = get_base_blocks("MATCH FAILED. SORRY, " + str(intra_id) + "!")
    slack.chat.post_message(channel=channel, blocks=json.dumps(blocks))
    print("MATCH FAILED HANDLING")
    print("_SLACK_ID: " + str(slack_id))
    print("_BLOCK: " + str(blocks))


def send_match_success_blocks(match):
    slack_id = [match.users[0].slack_id, match.users[1].slack_id]
    response = slack.conversations.open(users=slack_id, return_im=True)
    channel = response.body['channel']['id']
    print("_SLACK_ID: " + str(slack_id[0]) + " & " + str(slack_id[1]))
    blocks = get_base_blocks("MATCH SUCCESSED WITH " + str(match.users[0].intra_id) + " and " + str(match.users[1].intra_id) + "!")
    print("_BLOCK: " + str(blocks))
    slack.chat.post_message(channel=channel, blocks=json.dumps(blocks))


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


def match_successed_handling(matches):
    print("MATCH SUCCESSED HANDLING")
    total_evaluations = []
    for match in matches:
        send_match_success_blocks(match)
        evaluations = create_evaluations_for(match=match)
        total_evaluations += evaluations
    return total_evaluations


def make_match_and_eval():
    print("MAKE MATCH START")
    unmatched_users = User.query.filter_by(joined=True).all()
    matched_groups = []
    matches = []
    count_unmatched_users = len(unmatched_users)
    while count_unmatched_users >= 2:
        matched_group = sample(unmatched_users, 2)
        matched_groups += [matched_group]
        for i in range(2):
            unmatched_users.remove(matched_group[i])
        count_unmatched_users -= 2
    if count_unmatched_users == 1:
        unmatched_users[0].joined = False
        match_failed_handling(unmatched_users[0])
    for matched_group in matched_groups:
        matched_group[0].joined = False
        matched_group[1].joined = False
        match = Match(
            user1=matched_group[0],
            user2=matched_group[1]
        )
        matches.append(match)
    evaluations = match_successed_handling(matches)
    db.session.add_all(matches)
    db.session.add_all(evaluations)
    db.session.commit()


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
            if evaluation.user.intra_id == 'eunhkim':
                slack.chat.post_message(channel=channel, blocks=blocks)


if __name__ == "__main__":
    sched = BlockingScheduler()
    sched.add_job(send_evaluation_schedule, 'cron', hour=1)
    sched.add_job(make_match_and_eval, 'cron', hour=15)
    sched.start()

