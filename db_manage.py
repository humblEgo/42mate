from models import User, Match, Evaluation
from app import db
from datetime import datetime, timedelta
from pytz import timezone, utc
from sqlalchemy import extract


def create_user(form):
    """
    :param form: payload from slack slash command
    :return User: created user in database
    """
    slack_id = form.getlist('user_id')[0]
    intra_id = form.getlist('user_name')[0]
    try:
        user=User(
            slack_id=slack_id,
            intra_id=intra_id,
        )
        db.session.add(user)
        db.session.commit()
        return user
    except Exception as e:
        print(str(e))


def register_user(slack_id):
    try:
        user = User.query.filter_by(slack_id=slack_id).first()
        user.register = True
        user.joined = False
        db.session.commit()
    except Exception as e:
        print(str(e))


def unregister_user(slack_id):
    try:
        user = User.query.filter_by(slack_id=slack_id).first()
        user.register = False
        user.joined = False
        db.session.commit()
    except Exception as e:
        print(str(e))


def join_user(slack_id):
    try:
        user = User.query.filter_by(slack_id=slack_id).first()
        user.register = True
        user.joined = True
        db.session.commit()
    except Exception as e:
        print(str(e))


def unjoin_user(slack_id):
    try:
        user = User.query.filter_by(slack_id=slack_id).first()
        user.joined = False
        db.session.commit()
    except Exception as e:
        print(str(e))


def get_user_state(user):
    if user.register:
        if user.joined:
            return "joined"
        else:
            return "unjoined"
    else:
        return "unregistered"


def get_user_record(form):
    """
    :param form: payload from slack slash command
    :return User: record of the user who entered command from database
    """
    slack_id = form.getlist('user_id')[0]
    user_record = User.query.filter_by(slack_id=slack_id).first()
    return user_record


def get_user_current_mate(user):
    today_kst = datetime.now(timezone('Asia/Seoul'))
    today_utc = datetime.combine(today_kst.date(), datetime.min.time())
    yesterday_utc = today_utc - timedelta(days=1)
    current_evaluation = Evaluation.query.filter(Evaluation.user == user).order_by(Evaluation.index.desc()).first()
    if current_evaluation is None:
        return None
    current_match_day = current_evaluation.match.match_day
    if current_match_day >= yesterday_utc and current_match_day < today_utc:
        return current_evaluation.mate.intra_id


def get_user_info(user):
    """
    :param user: User
    :return dictionary: user infomation
    """
    user_info = {}
    user_info['slack_id'] = user.slack_id
    user_info['intra_id'] = user.intra_id
    user_info['state'] = get_user_state(user)
    user_info['current_mate'] = get_user_current_mate(user)
    return user_info


def is_overlap_evaluation(block_id):
    evaluation_index = block_id.replace('evaluation_blocks_', '')
    react_time = Evaluation.query.filter_by(index=evaluation_index).first().react_time
    return True if react_time is not None else False


def update_evaluation(data):
    try:
        evaluation_index = data['message']['blocks'][1]['block_id'].replace('evaluation_blocks_', '')
        evaluation = Evaluation.query.filter_by(index=evaluation_index).first()
        if evaluation.react_time is None:
            evaluation.react_time = datetime.now(utc)
            evaluation.satisfaction = int(data['actions'][0]['value'])
            db.session.commit()
    except Exception as e:
        print(str(e))
