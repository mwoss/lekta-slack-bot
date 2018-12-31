from os import environ
from uuid import UUID

from slackclient import SlackClient

from slack_bot.lekta.sandwich_api import SandwichAPI

# To remember which teams have authorized your app and which user open dialogue
# we can store this information in memory on as a global object. (for clarity it's only for development environment)
# In production it's best to save this in a more persistant memory store.
authed_teams = {}
user_dialogues = {}


class Bot:
    name = 'lektabot'
    emoji = ':robot_face:'

    def __init__(self):
        self.oauth = {'client_id': environ.get('CLIENT_ID'),
                      'client_secret': environ.get('CLIENT_SECRET'),
                      'scope': 'bot'}
        self.verification = environ.get('VERIFICATION_TOKEN')
        self.client = SlackClient(environ.get('BOT_OAUTH_TOKEN'))
        self.sandwich_api = SandwichAPI()

    def auth(self, code: str):
        auth_response = self.client.api_call(
            'oauth.access',
            client_id=self.oauth['client_id'],
            client_secret=self.oauth['client_secret'],
            code=code
        )
        team_id = auth_response['team_id']
        authed_teams[team_id] = {'bot_token': auth_response['bot']['bot_access_token']}
        self.client = SlackClient(authed_teams[team_id]["bot_token"])

    def welcome_user(self, channel: str, user_id: str):
        open_response = self.sandwich_api.open_dialogue()
        user_dialogues[user_id] = open_response.uuid

        self.client.api_call("chat.postMessage",
                             channel=channel,
                             text=f"Welcome to this channel <@{user_id}>! We're so glad you're here.",
                             username=self.name,
                             icon_emoji=self.emoji
                             )

    def answer(self, channel: str, user_id: str, text: str):
        clear_text = text.split(' ', 1)[1]
        dialogue_response = self.sandwich_api.make_dialogue(self._get_user_dialogue(user_id),
                                                            clear_text)
        self.client.api_call("chat.postMessage",
                             channel=channel,
                             text=f"<@{user_id}> {dialogue_response.answer}",
                             username=self.name,
                             icon_emoji=self.emoji
                             )

    def remove_user(self, user_id: str):
        self.sandwich_api.close_dialogue(user_dialogues[user_id])
        user_dialogues.pop(user_id, None)

    def _get_user_dialogue(self, user_id: str) -> UUID:
        try:
            return user_dialogues[user_id]
        except KeyError:
            open_response = self.sandwich_api.open_dialogue()
            user_dialogues[user_id] = open_response.uuid
            return open_response.uuid
