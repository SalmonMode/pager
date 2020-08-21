from typing import Any, Callable, List, Mapping, Tuple, Union

from src.utils.message import ImageMessage, TextMessage


MessageType = str
MessageConsumer = Callable[[Any], None]
Username = str
IsTyping = bool
ConnectedUserMessage = Tuple[MessageType, Username]
MessageData = Union[TextMessage, ImageMessage, ConnectedUserMessage]
Message = Tuple[MessageType, MessageData]
MessageHistory = List[MessageData]
