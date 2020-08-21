from datetime import datetime
import json
import random
import re
import string
import threading
from time import time, sleep
from typing import Any, List, Mapping, Tuple, Union, Callable, Dict
from urllib.parse import urljoin, urlencode

from requests import Session
import websocket

from src.utils.types import MessageType, MessageConsumer, Username, IsTyping, MessageData
from src.utils.message import TextMessage, ImageMessage
from src.utils.giphy import get_random_giphy


class WebSocketClient:

    def __init__(self, url: str, sid: str, username: str, **consumers: Mapping[MessageType, MessageConsumer]):
        self._sid = sid
        self.username = username
        query = {
            "username": self.username,
            "EIO": 3,
            "transport": "websocket",
            "sid": self._sid,
        }
        self._uri = urljoin(url.replace("http", "ws"), f"/socket.io/?{urlencode(query)}")
        self.active_typers = []
        self._consumers = {}
        for message_type, consumer_callback in consumers.items():
            self.register_consumer(message_type, consumer_callback)
        self._start_connection()

    def _incoming_message_handler(self, message):
        msg = WebSocketClient.get_deserialized_incoming_message(message)
        if msg:
            self._consume(msg)

    def _start_connection(self):
        self._keep_alive = True
        self._ws = websocket.WebSocketApp(
            self._uri,
            on_message=self._incoming_message_handler,
        )
        self._client_thread = threading.Thread(target=self._ws.run_forever)
        self._client_thread.start()
        timeout = time() + 2
        while time() <= timeout:
            if self._ws.sock.connected:
                break
        else:
            raise Exception("never connected")
        # probe request
        self._ws.send("2probe")
        # apparent followup to probe request
        self._ws.send("5")

    def kill(self):
        self._ws.close()
        self._client_thread.join()

    def send(self, message):
        # the 42 prefixes every message except handshake probe
        self._ws.send(f"42{json.dumps(message)}")
        # suspend thread so others have a chance to process messages they may have
        # received as a result of this message being sent
        sleep(0.1)

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
    def get_deserialized_incoming_message(message: str) -> Dict:
        """Returns the cleaned up and deserialized message."""
        try:
            return json.loads(message.strip(string.digits + ":"))
        except json.decoder.JSONDecodeError:
            return None


class ChatClient:
    def __init__(self, url: str, username: str):
        self._url = url
        self.username = username
        self._sid = None
        self.active_typers = []
        self._chat_history = []
        self._session = Session()
        self.authenticate()
        self.update_chat_history()
        consumers = {
            "message": self.consume_incoming_message,
            "is-typing": self.consume_typing_update,
        }
        self._ws_client = WebSocketClient(self._url, self._sid, self.username, **consumers)

    def kill(self):
        if self.username in self.active_typers:
            self.send_not_typing()
        self._ws_client.kill()

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

        Simply calling ``self.active_typers = []`` again would create a new list, which could
        cause problems. Instead, the contents of the list are wiped out so that anything else
        that has a reference to the list can retain that reference and use it to always have
        an up to date reference. This may also become relevant in the future if a lock is
        needed due to the asynchronous nature of the code.
        """
        del self.active_typers[:]
        self.active_typers.extend([username for username, is_typing in data.items() if is_typing])

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
            self.consume_incoming_message(message[-1])

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

    def handle_close(self, *args, **kwargs):
        self.send_not_typing()

    def send_typing(self):
        self._ws_client.send(["typing", True])

    def send_not_typing(self):
        self._ws_client.send(["typing", False])

    def send_message(self, message: Union[TextMessage, ImageMessage]):
        self._ws_client.send(message.simplify())

    def get_random_gif_message(self, search_text: str) -> ImageMessage:
        giphy = get_random_giphy(search_text)
        return ImageMessage(username=self.username, time=datetime.now(), url=giphy["data"]["image_url"], alt=giphy["data"]["title"])

    def get_text_message(self, text: str) -> TextMessage:
        return TextMessage(username=self.username, time=datetime.now(), text=text)

    @staticmethod
    def get_deserialized_authentication_response(message: str) -> List[Any]:
        """Returns the cleaned up and deserialized authentication response."""
        return json.loads(message.strip(string.digits + ":"))

    @staticmethod
    def get_deserialized_polling_message(message_feed: str) -> List[MessageData]:
        """Returns the cleaned up and deserialized message."""
        messages = re.split(r'(?<=\])\d+:\d+(?=\[)', message_feed.strip(string.digits + ":"))
        return [json.loads(message) for message in messages]
