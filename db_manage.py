from models import User, Match
from app import db
from datetime import datetime, timedelta
import pytz


def create_user(slack_id, intra_id):
    try:
        user=User(
            slack_id=slack_id,
            intra_id=intra_id,
        )
        db.session.add(user)
        db.session.commit()
        print("New user(" + user + ") Created Successfully")
    except Exception as e:
        print(str(e))


def register_user(slack_id):
    try:
        user = User.query.filter_by(slack_id=slack_id).first()
        user.register = True
        db.session.commit()
        print(slack_id + " register Successfully")
    except Exception as e:
        print(str(e))


def unregister_user(slack_id):
    try:
        user = User.query.filter_by(slack_id=slack_id).first()
        user.register = False
        user.joined = False
        db.session.commit()
        print(slack_id + " unregister Successfully")
    except Exception as e:
        print(str(e))


def join_user(slack_id):
    try:
        user = User.query.filter_by(slack_id=slack_id).first()
        user.joined = True
        db.session.commit()
        print(slack_id + " join Successfully")
    except Exception as e:
        print(str(e))


def unjoin_user(slack_id):
    try:
        user = User.query.filter_by(slack_id=slack_id).first()
        user.joined = False
        db.session.commit()
        print(slack_id + " unjoin Successfully")
    except Exception as e:
        print(str(e))


def get_user_state(user):
    if user is None:
        return None
    if user.register:
        if user.joined:
            return "joined"
        else:
            return "unjoined"
    else:
        return "unregistered"


def get_user_record(form):
    slack_id = form.getlist('user_id')[0]
    user_record = User.query.filter_by(slack_id=slack_id).first()
    return user_record


def get_user_info(form):
    user_info = {}
    user = get_user_record(form)
    user_info['state'] = get_user_state(user)
    user_info['slack_id'] = user.slack_id
    user_info['intra_id'] = user.intra_id
    user_info['match_count'] = user.match_count
    today = datetime.date(datetime.utcnow())
    match = Match.query.filter(Match.match_day >= today).first()
    if match:
        user_info['current_mate'] = match.users[0].intra_id == user_info['intra_id'] \
                                    and match.users[1].intra_id or match.users[0].intra_id
    else:
        user_info['current_mate'] = None
    return user_info
