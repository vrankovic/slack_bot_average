import pytest
from logic.slack_bot_logic import SlackBotLogic
from slackclient import SlackClient

sb = SlackBotLogic("../plugins/rtmbot.conf")


def test_check_data_is_num1():
    t1 = [56.0, 78.0, -5.6]
    for i, elem in enumerate(sb.check_data_is_num('56 78      -5.6')):
        assert elem == t1[i]


def test_check_data_is_num2():
    t2 = [-99.7, 130.0, -23.0]
    for i, elem in enumerate(sb.check_data_is_num('hjksadf   -99.7      asd     hfdg 130   -23')):
        assert elem == t2[i]


def test_get_dm_channels():
    """
    I am not sure if this way of testing is good, because data on slack is changeable
    """

    channels = [
        {'id': 'DUVQDTBGV', 'created': 1583338464, 'is_archived': False, 'is_im': True, 'is_org_shared': False, 'user': 'UUVPUR68G', 'is_user_deleted': False, 'priority': 0},
        {'id': 'DULDC3L79', 'created': 1582742026, 'is_archived': False, 'is_im': True, 'is_org_shared': False, 'user': 'UUJ40C752', 'is_user_deleted': False, 'priority': 0},
        {'id': 'DU5PNECKC', 'created': 1582742026, 'is_archived': False, 'is_im': True, 'is_org_shared': False, 'user': 'USLACKBOT', 'is_user_deleted': False, 'priority': 0}
    ]
    for i, channel in enumerate(sb.get_dm_channels()):
        assert channel == channels[i]



