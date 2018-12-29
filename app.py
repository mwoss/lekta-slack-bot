import json
from typing import Dict

from slack_bot.bot import Bot
from flask import Flask, request, make_response

bot = Bot()
app = Flask(__name__)


def _event_handler(event_type: str, slack_event: Dict[str, str]):
    """
    Function for handling received Slack event. Handling only known event types.
    :param event_type: Type of received Slack event
    :param slack_event: Dictionary with data from received Slack event
    :return:
    """
    team_id = slack_event["team_id"]
    # ================ Team Join Events =============== #
    # When the user first joins a team, the type of event will be team_join
    if event_type == "team_join":
        user_id = slack_event["event"]["user"]["id"]
        bot.onboarding_message(team_id, user_id)
        return make_response("Welcome Message Sent", 200, )

    # ============== Share Message Events ============= #
    # If the user has shared the onboarding message, the event type will be
    # message. We'll also need to check that this is a message that has been
    # shared by looking into the attachments for "is_shared".
    elif event_type == "message" and slack_event["event"].get("attachments"):
        user_id = slack_event["event"].get("user")
        if slack_event["event"]["attachments"][0].get("is_share"):
            # Update the onboarding message and check off "Share this Message"
            bot.update_share(team_id, user_id)
            return make_response("Welcome message updates with shared message",
                                 200, )

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/events", methods=["GET", "POST"])
def listen():
    """
    Route for incoming events from Slack, request data contains json with event info
    """
    slack_event = json.loads(request.data)
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
        # Then handle the event by event_type and have your bot respond
        return _event_handler(event_type, slack_event)

    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids you're looking for.", 404,
                         {"X-Slack-No-Retry": 1})


if __name__ == '__main__':
    app.run(debug=True, port='11000')
