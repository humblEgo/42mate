from apscheduler.schedulers.blocking import BlockingScheduler
from app import db
from models import User, Match
from random import sample

sched = BlockingScheduler()

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
        # NEED MATCH FAIL HANDLING
    for matched_group in matched_groups:
        matched_group[0].joined = False
        matched_group[1].joined = False
        match = Match(
            user1=matched_group[0],
            user2=matched_group[1]
        )
        matches.append(match)
    db.session.add_all(matches)
    db.session.commit()
    # NEED MATCH SUCCESS HANDLING
    return "success"

sched.add_job(make_match, 'cron', hour=15)

sched.start()