from selenium.webdriver.common.by import By

from pypcom import PC


class ActiveTypers(PC):

    _locator = (By.CSS_SELECTOR, ".users-typing")
