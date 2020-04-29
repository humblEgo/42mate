from apscheduler.schedulers.blocking import BlockingScheduler
from app import db, slack
from models import User, Match, user_identifier
from random import sample
from blocks import get_base_blocks
from sqlalchemy import func, text
import json

sched = BlockingScheduler()



def match_failed_handling(unmatched_user):
    slack_id = unmatched_user.slack_id
    intra_id = unmatched_user.intra_id
    #response = slack.conversations.open(users=slack_id, return_im=True)
    #channel = response.body['channel']['id']
    #blocks = get_base_blocks("MATCH FAILED. SORRY, " + str(intra_id) + "!")
    #slack.chat.post_message(channel=channel, blocks=json.dumps(blocks))
    print("MATCH FAILED HANDLING")
    print("_SLACK_ID: " + str(slack_id))
    #print("_BLOCK: " + str(blocks))
    return ("", 200)


def match_successed_handling(matches):
    print("MATCH SUCCESSED HANDLING")
    for match in matches:
        slack_id = [match.users[0].slack_id, match.users[1].slack_id]
        print("_SLACK_ID: " + str(slack_id[0]) + " & " + str(slack_id[1]))
        #response = slack.conversations.open(users=slack_id, return_im=True)
        #channel = response.body['channel']['id']
        #blocks = get_base_blocks("MATCH SUCCESSED WITH " + str(match.users[0].intra_id) + " and " + str(match.users[1].intra_id) + "!")
        #print("_BLOCK: " + str(blocks))
        #slack.chat.post_message(channel=channel, blocks=json.dumps(blocks))
    return ("", 200)


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


def make_match():
    print("MAKE MATCH START")
    unmatched_users = db.session.query(User).join(user_identifier)\
        .group_by(User).order_by(func.count(user_identifier.c.user_index)).all()
    unused_matches = db.session.query(Match).all()
    matched_groups = []
    matches = []
    count_unmatched_users = len(unmatched_users)
    while count_unmatched_users >= 2:
        matched_groups += [get_matched_group(unmatched_users, unused_matches)]
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
    #db.session.add_all(matches)
    #db.session.commit()
    return ("", 200)


sched.add_job(make_match, 'cron', hour=15, minute=00)

sched.start()