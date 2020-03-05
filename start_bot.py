from rtmbot import RtmBot
from constants import path_conf_file
import yaml
if __name__ == '__main__':
    """
    Python script that will run 
    """
    with open(path_conf_file, 'r') as conffile:
        conf = yaml.load(conffile)
    bot = RtmBot(conf)
    bot.start()
