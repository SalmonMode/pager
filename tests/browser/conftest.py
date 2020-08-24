import os
from uuid import uuid4

import pytest
from selenium import webdriver

from src.utils.pages import LoginPage, ChatPage
from src.utils.ws_client import ChatClient


def pytest_collection_modifyitems(items):
    for item in items:
        item.add_marker(pytest.mark.unrefined)


@pytest.fixture(scope="class")
def client_username():
    return str(uuid4())


@pytest.fixture(scope="class")
def chat_client(client_username, page):
    client = ChatClient("https://pager-qa-hiring.herokuapp.com/", client_username)
    yield client
    client.kill()


@pytest.fixture(scope="class")
def username():
    return str(uuid4())


@pytest.fixture(scope="class")
def driver():
    host = os.environ.get("SELENIUM_HOST", "localhost")
    port = os.environ.get("SELENIUM_PORT", "4444")
    command_executor=f"http://{host}:{port}/wd/hub"
    opts = webdriver.ChromeOptions()
    _driver = webdriver.Remote(command_executor=f"http://{host}:{port}/wd/hub", options=opts)
    yield _driver
    _driver.quit()


@pytest.fixture(scope="class")
def login_page(driver):
    driver.get("https://pager-qa-hiring.herokuapp.com/#/chat")
    return LoginPage(driver)


@pytest.fixture(scope="class", autouse=True)
def login(login_page, driver, username):
    login_page.login(username)


@pytest.fixture(scope="class", autouse=True)
def page(login, driver):
    return ChatPage(driver)
