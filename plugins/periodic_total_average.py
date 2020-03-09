from __future__ import print_function
from rtmbot.core import Plugin, Job
from logic import slack_bot_logic
from logic.slack_bot_logic import SlackBotLogic
from logic.exceptions import NoNumbers, ApiError
from constants import path_conf_file


class MyJob(Job):

    def create_msg_for_avrg_nums_public(self, sb_logic):
        """
        Method which returns key: value pairs of channel_id: message that contains the average
        of numbers of public channels
        """
        try:
            for channel_id in sb_logic.get_public_channels_bot_is_in():
                if sb_logic.check_new_channel_messages_last_min(channel_id):
                    try:
                        channel_average = sb_logic.get_channel_average(channel_id)
                        return_message = f'Average of all numbers in this channel {channel_id} is: {channel_average}'
                    except NoNumbers:
                        return_message = f'Messages in this channel does not contain numbers that can be parsed.'
                else:
                    return_message = ''
                yield channel_id, return_message
        except ApiError as ae:
            print(ae)

    def run(self, slack_client):
        sb_logic = SlackBotLogic(path_conf_file, slack_client)
        return_list = []
        for channel_id, return_message in self.create_msg_for_avrg_nums_public(sb_logic):
            if return_message:
                return_list.append([channel_id, return_message])
        if return_list:
            return return_list


class CollectTotalAverage(Plugin):
    def register_jobs(self):
        job = MyJob(60)
        self.jobs.append(job)
