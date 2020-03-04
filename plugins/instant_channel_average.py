from __future__ import print_function
from rtmbot.core import Plugin
from logic.slack_bot_logic import SlackBotLogic
from constants import path_conf_file

class InstantChannelAverage(Plugin):

    def process_message(self, data):
        channel_id = data['channel']
        sb_logic = SlackBotLogic(path_conf_file)
        return_message = sb_logic.create_dmc_average_message(channel_id)
        self.outputs.append(
            [channel_id, return_message]
        )
