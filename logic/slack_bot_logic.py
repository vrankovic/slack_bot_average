import inspect
import os
from slackclient import SlackClient
import time
import yaml
from datetime import datetime, timedelta
from .decorators import check_path_exists_decorator
from .exceptions import NoUserWithUsername, NoNumbers, ApiError
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

    def get_channel_average(self, channel):
        """

        """
        suma = 0.0
        count = 0
        for msg in self.get_channel_messages(channel):
            for num in self.check_data_is_num(msg):
                suma += num
                count += 1
        if count == 0:
            raise NoNumbers
        average = round(suma / count, 2)
        return average

    def get_average_for_user(self, username):
        """

        """
        suma = 0.0
        count = 0
        user_id = self.get_user_id_by_username(username)
        for channel_id in self.get_channels_user_is_in(user_id):
            for msg in self.get_channel_msgs_for_user(channel_id, user_id):
                for num in self.check_data_is_num(msg):
                    suma += num
                    count += 1
        if count == 0:
            raise NoNumbers
        average = round(suma / count, 2)
        return average

    def get_average_of_all_public(self):
        """

        """
        suma = 0.0
        count = 0
        for channel_id in self.get_public_channels_bot_is_in():
            for msg in self.get_channel_messages(channel_id):
                for num in self.check_data_is_num(msg):
                    suma += num
                    count += 1
        if count == 0:
            raise NoNumbers
        average = round(suma / count, 2)
        return average

    def get_public_channels_bot_is_in(self):
        """

        """
        bot_id = self.get_bot_id()
        public_channels_response = self.slack_client.api_call('conversations.list', types='public_channel')
        self.raise_api_exception(public_channels_response, 'conversations.list',
                                 'get_public_channels_bot_is_in(self)')

        public_channels = public_channels_response['channels']
        for channel in public_channels:
            if self.check_member_in_channel(channel['id'], bot_id):
                yield channel['id']

    def get_channel_messages(self, channel):
        """
        This generator
        """
        history = self.slack_client.api_call('conversations.history', channel=channel)
        self.raise_api_exception(history, 'conversations.history',
                                 'get_channel_messages(self, channel)')
        has_more = True
        while has_more:
            for obj in history['messages']:
                if 'bot_id' not in obj:
                    yield obj['text']
            has_more = history['has_more']
            if has_more:
                next_cursor = history['response_metadata']['next_cursor']
                history = self.slack_client.api_call('conversations.history', channel=channel, cursor=next_cursor)
                self.raise_api_exception(history, 'conversations.history',
                                         'get_channel_messages(self, channel)')

    def get_channel_msgs_for_user(self, channel_id, user_id):
        """
        This generator
        """
        history = self.slack_client.api_call('conversations.history', channel=channel_id)
        self.raise_api_exception(history, 'conversations.history',
                                 'get_channel_msgs_for_user(self, channel_id, user_id)')
        has_more = True
        while has_more:
            for obj in history['messages']:
                if 'user' in obj and obj['user'] == user_id:
                    yield obj['text']
            has_more = history['has_more']
            if has_more:
                next_cursor = history['response_metadata']['next_cursor']
                history = self.slack_client.api_call('conversations.history', channel=channel_id, cursor=next_cursor)
                self.raise_api_exception(history, 'conversations.history',
                                         'get_channel_msgs_for_user(self, channel_id, user_id)')

    def check_new_channel_messages_last_min(self, channel):
        """

        """
        now_in_timestamp = datetime.timestamp(datetime.now())
        min_before = datetime.now() - timedelta(seconds=10)
        min_before_in_timestamp = datetime.timestamp(min_before)
        history = self.slack_client.api_call('conversations.history', channel=channel, latest=now_in_timestamp,
                                             oldest=min_before_in_timestamp)
        self.raise_api_exception(history, 'conversations.history',
                                 'check_new_channel_messages_last_min(self, channel)')
        print(history)
        for msg in history['messages']:
            if 'client_msg_id' in msg:
                return True
        return False

    def is_channel_private(self, channel):
        """

        """
        channel_info = self.slack_client.api_call("conversations.info", channel=channel)
        self.raise_api_exception(channel_info, 'conversations.info',
                                 'is_channel_private(self, channel)')
        if 'is_private' in channel_info['channel']:
            return channel_info['channel']['is_private']

    def is_dm_channel(self, channel):
        """

        """
        channel_info = self.slack_client.api_call("conversations.info", channel=channel)
        self.raise_api_exception(channel_info, 'conversations.info',
                                 'is_dm_channel(self, channel)')
        return channel_info['channel']['is_im']

    def get_dm_channels(self):
        """

        """
        dm_channels = self.slack_client.api_call('conversations.list', types='im')
        self.raise_api_exception(dm_channels, 'conversations.list',
                                 'get_dm_channels(self)')
        has_more = True
        while has_more:
            for dm_channel in dm_channels['channels']:
                yield dm_channel
            has_more = dm_channels['response_metadata']['next_cursor'] != ''
            if has_more:
                next_cursor = dm_channels['response_metadata']['next_cursor']
                dm_channels = self.slack_client.api_call('conversations.list', types='im', cursor=next_cursor)
                self.raise_api_exception(dm_channels, 'conversations.list',
                                         'get_dm_channels(self)')

    def check_data_is_num(self, data):
        """

        """
        val_list = data.split()
        for val in val_list:
            try:
                yield float(val)
            except ValueError:
                pass

    def get_bot_id(self):
        """

        """
        auth_test = self.slack_client.api_call('auth.test')
        self.raise_api_exception(auth_test, 'auth.test',
                                 'get_bot_id(self)')
        bot_id = auth_test['user_id']
        return bot_id

    def check_member_in_channel(self, channel_id, member_id):
        """

        """
        members_response = self.slack_client.api_call('conversations.members', channel=channel_id)
        self.raise_api_exception(members_response, 'conversations.members',
                                 'check_member_in_channel(self, channel_id, member_id)')
        channel_members = members_response['members']
        return member_id in channel_members

    def get_user_id_by_username(self, username):
        """

        """
        users_list_response = self.slack_client.api_call('users.list')
        self.raise_api_exception(users_list_response, 'users.list',
                                 'get_user_id_by_username(self, username)')
        list_of_users = users_list_response['members']
        for user in list_of_users:
            if user['name'] == username:
                return user['id']
        else:
            raise NoUserWithUsername

    def get_channels_user_is_in(self, user_id):
        """

        """
        conversation_list_response = self.slack_client.api_call('conversations.list')
        self.raise_api_exception(conversation_list_response, 'conversations.list',
                                 'get_channels_user_is_in(self, user_id)')
        channels = conversation_list_response['channels']
        channels.extend(self.slack_client.api_call('conversations.list', types='im')['channels'])
        for channel in channels:
            if self.check_member_in_channel(channel['id'], user_id):
                yield channel['id']

    def raise_api_exception(self, raising_object, api_method, raising_method):
        if not raising_object['ok']:
            raise ApiError(f"In the function logic.slack_bot_logic.{raising_method} for api method '{api_method}' "
                           f"raised Error in api method call: {raising_object['error']}")


# sb = SlackBotLogic(path_conf_file)
# sb.test()
# print(sb.get_average_of_all_public())
# print(sb.get_average_for_user('ivanczv'))
# for msg in sb.get_chnl_msgs(sb.get_all_dm_channels()[1]['id']):
#     print(msg)
# print(sb.get_all_dm_channels())
#
# try:
#     sb = SlackClient('xoxb-972451774343-970138762340-WkzKa1JpAWBUWkKLpdMywrNz')
#     test = sb.api_call('users.identity')
#     if not test['ok']:
#         raise ApiError(f"Error in api method call: {test['error']}")
# except ApiError as ae:
#     print(ae)
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
