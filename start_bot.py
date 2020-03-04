from rtmbot import RtmBot
import yaml
if __name__ == '__main__':
    """
    Python script that will run 
    """
    with open("./plugins/rtmbot.conf", 'r') as conffile:
        conf = yaml.load(conffile)
    bot = RtmBot(conf)
    bot.start()