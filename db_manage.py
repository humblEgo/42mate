from models import User, Match


def create_user(slack_id, intra_id):
    try:
        user=User(
            slack_id=slack_id,
            intra_id=intra_id,
        )
        db.session.add(user)
        db.session.commit()
        return "Success"
    except Exception as e:
        return(str(e))


def register_user(slack_id):
    try:
        user = User.query.filter_by(slack_id=slack_id).first()
        user.register = True
        db.session.commit()
        return "Success"
    except Exception as e:
        return(str(e))


def unregister_user(slack_id):
    try:
        user = User.query.filter_by(slack_id=slack_id).first()
        user.register = False
        user.joined = False
        db.session.commit()
        print("Unregister Success")
        return "Success"
    except Exception as e:
        return(str(e))


def join_user(slack_id):
    try:
        user = User.query.filter_by(slack_id=slack_id).first()
        user.joined = True
        db.session.commit()
        print("Join Success")
        print("Success")
        return "Success"
    except Exception as e:
        print(str(e))
        return(str(e))


def unjoin_user(slack_id):
    try:
        user = User.query.filter_by(slack_id=slack_id).first()
        user.joined = False
        db.session.commit()
        return "Success"
    except Exception as e:
        return(str(e))


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
