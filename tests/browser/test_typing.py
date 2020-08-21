from uuid import uuid4

import pytest


class TestTyping:

    @pytest.fixture(scope="class", autouse=True)
    def start_typing(self, page, chat_client):
        chat_client.send_typing()

    def test_typing_is_indicated(self, page, client_username):
        assert page.active_typers.text == f"{client_username} is typing..."
