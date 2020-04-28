from apscheduler.schedulers.blocking import BlockingScheduler
from app import db, slack
from models import User, Match
from random import sample

sched = BlockingScheduler()


def get_blocks(match_status, users):
    if match_status == "MATCH_SUCCESSED":
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "MATCH SUCCESSED WITH " + str(users[0].intra_id) + " and " + str(user[1].intra_id) + "!"
                }
            }
        ]
    elif match_status == "MATCH_FAILED":
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "MATCH FAILED. SORRY, " + str(user[0].intr_id) + "!"
                }
            }
        ]
    return json.dumps(blocks)

def match_failed_handling(unmatched_user):
    slack_id = unmatched_user.slack_id
    response = slack.conversations.open(users=slack_id, return_im=True)
    channel = response.body['channel']['id']
    blocks = get_blocks("MATCH_FAILED", [unmatched_user])
    slack.chat.post_message(channel=channel, blocks=blocks)
    return ("", 200)

def match_successed_handling(matche):
    for match in matches:
        slack_id = [match.users[0], match.users[1]]
        response = slack.conversations.open(users=slack_id, return_im=True)
        channel = response.body['channel']['id']
        blocks = get_blocks("MATCH_SUCCESSED", match.users)
        slack.chat.post_message(channel=channel, blocks=blocks)
    return ("", 200)

def make_match():
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
    match_successed_handling(matches)
    db.session.add_all(matches)
    db.session.commit()
    return ("", 200)

sched.add_job(make_match, 'cron', hour=15)

sched.start()