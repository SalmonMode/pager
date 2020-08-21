from pypcom import Page

from src.utils.pages.components.login import LoginForm


class LoginPage(Page):

    login_form = LoginForm()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login_form.username.wait_until("visible")

    def login(self, username: str):
        self.login_form.username = username
        self.login_form.submit()
        self.login_form.username.wait_until_not("present")
