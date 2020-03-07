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
    """
    Logic that is used to get all necessary data from slack and do all calculations to create
    requested averages of numbers
    """
    def __init__(self, file_path, slack_client=None):
        self._create_slack_client(file_path, slack_client)

    @check_path_exists_decorator
    def _create_slack_client(self, file_path, slack_client=None):
        """
        Method which is used to initialize slack client called by the constructor of this class.
        It is also decorated with the @check_path_exists_decorator which is checking
        if the configuration file exists on the provided path
        """
        if slack_client:
            self.slack_client = slack_client
        else:
            with open(file_path, 'r') as conf_file:
                conf = yaml.load(conf_file)
                self.slack_client = SlackClient(conf.get('SLACK_TOKEN'))

    def get_channel_average(self, channel_id):
        """
        Method which returns average of all numbers found in the channel with id 'channel_id'
        """
        summ = 0.0
        count = 0
        for msg in self.get_channel_messages(channel_id):
            for num in self.check_data_is_num(msg):
                summ += num
                count += 1
        if count == 0:
            raise NoNumbers
        average = round(summ / count, 2)
        return average

    def get_average_for_user(self, username):
        """
        Method which returns average of all numbers user with username 'username' wrote in all, public
        or direct message channels
        """
        summ = 0.0
        count = 0
        user_id = self.get_user_id_by_username(username)
        for channel_id in self.get_channels_user_is_in(user_id):
            for msg in self.get_channel_msgs_for_user(channel_id, user_id):
                for num in self.check_data_is_num(msg):
                    summ += num
                    count += 1
        if count == 0:
            raise NoNumbers
        average = round(summ / count, 2)
        return average

    def get_average_of_all_public(self):
        """
        Method which returns average of all numbers found in all public channels
        """
        summ = 0.0
        count = 0
        for channel_id in self.get_public_channels_bot_is_in():
            for msg in self.get_channel_messages(channel_id):
                for num in self.check_data_is_num(msg):
                    summ += num
                    count += 1
        if count == 0:
            raise NoNumbers
        average = round(summ / count, 2)
        return average

    def get_public_channels_bot_is_in(self):
        """
        Generator which returns all public channels where bot is a member
        """
        bot_id = self.get_bot_id()
        public_channels_response = self.slack_client.api_call('conversations.list', types='public_channel')
        self.raise_api_exception(public_channels_response, 'conversations.list',
                                 'get_public_channels_bot_is_in(self)')

        public_channels = public_channels_response.get('channels')
        for channel in public_channels:
            if self.check_member_in_channel(channel.get('id'), bot_id):
                yield channel.get('id')

    def get_channel_messages(self, channel_id):
        """
        This generator returns all messages which in channel with id 'channel_id' with the
        condition that message is not received by bot
        """
        history = self.slack_client.api_call('conversations.history', channel=channel_id)
        self.raise_api_exception(history, 'conversations.history',
                                 'get_channel_messages(self, channel_id)')
        has_more = True
        while has_more:
            for obj in history.get('messages'):
                if 'bot_id' not in obj:
                    yield obj.get('text')
            has_more = history.get('has_more')
            if has_more:
                next_cursor = history.get('response_metadata').get('next_cursor')
                history = self.slack_client.api_call('conversations.history', channel=channel_id, cursor=next_cursor)
                self.raise_api_exception(history, 'conversations.history',
                                         'get_channel_messages(self, channel_id)')

    def get_channel_msgs_for_user(self, channel_id, user_id):
        """
        This generator returns text of all messages that user with id 'user_id'
        wrote in the channel with id 'channel_id'
        """
        history = self.slack_client.api_call('conversations.history', channel=channel_id)
        self.raise_api_exception(history, 'conversations.history',
                                 'get_channel_msgs_for_user(self, channel_id, user_id)')
        has_more = True
        while has_more:
            for obj in history.get('messages'):
                if 'user' in obj and obj.get('user') == user_id:
                    yield obj.get('text')
            has_more = history.get('has_more')
            if has_more:
                next_cursor = history.get('response_metadata').get('next_cursor')
                history = self.slack_client.api_call('conversations.history', channel=channel_id, cursor=next_cursor)
                self.raise_api_exception(history, 'conversations.history',
                                         'get_channel_msgs_for_user(self, channel_id, user_id)')

    def check_new_channel_messages_last_min(self, channel_id):
        """
        Method which checks if channel with id 'channel_id' contains messages that are written
        in last minute.
        """
        now_in_timestamp = datetime.timestamp(datetime.now())
        min_before = datetime.now() - timedelta(seconds=10)
        min_before_in_timestamp = datetime.timestamp(min_before)
        history = self.slack_client.api_call('conversations.history', channel=channel_id, latest=now_in_timestamp,
                                             oldest=min_before_in_timestamp)
        self.raise_api_exception(history, 'conversations.history',
                                 'check_new_channel_messages_last_min(self, channel_id)')
        for msg in history.get('messages'):
            if 'client_msg_id' in msg:
                return True
        return False

    def is_channel_private(self, channel):
        """
        Method which checks if the channel is private channel
        """
        channel_info = self.slack_client.api_call("conversations.info", channel=channel)
        self.raise_api_exception(channel_info, 'conversations.info',
                                 'is_channel_private(self, channel)')
        if 'is_private' in channel_info.get('channel'):
            return channel_info.get('channel').get('is_private')

    def is_dm_channel(self, channel):
        """
        Method which checks if the channel is direct message channel
        """
        channel_info = self.slack_client.api_call("conversations.info", channel=channel)
        self.raise_api_exception(channel_info, 'conversations.info',
                                 'is_dm_channel(self, channel)')
        return channel_info.get('channel').get('is_im')

    def get_dm_channels(self):
        """
        Generator which returns only direct message channel objects.
        Slack api method conversations.list returns typically 100 objects per page where
        every object refers to one channel. If there is more than 100 direct message channels
        it means that in one api request should be sent more than 100 objects
        and that is not possible. It is necessary to paginate(create api calls) through pages and receive
        all objects in portions of 100 objects per page.
        """
        dm_channels = self.slack_client.api_call('conversations.list', types='im')
        self.raise_api_exception(dm_channels, 'conversations.list',
                                 'get_dm_channels(self)')
        has_more = True
        while has_more:
            for dm_channel in dm_channels.get('channels'):
                yield dm_channel
            has_more = dm_channels.get('response_metadata').get('next_cursor') != ''
            if has_more:
                next_cursor = dm_channels.get('response_metadata').get('next_cursor')
                dm_channels = self.slack_client.api_call('conversations.list', types='im', cursor=next_cursor)
                self.raise_api_exception(dm_channels, 'conversations.list',
                                         'get_dm_channels(self)')

    def check_data_is_num(self, data):
        """
        Generator which receives string 'data' as the input, splits 'data'
        on all white characters and stores it in the list. After that it checks if the string
        in list element can be converted in float and returns that float number only if the condition
        is satisfied. Process repeats for every element of the list.
        """
        val_list = data.split()
        for val in val_list:
            try:
                yield float(val)
            except ValueError:
                pass

    def get_bot_id(self):
        """
        Method which returns user id of Slack Bot
        """
        auth_test = self.slack_client.api_call('auth.test')
        self.raise_api_exception(auth_test, 'auth.test',
                                 'get_bot_id(self)')
        bot_id = auth_test.get('user_id')
        return bot_id

    def check_member_in_channel(self, channel_id, member_id):
        """
        Method which returns if user with id 'member_id' is member of channel
        with id 'channel_id'
        """
        members_response = self.slack_client.api_call('conversations.members', channel=channel_id)
        self.raise_api_exception(members_response, 'conversations.members',
                                 'check_member_in_channel(self, channel_id, member_id)')
        channel_members = members_response.get('members')
        return member_id in channel_members

    def get_user_id_by_username(self, username):
        """
        Method which returns id of the user in team. If there is no user with provided
        username NoUserWithUsername exception is raised.
        """
        users_list_response = self.slack_client.api_call('users.list')
        self.raise_api_exception(users_list_response, 'users.list',
                                 'get_user_id_by_username(self, username)')
        list_of_users = users_list_response.get('members')
        for user in list_of_users:
            if user.get('name') == username:
                return user.get('id')
        else:
            raise NoUserWithUsername

    def get_channels_user_is_in(self, user_id):
        """
         Generator which is used to return ids of all channels where user
         with id 'user_id' is member.
        """
        conversation_list_response = self.slack_client.api_call('conversations.list')
        self.raise_api_exception(conversation_list_response, 'conversations.list',
                                 'get_channels_user_is_in(self, user_id)')
        channels = conversation_list_response.get('channels')

        dm_conversation_list_response = self.slack_client.api_call('conversations.list', types='im')
        self.raise_api_exception(dm_conversation_list_response, 'conversations.list',
                                 'get_channels_user_is_in(self, user_id)')
        channels.extend(dm_conversation_list_response.get('channels'))

        for channel in channels:
            if self.check_member_in_channel(channel.get('id'), user_id):
                yield channel.get('id')

    def raise_api_exception(self, raising_object, api_method, raising_method):
        """
        Typical response after api call contains key/value pair "ok": True or "ok": False.
        If value is False, it means that an error occurred and the error message is stored as
        a dictionary value for key "error". This method rises an exception with the error description
        if the error occurs.
        """
        if not raising_object.get('ok'):
            raise ApiError(f"In the function logic.slack_bot_logic.{raising_method} for api method '{api_method}' "
                           f"response contains Error: {raising_object.get('error')}")


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
