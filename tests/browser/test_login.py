import pytest


@pytest.mark.unrefined
class TestLogin:

    def test_user_is_online(self, chat_client, username):
        assert username in chat_client.connected_users
