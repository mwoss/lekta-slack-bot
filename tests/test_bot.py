from unittest import TestCase
from unittest.mock import patch, Mock, MagicMock, PropertyMock

from slack_bot.bot import Bot
from slack_bot.lekta.sandwich_api import OpenResponse


@patch("slack_bot.bot.SandwichAPI", name='mock_api')
@patch("slack_bot.bot.SlackClient", name='mock_slack')
class TestBot(TestCase):

    @patch("slack_bot.bot.user_dialogues")
    def test_should_open_new_dialogue(self, mock_slack, mock_api, mock_user_dial):
        user_uuid = 'user_uuid'
        mock_user_dial = MagicMock(spec_set=dict)
        mock_user_dial.__getitem__.side_effect = self.sss
        mock_api.open_dialogue.return_value = OpenResponse(user_uuid, 'answer', 'language')

        result_uuid = self.bot._get_user_dialogue(user_uuid)

        self.assertEquals(user_uuid, result_uuid)
        mock_api.open_dialogue.assert_called_once()

    @patch("slack_bot.bot.user_dialogues")
    def test_should_return_existing_dialogue_id(self, mock_slack, mock_api, mock_user_dial):
        user_uuid = 'user_uuid'
        user_id = 'user_id'
        mock_user_dial.return_value = {user_id: user_uuid}
        mock_api.open_dialogue.return_value = OpenResponse(user_uuid, 'answer', 'language')

        result_uuid = self.bot._get_user_dialogue(user_id)

        self.assertEquals(user_uuid, result_uuid)

    @patch("slack_bot.bot.user_dialogues")
    def test_should_remove_user(self, mock_slack, mock_api, mock_user_dial):
        bot = Bot()
        user_uuid = 'user_uuid'
        user_id = 'user_id'
        mock_dict = {user_id: user_uuid}
        mock_user_dial.__getitem__.side_effect = mock_dict.__getitem__

        bot.remove_user(user_id)

        self.assertDictEqual()
        mock_api.return_value.close_dialogue.assert_called_once_with()

    @patch("slack_bot.bot.Bot._get_user_dialogue", Mock())
    def test_should_answer_to_direct_user(self, mock_slack, mock_api):
        bot = Bot()
        text = '@lekta text'

        bot.answer(Mock(spec=str), Mock(spec=str), text)

        mock_api.return_value.make_dialogue.assert_called_once()
        mock_slack.return_value.api_call.assert_called_once()

    def test_should_welcome_direct_user(self, mock_slack, mock_api):
        bot = Bot()
        mock_api.open_dialogue.return_value = PropertyMock()

        bot.welcome_user(Mock(spec=str), Mock(spec=str))

        mock_slack.return_value.api_call.assert_called_once()
