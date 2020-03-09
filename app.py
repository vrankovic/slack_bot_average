from flask import Flask
from logic.slack_bot_logic import SlackBotLogic
from flask import jsonify
from constants import path_conf_file
from logic.exceptions import ApiError, NoUserWithUsername, NoConfFile

app = Flask(__name__)



@app.route('/average')
def all_average():
    """
    The route which is responsible to return average number of all numbers that users
    wrote in all public channels
    """
    try:
        sb_logic = SlackBotLogic(path_conf_file)
        return_average_message = f'Average of all users in all public channels is: ' \
                                 f'{sb_logic.get_average_of_all_public()}'
        return return_average_message
    except NoConfFile as ncf:
        return f'ERROR, {ncf}', 404
    except ApiError as ae:
        return jsonify(error=404, text=str(ae)), 404

@app.route('/average/<username>')
def user_average(username):
    """
    The route which is responsible to return average number of all numbers that user
    with username 'username' ever wrote in the team
    """
    try:
        sb_logic = SlackBotLogic(path_conf_file)
        return_average_message = f'Average for user {username} in all channels is: ' \
                                 f'{sb_logic.get_average_for_user(username)}'
        return return_average_message
    except NoConfFile as ncf:
        return f'ERROR, {ncf}', 404
    except ApiError as ae:
        return f'ERROR, {ae}', 404
    except NoUserWithUsername as nuwu:
        return f'ERROR, {nuwu}', 404


if __name__ == '__main__':
    app.run()
