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
def text_message(chat_client):
    return chat_client.get_text_message("hello")


@pytest.fixture
def image_message(chat_client):
    return chat_client.get_random_gif_message("hello")


@pytest.fixture
def send_text_message(chat_client, text_message):
    chat_client.send_message(text_message)


@pytest.fixture
def send_image_message(chat_client, image_message):
    chat_client.send_message(image_message)


@pytest.mark.refined
def test_received_text_message(send_text_message, text_message, alternate_chat_client):
    assert alternate_chat_client._chat_history == [text_message]


@pytest.mark.refined
def test_received_image_message(send_image_message, image_message, alternate_chat_client):
    assert alternate_chat_client._chat_history == [image_message]


@pytest.mark.unrefined
def test_received_text_message_in_history(send_text_message, text_message, alternate_chat_client):
    assert text_message in alternate_chat_client._chat_history


@pytest.mark.unrefined
def test_received_image_message_in_history(send_image_message, image_message, alternate_chat_client):
    assert image_message in alternate_chat_client._chat_history
