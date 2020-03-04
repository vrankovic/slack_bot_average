import os
from slackclient import SlackClient
import time
import yaml
from datetime import datetime, timedelta
from .decorators import check_path_exists_decorator
from constants import path_conf_file


class SlackBotLogic:

    @check_path_exists_decorator
    def __init__(self, file_path, slack_client=None):
        if slack_client:
            self.slack_client = slack_client
        else:
            with open(file_path, 'r') as conf_file:
                conf = yaml.load(conf_file)
                self.slack_client = SlackClient(conf['SLACK_TOKEN'])

    def get_pblic_chnls_bot_is_in(self):
        """

        """
        bot_id = self.get_bot_id()
        public_channels = self.slack_client.api_call('conversations.list', types='public_channel')['channels']
        for channel in public_channels:
            if self.check_member_in_chnl(channel['id'],bot_id):
                yield channel['id']



    def create_dmc_average_message(self, channel_id):
        """

        """
        if self.is_chnl_dmc(channel_id):
            channel_average = self.calc_chnl_average(channel_id)
            return_message = f'Average of all numbers in this channel {channel_id} is: {channel_average}'
            return return_message

    def create_msg_for_avrg_nums_public(self):
        """

        """
        channel_average = 0
        for channel_id in self.get_pblic_chnls_bot_is_in():
            if self.check_new_chnl_msgs_last_min(channel_id):
                channel_average = self.calc_chnl_average(channel_id)
                return_message = f'Average of all numbers in this channel {channel_id} is: {channel_average}'
            else:
                return_message = ''
            yield channel_id, return_message

    def get_chnl_msgs(self, channel):
        """
        This generator
        """
        history = self.slack_client.api_call('conversations.history', channel=channel)
        has_more = True
        while has_more:
            for obj in history['messages']:
                if 'bot_id' not in obj:
                    yield obj['text']
            has_more = history['has_more']
            if has_more:
                next = history['response_metadata']['next_cursor']
                history = self.slack_client.api_call('conversations.history', channel=channel, cursor=next)

    def check_new_chnl_msgs_last_min(self, channel):
            """

            """
            now_in_timestamp = datetime.timestamp(datetime.now())
            min_before = datetime.now() - timedelta(seconds=10)
            min_before_in_timestamp = datetime.timestamp(min_before)
            history = self.slack_client.api_call('conversations.history', channel=channel, latest=now_in_timestamp,
                                                 oldest=min_before_in_timestamp)
            print(history)
            for msg in history['messages']:
                if 'client_msg_id' in msg:
                    return True
            return False

    def is_chnl_private(self, chnl):
        """

        """
        channel_info = self.slack_client.api_call("conversations.info", channel=chnl)
        if 'is_private' in channel_info['channel']:
            return channel_info['channel']['is_private']

    def is_chnl_dmc(self, chnl):
        """

        """
        channel_info = self.slack_client.api_call("conversations.info", channel=chnl)
        return channel_info['channel']['is_im']

    def check_data_is_num(self, data):
        """

        """
        val_list = data.split()
        for val in val_list:
            try:
                yield float(val)
            except ValueError:
                pass
                
    def calc_chnl_average(self, chnl):
        """

        """
        suma = 0.0
        count = 0
        for msg in self.get_chnl_msgs(chnl):
            for num in self.check_data_is_num(msg):
                suma += num
                count += 1
        average = round(suma/count, 2)
        return average

    def get_bot_id(self):
        """

        """
        bot_id = self.slack_client.api_call('auth.test')['user_id']
        return bot_id

    def check_member_in_chnl(self, chnl_id, member_id):
        """

        """
        channel_members = self.slack_client.api_call('conversations.members', channel=chnl_id)['members']
        return member_id in channel_members


# sb = SlackBotLogic(path_conf_file)
# for msg in sb.get_chnl_msgs(sb.get_all_dm_channels()[1]['id']):
#     print(msg)
# print(sb.get_all_dm_channels())
#
# slach_bot = SlackClient('xoxb-972451774343-970138762340-uUucbeUBbMze4xcY40K5W23W')
# print(slach_bot.api_call('conversations.info', channel=sb.get_all_dm_channels()[1]['id']))
#
# print(sb.check_new_chnl_msgs_last_min('DULDC3L79'))
#
# for msg in sb.get_chnl_msgs('DULDC3L79'):
#     for elem in sb.check_data_is_num(msg):
#         print(elem)

# print(slach_bot.api_call('chat.postMessage', channel='DULDC3L79', text='stefan test'))
# print(slach_bot.api_call('conversations.list', types='public_channel')['channels'])
# for chnl_id in sb.get_pblic_chnls_bot_is_in():
#     print(chnl_id)