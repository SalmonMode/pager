from pypcom import Page

from src.utils.pages.components.chat import ActiveTypers

class ChatPage(Page):

    active_typers = ActiveTypers()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.active_typers.wait_until("present")
