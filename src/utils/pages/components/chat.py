from selenium.webdriver.common.by import By

from pypcom import PC


class Input(PC):

    _find_from_parent = True
    _locator = (By.CSS_SELECTOR, "input")


class SendButton(PC):

    _find_from_parent = True
    _locator = (By.CSS_SELECTOR, "button")


class Form(PC):

    _locator = (By.CSS_SELECTOR, ".btn-container")

    text_input = Input()
    send_button = SendButton()

    def submit(self):
        """Submit the form.

        There is no actual form, so the only away to submit the username to log
        in is to click the send button.
        """
        self.send_button.click()

    def send_message(self, text: str):
        self.text_input = text
        self.submit()


class ActiveTypers(PC):

    _locator = (By.CSS_SELECTOR, ".users-typing")
