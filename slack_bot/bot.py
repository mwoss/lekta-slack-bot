import os

from slackclient import SlackClient

# To remember which teams have authorized your app and what tokens are
# associated with each team, we can store this information in memory on
# as a global object. When your bot is out of development, it's best to
# save this in a more persistant memory store.
authed_teams = {}


class Bot:
    name = "lektabot"
    emoji = ":robot_face:"

    def __init__(self):
        self.oauth = {"client_id": os.environ.get("CLIENT_ID"),
                      "client_secret": os.environ.get("CLIENT_SECRET"),
                      "scope": "bot"}
        self.verification = os.environ.get("VERIFICATION_TOKEN")
        self.client = SlackClient("")

    def auth(self, code: str):
        auth_response = self.client.api_call(
            "oauth.access",
            client_id=self.oauth["client_id"],
            client_secret=self.oauth["client_secret"],
            code=code
        )
        team_id = auth_response["team_id"]
        authed_teams[team_id] = {"bot_token": auth_response["bot"]["bot_access_token"]}
        self.client = SlackClient(authed_teams[team_id]["bot_token"])

    def onboarding_message(self, team_id: str, user_id: str):
        text = "Welcome to Slack! We're so glad you're here.\n" \
               "Get started by completing the steps below."
        channel = self._open_dm(user_id)
        self.client.api_call("chat.postMessage",
                             channel=channel,
                             username=self.name,
                             icon_emoji=self.emoji,
                             text=text,
                             )

    def answer(self, team_id, user_id):
        completed_attachments = {"text": ":white_check_mark: "
                                         "~*Share this Message*~ "
                                         ":mailbox_with_mail:",
                                 "color": "#439FE0"}
        # Grab the message object we want to update by team id and user id
        message_obj = self.messages[team_id].get(user_id)
        # Update the message's attachments by switching in incomplete
        # attachment with the completed one above.
        message_obj.share_attachment.update(completed_attachments)
        # Update the message in Slack
        post_message = self.client.api_call("chat.update",
                                            channel=message_obj.channel,
                                            ts=message_obj.timestamp,
                                            text=message_obj.text,
                                            attachments=message_obj.attachments
                                            )
        # Update the timestamp saved on the message object
        message_obj.timestamp = post_message["ts"]

    def leave_message(self):
        pass

    def _open_dm(self, user_id: str):
        new_dm = self.client.api_call("im.open", user=user_id)
        return new_dm["channel"]["id"]
