from pypcom import Page

from src.utils.pages.components.chat import ActiveTypers, Form

class ChatPage(Page):

    active_typers = ActiveTypers()
    form = Form()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.active_typers.wait_until("present")

    def send_message(self, text: str):
        self.form.send_message(text)
