from __future__ import print_function
from rtmbot.core import Plugin, Job
from logic import slack_bot_logic
from logic.slack_bot_logic import SlackBotLogic
from constants import path_conf_file


class myJob(Job):

    def run(self, slack_client):
        sb_logic = SlackBotLogic(path_conf_file, slack_client)
        return_list = []
        for channel_id, return_message in sb_logic.create_pub_average_message():
            if return_message:
                return_list.append([channel_id, return_message])

        print(return_list)

        if return_list:
            return return_list


class CollectTotalAverage(Plugin):
    def register_jobs(self):
        job = myJob(2)
        self.jobs.append(job)