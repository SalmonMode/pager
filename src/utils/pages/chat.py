from typing import List, Union

from pypcom import Page

from src.utils.pages.components.chat import ActiveTypers, Form, MessageList
from src.utils.message import TextMessage, ImageMessage

class ChatPage(Page):

    active_typers = ActiveTypers()
    form = Form()
    _message_list = MessageList()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.active_typers.wait_until("present")

    @property
    def chat_history(self) -> List[Union[TextMessage, ImageMessage]]:
        return self._message_list.messages

    def send_message(self, text: str):
        self.form.send_message(text)
