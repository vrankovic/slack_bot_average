from flask import Flask
from logic.slack_bot_logic import SlackBotLogic
from flask import jsonify
from constants import path_conf_file
from logic.exceptions import ApiError

sb_logic = SlackBotLogic(path_conf_file)

app = Flask(__name__)


@app.route('/average')
def all_average():
    try:
        return_dict = {'message': f'Average of all users in all channels is: ',
                       'average': sb_logic.get_average_of_all_public()}
        return jsonify(return_dict)
    except ApiError as ae:
        return_dict = {'message': f'{ae}'}
    return jsonify(return_dict)


@app.route('/average/<username>')
def user_average(username):
    return_dict = {'message': f'Average for user {username} in all channels is: ',
                   'average': sb_logic.get_average_for_user(username)}
    return jsonify(return_dict)


if __name__ == '__main__':
    app.run()
