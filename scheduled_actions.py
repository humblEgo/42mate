from apscheduler.schedulers.blocking import BlockingScheduler
from app import db, slack
from blocks import get_base_blocks, get_match_blocks, get_invitation_blocks
from models import User, Match, user_identifier, Activity
from random import sample
from sqlalchemy import func, text, or_, any_, and_
import json

sched = BlockingScheduler()


def get_unused_matches():
    all_matches = db.session.query(Match).join(Match.users).all()
    unused_matches = []
    for match in all_matches:
        if match.users[0].joined == True or match.users[1].joined == True:
            unused_matches += [match]
    return unused_matches


def get_matched_group(unmatched_users, unused_matches):
    user = unmatched_users[0]
    unmatched_users.remove(user)
    for i in range(len(unmatched_users)):
        mate = sample(unmatched_users, 1)[0]
        ret = 0
        for match in unused_matches:
            if set([user, mate]).issubset(match.users):
                ret = 1
                break
        if ret == 0 or (i == len(unmatched_users) - 1):
            unmatched_users.remove(mate)
            matched_group = [user, mate]
            for match in unused_matches:
                if any(user in matched_group for user in match.users):
                    unused_matches.remove(match)
            return matched_group


def get_matched_groups(unmatched_users, unused_matches):
    count_unmatched_users = len(unmatched_users)
    matched_groups = []
    while count_unmatched_users >= 2:
        matched_groups += [get_matched_group(unmatched_users, unused_matches)]
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
    return ("", 200)


def match_failed_handling(unmatched_user):
    print("MATCH_FAILED_HANDLING")
    slack_id = unmatched_user.slack_id
    print("_SLACK_ID: " + str(slack_id))
    intra_id = unmatched_user.intra_id
    response = slack.conversations.open(users=slack_id, return_im=True)
    channel = response.body['channel']['id']
    blocks = get_base_blocks("MATCH FAILED. SORRY, " + str(intra_id) + "!")
    slack.chat.post_message(channel=channel, blocks=json.dumps(blocks))
    unmatched_user.match_count -= 1
    return ("", 200)


def match_make_schedule():
    print("MATCH_MAKE_SCHEDULE_START")
    unmatched_users = db.session.query(User).filter_by(joined=True).order_by('match_count').all()
    unused_matches = get_unused_matches()
    update_user_field(unmatched_users)
    matched_groups = get_matched_groups(unmatched_users, unused_matches)
    matches = []
    activities = Activity.query.all()
    for matched_group in matched_groups:
        matches += [create_match(matched_group, activities)]
    match_successed_handling(matches)
    if unmatched_users:
        match_failed_handling(unmatched_users[0])
    print("MATCH_MAKE_SCHEDULE_ADD_AND_COMMIT_START")
    db.session.add_all(matches)
    print(matches)
    db.session.commit()
    print("MATCH_MAKE_SCHEDULE_END")
    return ("", 200)


def send_join_invitation_schedule():
    blocks = get_invitation_blocks()
    unjoined_users = db.session.query(User).filter(and_(User.register == True, User.joined == False)).all()
    for user in unjoined_users:
        slack_id = user.slack_id
        response = slack.conversations.open(users=slack_id, return_im=True)
        channel = response.body['channel']['id']
        slack.chat.post_message(channel=channel, blocks=json.dumps(blocks))


sched.add_job(match_make_schedule, 'cron', hour=15, minute=00)
sched.start()

