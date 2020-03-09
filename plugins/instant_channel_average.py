from __future__ import print_function
from rtmbot.core import Plugin
from logic.slack_bot_logic import SlackBotLogic
from constants import path_conf_file
from logic.exceptions import NoNumbers, ApiError


class InstantChannelAverage(Plugin):

    def create_dmc_average_message(self, sb_logic, channel_id):
        """
        Method which returns message that contains the average of numbers of channel with id 'channel_id'
        """
        if sb_logic.is_dm_channel(channel_id):
            try:
                channel_average = sb_logic.get_channel_average(channel_id)
                return_message = f'Average of all numbers in this channel {channel_id} is: {channel_average}'
                return return_message
            except NoNumbers:
                return_message = f'Messages in this channel does not contain numbers that can be parsed.'
                return return_message
            except ApiError as ae:
                return_message = f'ERROR: {ae}'
                return return_message

    def process_message(self, data):
        channel_id = data.get('channel')
        sb_logic = SlackBotLogic(path_conf_file)
        return_message = self.create_dmc_average_message(sb_logic, channel_id)
        self.outputs.append(
            [channel_id, return_message]
        )
