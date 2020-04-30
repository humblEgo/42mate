from models import User, Match, Evaluation
from app import db
from datetime import datetime
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


def check_overlap_evaluation(data):
    user = User.query.filter_by(slack_id=data['user']['id']).first()
    check = next((evaluation for evaluation in user.active_evaluations if evaluation.match.match_day.day == datetime.utcnow().day), None)
    if check is None:
        return False
    return True


def create_evaluation(data):
    user_slack_id = data['user']['id']
    user = User.query.filter_by(slack_id=user_slack_id).first()
    match = Match.query.filter(Match.users.contains(user)).first()
    #TODO: NEEDS REFACTORING
    mate_slack_id = next((mate.slack_id for mate in match.users if mate.slack_id != user_slack_id), None)
    mate = User.query.filter_by(slack_id=mate_slack_id).first()
    satisfaction = int(data['actions'][0]['value'])
    try:
        evaluation=Evaluation(
            match=match,
            user=user,
            mate=mate,
            satisfaction=satisfaction
        )
        db.session.add(evaluation)
        db.session.commit()
        print("New evaluation(" + str(evaluation) + ") Created Successfully")
    except Exception as e:
        print(str(e))