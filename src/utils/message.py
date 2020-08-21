from dataclasses import dataclass
from datetime import datetime
from time import time
from typing import List, Any, Union


def datetime_from_utc_to_local(utc_datetime):
    now_timestamp = time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset


@dataclass
class TextMessage:
    username: str
    time: Union[str, datetime]
    text: str
    type: str = "text"

    def simplify(self) -> List[str]:
        return ["text-message", self.text]

    def __post_init__(self):
        if isinstance(self.time, datetime):
            self.time = self.time.strftime("%I:%M %p").strip("0")
        elif isinstance(self.time, str) and len(self.time) == 24:
            self.time = datetime_from_utc_to_local(datetime.fromisoformat(self.time[:-1]+"+00:00".upper())).strftime("%I:%M %p").strip("0")
        self.time = self.time.lower()


@dataclass
class ImageMessage:
    username: str
    time: Union[str, datetime]
    url: str
    alt: str
    type: str = "image"

    def simplify(self) -> List[Any]:
        return ["image-message", {"url": self.url, "alt": self.alt}]

    def __post_init__(self):
        if isinstance(self.time, datetime):
            self.time = self.time.strftime("%I:%M %p").strip("0")
        elif isinstance(self.time, str) and len(self.time) == 24:
            self.time = datetime_from_utc_to_local(datetime.fromisoformat(self.time[:-1]+"+00:00".upper())).strftime("%I:%M %p").strip("0")
        self.time = self.time.lower()
