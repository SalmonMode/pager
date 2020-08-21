from uuid import uuid4

import pytest

from src.utils.pages import LoginPage, ChatPage
from src.utils.ws_client import ChatClient


@pytest.fixture(scope="class")
def alternate_username():
    return str(uuid4())


@pytest.fixture(scope="class")
def chat_client(alternate_username, page):
    client = ChatClient("https://pager-qa-hiring.herokuapp.com/", alternate_username)
    yield client
    client.kill()


@pytest.fixture(scope="class")
def username():
    return str(uuid4())


class TestLogin:

    @pytest.fixture(scope="class")
    def login_page(self, driver):
        driver.get("https://pager-qa-hiring.herokuapp.com/#/chat")
        return LoginPage(driver)

    @pytest.fixture(scope="class", autouse=True)
    def login(self, login_page, driver, username):
        login_page.login(username)

    @pytest.fixture(scope="class", autouse=True)
    def page(self, login, driver):
        return ChatPage(driver)

    def test_user_is_online(self, chat_client, username):
        assert username in chat_client.connected_users
