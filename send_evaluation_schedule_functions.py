from app import db, slack
from blocks import get_evaluation_blocks
from models import Match
import json
from datetime import timedelta
from db_manage import get_today_start_dt


def get_target_matches():
    """
    get yesterday's matches which are not yet evaluated
    :return list: list of Match
    """
    today_start_dt = get_today_start_dt()
    yesterday_start_dt = today_start_dt - timedelta(days=1)
    target_matches = db.session.query(Match).filter(Match.match_day >= yesterday_start_dt,
                                            Match.match_day < today_start_dt).all()
    return target_matches


def send_evaluation_message(evaluation):
    """
    :param evaluation: Evaluation
    """
    blocks = get_evaluation_blocks(evaluation)
    slack_id = evaluation.user.slack_id
    response = slack.conversations.open(users=slack_id, return_im=True)
    channel = response.body['channel']['id']
    slack.chat.post_message(channel=channel, blocks=json.dumps(blocks))
