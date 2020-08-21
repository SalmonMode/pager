import pytest
from selenium import webdriver


@pytest.fixture(scope="class")
def driver():
    opts = webdriver.ChromeOptions()
    _driver = webdriver.Remote(options=opts)
    yield _driver
    _driver.quit()
