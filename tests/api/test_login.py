from uuid import uuid4

import pytest

from src.utils.ws_client import ChatClient


@pytest.fixture
def username():
    return str(uuid4())


@pytest.fixture
def chat_client(username):
    client = ChatClient("https://pager-qa-hiring.herokuapp.com/", username)
    yield client
    client.kill()


# has no means of resetting state of chat room, so it will almost always fail
@pytest.mark.refined
def test_user_is_connected(chat_client, username):
    assert chat_client.connected_users == [username]


@pytest.mark.unrefined
def test_user_is_among_those_connected(chat_client, username):
    assert username in chat_client.connected_users
