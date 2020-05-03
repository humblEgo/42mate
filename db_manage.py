from models import User, Match
from app import db


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


def get_user_recode(form):
    slack_id = form.getlist('user_id')[0]
    user_recode = User.query.filter_by(slack_id=slack_id).first()
    return user_recode


def get_user_info(form):
    info = {}
    user = get_user_recode(form)
    info['slack_id'] = user.slack_id
    info['name'] = user.intra_id
    info['state'] = get_user_state(user)
    info['match_count'] = user.match_count
    # info['current_mate'] = get_current_mate(user)
    return info
