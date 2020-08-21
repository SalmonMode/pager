import asyncio
import json
import random
import re
import string
from typing import Any, List, Mapping, Tuple, Callable, Dict
from urllib.parse import urljoin, urlencode

from requests import Session
import websockets

from src.utils.types import *
from src.utils.message import TextMessage, ImageMessage


class WebSocketClient:

    def __init__(self, url: str, sid: str, username: str, **consumers: Mapping[MessageType, MessageConsumer]):
        self._sid = sid
        self.username = username
        query = {
            "username": self.username,
            "transport": "websocket",
            "EIO": 3,
            "sid": self._sid,
        }
        self._uri = urljoin(url.replace("http", "ws"), f"/socket.io/?{urlencode(query)}")
        self.active_typers = []
        self._consumers = {}
        for message_type, consumer_callback in consumers.items():
            self.register_consumer(message_type, consumer_callback)

    async def _incoming_message_handler(self):
        async for message in self._ws:
            msg = WebSocketClient.get_deserialized_authentication_response(message)
            if msg:
                self._consume(msg)

    async def _start_connection(self):
        self._keep_alive = True
        async with websockets.connect(self._uri) as ws:
            self._ws = ws
            while self._keep_alive:
                await asyncio.sleep(0.001) # put a nominal delay forcing this to wait in event loop

    def kill(self):
        self._keep_alive = False

    def register_consumer(self, message_type: MessageType, callback: MessageConsumer):
        """Register a specific callback for an associated message type.

        This will make sure to pass the message's data to the associated callback as it's received.

        The consumer is used to parse the data and feed it into the relevant storage location. The
        data may be stored as is once the consumer is done with it, or it may be transformed in some
        way.
        """
        self._consumers[message_type] = callback

    def _consume(self, message: List[Tuple[MessageType, Any]]):
        message_type, message_data = message
        consumer = self._consumers.get(message_type)
        if not message_type:
            raise KeyError(f"No registered consumer for message type: {message_type}")
        consumer(message_data)

    @staticmethod
    def get_deserialized_authentication_response(message: str) -> Dict:
        """Returns the cleaned up and deserialized message."""
        return json.loads(message.strip(string.digits + ":"))


class ChatClient:
    def __init__(self, url: str, username: str):
        self._url = url
        self.username = username
        self._sid = None
        self._active_typers = []
        self._chat_history = []
        self._session = Session()
        self.authenticate()
        self.update_chat_history()
        consumers = {
            "message": self.consume_incoming_message,
            "is-typing": self.consume_typing_update,
        }
        self._ws = WebSocketClient(self._url, self._sid, self.username, **consumers)

    def authenticate(self):
        query = {
            "username": self.username,
            "transport": "polling",
            "EIO": 3,
            "t": "".join(random.choices(string.ascii_letters + string.digits, k=7)),
        }
        response = self._session.get(urljoin(self._url, "/socket.io/"), params=query)

        data = ChatClient.get_deserialized_authentication_response(response.text)
        self._sid = data["sid"]

    def consume_typing_update(self, data: Mapping[Username, IsTyping]):
        """Update the list of who is typing.

        The list of who is typing is always overwritten. The most recently received "is-typing"
        dictionary is always the most up to date, and who is typing at that moment is boiled
        down to which members of that dictionary have a value of ``True``. Only members that
        have a value of ``True`` are used to overwrite the contents of the active typers list.

        Simply calling ``self._active_typers = []`` again would create a new list, which could
        cause problems. Instead, the contents of the list are wiped out so that anything else
        that has a reference to the list can retain that reference and use it to always have
        an up to date reference. This may also become relevant in the future if a lock is
        needed due to the asynchronous nature of the code.
        """
        del self._active_typers[:]
        self._active_typers.extend([username for username, is_typing in data if is_typing])

    def update_chat_history(self):
        del self._chat_history[:]
        query = {
            "username": self.username,
            "transport": "polling",
            "EIO": 3,
            "t": str(random.choices(string.ascii_letters + string.digits, k=7)),
            "sid": self._sid,
        }
        response = self._session.get(urljoin(self._url, "/socket.io/"), params=query)
        data = ChatClient.get_deserialized_polling_message(response.text)
        # The last message is always just an message about the current user connecting
        for message in data[:-1]:
            self.consume_incoming_message(message)

    @property
    def connected_users(self) -> List[Username]:
        response = self._session.get(urljoin(self._url, "/connected-users"))
        return response.json()["users"]

    def consume_incoming_message(self, message: Any):
        message["type"] = message["type"]
        if message["type"] == "text":
            self._chat_history.append(TextMessage(**message))
        elif message["type"] == "image":
            self._chat_history.append(ImageMessage(**message))
        else:
            raise TypeError(f"Unknown message type: {message['type']}")

    @staticmethod
    def get_deserialized_authentication_response(message: str) -> List[Any]:
        """Returns the cleaned up and deserialized authentication response."""
        return json.loads(message.strip(string.digits + ":"))

    @staticmethod
    def get_deserialized_polling_message(message_feed: str) -> List[MessageData]:
        """Returns the cleaned up and deserialized message."""
        messages = re.split(r'(?<=\])\d+:\d+(?=\[)', message_feed.strip(string.digits + ":"))
        return [json.loads(message) for message in messages]
