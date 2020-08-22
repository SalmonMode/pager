from uuid import uuid4

import pytest





class TestShowsTextMessage:

    @pytest.fixture(scope="class", autouse=True)
    def message(self, page, chat_client, username):
        msg = chat_client.get_text_message("hello")
        return msg

    @pytest.fixture(scope="class", autouse=True)
    def send_message(self, page, chat_client, message):
        chat_client.send_message(message)

    def test_received_text_message_in_history(self, message, page):
        assert message in page.chat_history


class TestShowsImageMessage:

    @pytest.fixture(scope="class", autouse=True)
    def message(self, page, chat_client, username):
        msg = chat_client.get_random_gif_message("hhhhhhhh")
        return msg

    @pytest.fixture(scope="class", autouse=True)
    def send_message(self, page, chat_client, message):
        chat_client.send_message(message)

    def test_received_text_message_in_history(self, message, page):
        assert message in page.chat_history
