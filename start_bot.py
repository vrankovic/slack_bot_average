from rtmbot import RtmBot
from os import path
from constants import path_conf_file
from logic.exceptions import NoConfFile
import yaml

"""
This python script is responsible for starting process of 
instant and periodical messages replay by our bot.
"""
if __name__ == '__main__':
    try:
        if not path.exists(path_conf_file):
            raise NoConfFile
        with open(path_conf_file, 'r') as conffile:
            conf = yaml.load(conffile)
        bot = RtmBot(conf)
        bot.start()
    except NoConfFile:
        raise NoConfFile('There is no configuration file at the provided path. '
                         'Please check if the path you provided is correct.')
