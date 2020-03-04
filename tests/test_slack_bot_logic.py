import pytest
from logic.slack_bot_logic import SlackBotLogic

sb = SlackBotLogic("../plugins/rtmbot.conf")


def test_check_data_is_num():
    t1 = [56.0, 78.0, -5.6]
    for i, elem in enumerate(sb.check_data_is_num('56 78      -5.6')):
        assert elem == t1[i]
    t2 = [False, -99.7, False, False, 130.0, -23.0]
    for i, elem in enumerate(sb.check_data_is_num('hjksadf -99.7      asd     hfdg 130   -23')):
        assert elem == t2[i]