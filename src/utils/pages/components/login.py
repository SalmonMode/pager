from selenium.webdriver.common.by import By

from pypcom import PC


class NextButton(PC):

    _locator = (By.CSS_SELECTOR, "button")


class UsernameField(PC):

    _locator = (By.CSS_SELECTOR, ".username-input")


class LoginForm(PC):

    _locator = (By.CSS_SELECTOR, ".box")

    username = UsernameField()
    next_button = NextButton()

    def submit(self):
        """Submit the form.

        There is no actual form, so the only away to submit the username to log
        in is to click the next button.
        """
        self.next_button.click()
