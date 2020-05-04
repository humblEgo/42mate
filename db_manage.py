from models import User, Match, Evaluation
from app import db
from datetime import datetime, timedelta
import pytz
from sqlalchemy import extract


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
    evaluation = Evaluation.query.filter(Evaluation.user == user, Evaluation.match.match_day >= today).first()
    if evaluation:
        user_info['current_mate'] = evaluation.mate.intra_id
    else:
        user_info['current_mate'] = None
    return user_info


def is_overlap_evaluation(block_id):
    evaluation_index = block_id.replace('evaluation_blocks_', '')
    check = Evaluation.query.filter_by(index=evaluation_index).first().react_time
    if check is None:
        return False
    return True


def update_evaluation(data):
    try:
        evaluation_index = data['message']['blocks'][1]['block_id'].replace('evaluation_blocks_', '')
        evaluation = Evaluation.query.filter_by(index=evaluation_index).first()
        evaluation.satisfaction = int(data['actions'][0]['value'])
        evaluation.react_time = datetime.utcnow()
        db.session.commit()
    except Exception as e:
        print(str(e))
