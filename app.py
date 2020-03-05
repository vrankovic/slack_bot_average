from flask import Flask
from logic.slack_bot_logic import SlackBotLogic
from constants import path_conf_file

sb_logic = SlackBotLogic(path_conf_file)

app = Flask(__name__)


@app.route('/average')
def hello_world():
    return f'Average of all users in all channels is: {sb_logic.get_average_of_all_public()}'

@app.route('/average/<username>')
def hello_world1(username):
    return f'Average for user {username} in all channels is: {sb_logic.get_average_for_user(username)}'


if __name__ == '__main__':
    app.run()
