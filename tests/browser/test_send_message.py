from datetime import datetime
from uuid import uuid4

import pytest

from src.utils.message import ImageMessage


@pytest.fixture(scope="class", autouse=True)
def message(page, chat_client, username):
    msg = chat_client.get_text_message("hello")
    msg.username = username
    return msg


class TestSendTextMessage:

    @pytest.fixture(scope="class", autouse=True)
    def send_message(self, page, chat_client, message):
        page.send_message(message.text)

    def test_received_text_message_in_history(self, message, chat_client):
        assert message in chat_client._chat_history


class TestSendImageMessage:

    @pytest.fixture(scope="class", autouse=True)
    def send_message(self, page, chat_client):
        page.send_message("/gif test")

    @pytest.fixture(scope="class")
    def time_sent(self, send_message):
        return datetime.now().strftime("%I:%M %p").strip("0").lower()

    @pytest.fixture(scope="class", autouse=True)
    def last_received_message(self, send_message, chat_client):
        return chat_client._chat_history[-1]

    def test_last_received_message_is_image(self, last_received_message):
        assert isinstance(last_received_message, ImageMessage)

    def test_last_received_message_author_is_user(self, last_received_message, username):
        assert last_received_message.username == username

    def test_time_sent_lines_up(self, last_received_message, time_sent):
        assert last_received_message.time == time_sent
