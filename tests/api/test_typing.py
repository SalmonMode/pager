from uuid import uuid4

import pytest

from src.utils.ws_client import ChatClient


@pytest.fixture
def username():
    return str(uuid4())


@pytest.fixture
def alternate_username():
    return str(uuid4())


@pytest.fixture(autouse=True)
def chat_client(username):
    client = ChatClient("https://pager-qa-hiring.herokuapp.com/", username)
    yield client
    client.kill()


@pytest.fixture(autouse=True)
def alternate_chat_client(username):
    client = ChatClient("https://pager-qa-hiring.herokuapp.com/", alternate_username)
    yield client
    client.kill()


@pytest.fixture
def start_typing(chat_client, alternate_chat_client):
    chat_client.send_typing()


@pytest.fixture
def stop_typing(chat_client, alternate_chat_client):
    chat_client.send_not_typing()


@pytest.mark.refined
def test_user_is_active_typer(start_typing, username, alternate_chat_client):
    assert alternate_chat_client.active_typers == [username]


@pytest.mark.refined
def test_user_is_not_active_typer_after_stopping(stop_typing, alternate_chat_client):
    assert alternate_chat_client.active_typers == []


@pytest.mark.unrefined
def test_user_is_among_active_typers(start_typing, username, alternate_chat_client):
    assert username in alternate_chat_client.active_typers


@pytest.mark.unrefined
def test_user_is_not_among_active_typers_after_stopping(stop_typing, username, alternate_chat_client):
    assert username not in alternate_chat_client.active_typers
