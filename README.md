Bot in Slack system is designed to interact with users via conversations. 

Slack_bot tool is used as the the "brain" of the bot in Slack. It calculates the average of numbers and responds to the 
particular user in the slack team or to the group bot is member of. The bot which is connected with running slack-bot 
tool will respond to the direct message channel with the average of all numbers in that particular channel. Also, bot 
will respond to the group with the average of all numbers found in it, but periodically with the period of one minute,
and only if the channel contains messages written in the last minute.

Slack_bot tool contains Flask application with two routes where one route: ```http://127.0.0.1:5000/average```
is returning the average of numbers found in all channels (public or direct message) where bot is member of. 
Also, there is second route: ```http://127.0.0.1:5000/average/{slack_username}``` which is returning the average of 
numbers found in direct message channel between slack bot and the user with user's username found instead of 
{slack_username}.

The project can be ran successfully if the following instructions are followed:

* Clone the repository:
```
git clone https://github.com/choco-brownies/slack_bot_average.git
```
* In the slack_bot directory create and activate virtual environment:
```
cd slack_bot
virtualenv -p python3 venv
source venv/bin/activate
```
* Install all dependencies from the file requirements.txt:
```
pip install -r requirements.txt
```
* Copy the token of the created Slack bot application to the file slack_bot/plugins/rtmbot.conf in:
```
SLACK_TOKEN: xoxb-slack_bot_token
```
* start slack-bot tool:
```
python start_bot.py
```
* Start the Flask application:
```
python app.py
```