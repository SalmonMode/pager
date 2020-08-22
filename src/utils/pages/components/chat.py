from typing import List, Union

from selenium.webdriver.common.by import By
from pypcom import PC

from src.utils.message import TextMessage, ImageMessage


class MessageLineItem(PC):
    _index = None
    _find_from_parent = True
    __locator = ".//div[contains(concat(' ', normalize-space(@class), ' '), ' message-line ')][{index}]"

    @property
    def _locator(self) -> tuple:
        return (By.XPATH, self.__locator.format(index=self._index + 1))

    def __init__(self, index: int, parent: PC):
        self._index = index
        self._parent = parent
        self.driver = self._parent.driver

    @property
    def is_image(self):
        return bool(self.find_elements(By.CSS_SELECTOR, "img"))

    @property
    def image_src(self):
        return self.find_element(By.CSS_SELECTOR, "img").get_attribute("src")

    @property
    def image_alt(self):
        return self.find_element(By.CSS_SELECTOR, "img").get_attribute("alt")


class MessageBlockTitle(PC):
    _find_from_parent = True
    _locator = (By.CSS_SELECTOR, ".title")


class MessageBlockItem(PC):
    __locator = ".message-slot:nth-of-type({index})"
    _item_locator = (By.CSS_SELECTOR, ".message-line")

    title = MessageBlockTitle()

    @property
    def _locator(self) -> tuple:
        return (By.CSS_SELECTOR, self.__locator.format(index=self._index + 1))

    def __init__(self, index: int, parent: PC):
        self._index = index
        self._parent = parent
        self.driver = self._parent.driver

    @property
    def message_line_count(self) -> int:
        return len(self.find_elements(*self._item_locator))

    @property
    def message_line_items(self) -> List[MessageLineItem]:
        return list(MessageLineItem(i, self) for i in range(self.message_line_count))

    @property
    def messages(self) -> List[Union[TextMessage, ImageMessage]]:
        _messages = []
        for msg in self.message_line_items:
            if msg.is_image:
                message = ImageMessage(username=self.username, time=self.time, url=msg.image_src, alt=msg.image_alt)
            else:
                message = TextMessage(username=self.username, time=self.time, text=msg.text)
            _messages.append(message)
        return _messages

    @property
    def username(self) -> str:
        return self.title.text[:-8].strip()

    @property
    def time(self) -> str:
        return self.title.text[-8:].strip()


class MessageList(PC):
    _locator = (By.CSS_SELECTOR, ".messages")
    _item_locator = (By.CSS_SELECTOR, ".message-slot")

    @property
    def message_block_count(self) -> int:
        return len(self.find_elements(*self._item_locator))

    @property
    def message_blocks_items(self) -> List[MessageBlockItem]:
        return list(MessageBlockItem(i, self) for i in range(self.message_block_count))

    @property
    def messages(self) -> List[Union[TextMessage, ImageMessage]]:
        _messages = []
        for message_block in self.message_blocks_items:
            _messages.extend(message_block.messages)
        return _messages


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
