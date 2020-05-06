from app import db, slack
from blocks import get_base_blocks, get_match_blocks, get_evaluation_blocks, get_invitation_blocks
from models import User, Match, user_identifier, Evaluation, Activity
import json
from datetime import datetime, timedelta
from pytz import timezone, utc


def get_today_start_dt():
    """
    get today's 00:00:00 KST datetime and convert it to UTC datetime
    :return datetime: today's 00:00:00 datetime(UTC)
    """
    now_dt_kst = datetime.now(timezone('Asia/Seoul'))
    today_start_dt_kst = now_dt_kst.replace(hour=00, minute=00, second=00)
    today_start_dt_utc = today_start_dt_kst.astimezone(utc)
    return today_start_dt_utc


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
