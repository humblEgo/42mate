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


def get_user_state(slack_id):
    if isinstance(slack_id, list):
        slack_id = slack_id[0]
    user = User.query.filter_by(slack_id=slack_id).first()
    if user is None:
        return None
    if user.register is True:
        if user.joined is True:
            return "joined"
        else:
            return "unjoined"
    else:
        return "unregistered"
