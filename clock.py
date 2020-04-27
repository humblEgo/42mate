from apscheduler.schedulers.blocking import BlockingScheduler
from app import db
from models import User, Match
from random import sample

sched = BlockingScheduler()

def make_match():
    users = User.query.filter_by(joined=True).all()
    groups = []
    matches = []
    while len(users) >= 2:
        group = sample(users, 2)
        groups += [group]
        for i in range(2):
            users.remove(group[i])
    if len(users) == 1:
        users[0].joined = False
        # NEED MATCH FAIL HANDLING
    for group in groups:
        group[0].joined = False
        group[1].joined = False
        match = Match(
            user1=group[0],
            user2=group[1]
        )
        matches.append(match)
    db.session.add_all(matches)
    db.session.commit()
    # NEED MATCH SUCCESS HANDLING
    return "success"

sched.add_job(make_match, 'cron', hour=15)

sched.start()