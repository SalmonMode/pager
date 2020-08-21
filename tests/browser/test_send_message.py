from uuid import uuid4

import pytest


@pytest.fixture(scope="class", autouse=True)
def message(page, chat_client, username):
    msg = chat_client.get_text_message("hello")
    msg.username = username
    return msg


class TestSendMessage:

    @pytest.fixture(scope="class", autouse=True)
    def send_message(self, page, chat_client, message):
        page.send_message(message.text)

    def test_received_text_message_in_history(self, message, chat_client):
        assert message in chat_client._chat_history
