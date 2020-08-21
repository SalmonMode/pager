from dataclasses import dataclass
from datetime import datetime


@dataclass
class TextMessage:
    type: str
    username: str
    time: datetime
    text: str


@dataclass
class ImageMessage:
    type: str
    username: str
    time: datetime
    url: str
    alt: str
