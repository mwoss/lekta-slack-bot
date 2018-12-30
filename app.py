from typing import Dict, Any

from flask import Flask, request, make_response, render_template

from slack_bot.bot import Bot

bot = Bot()
app = Flask(__name__)


def _event_handler(event_type: str, slack_event: Dict[str, Any]):
    """
    Function for handling received Slack event. Handling only known event types.
    :param event_type: Type of received Slack event
    :param slack_event: Dictionary with data from received Slack event
    """
    team_id = slack_event["team_id"]
    user_id = slack_event["event"]["user"]

    if event_type == "message":
        bot.answer(team_id, user_id)
        return make_response("Response from Lekta API sent", 200, )
    elif event_type == "member_joined_channel":
        bot.onboarding_message(team_id, user_id)
        return make_response("Welcome message sent", 200, )
    elif event_type == 'member_left_channel':
        bot.leave_message(team_id, user_id)
        return make_response(f"User with ID: {user_id} left channel", 200, )

    return make_response(f"Could not find handler for event: {event_type}", 404,
                         {"X-Slack-No-Retry": 1})


@app.route("/install", methods=["GET"])
def pre_install():
    return render_template("install.html",
                           client_id=bot.oauth["client_id"],
                           scope=bot.oauth["scope"])


@app.route("/thanks", methods=["GET", "POST"])
def thanks():
    bot.auth(request.args.get('code'))
    return render_template("thanks.html")


@app.route("/events", methods=["GET", "POST"])
def listen():
    """
    Route for incoming events from Slack, request contains json with event data
    """
    slack_event = request.json

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200,
                             {"content_type": "application/json"})

    if bot.verification != slack_event.get("token"):
        return make_response("Verification token invalid. Consider regenerating token :)", 403,
                             {"X-Slack-No-Retry": 1})

    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        from pprint import pprint
        pprint(slack_event)
        return _event_handler(event_type, slack_event)

    return make_response("Error. Event property not provided in response", 404,
                         {"X-Slack-No-Retry": 1})


if __name__ == '__main__':
    app.run(debug=True, port='11000')
