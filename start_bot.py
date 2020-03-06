from rtmbot import RtmBot
from os import path
from constants import path_conf_file
from logic.exceptions import NoConfFile
import yaml

if __name__ == '__main__':
    """
    Python script that will run 
    """
    try:
        if not path.exists(path_conf_file):
            raise NoConfFile
        with open(path_conf_file, 'r') as conffile:
            conf = yaml.load(conffile)
        bot = RtmBot(conf)
        bot.start()
    except NoConfFile:
        raise
