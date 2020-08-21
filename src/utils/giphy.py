from dataclasses import dataclass
from typing import Any

import requests


def get_random_giphy(search_text: str) -> Any:
    data = {
        "api_key": "cHuezmxGygeqPfQ63lAvzDrcMIY6fgXt",
        "tag": search_text,
        "rating": "G",
    }
    response = requests.get("https://api.giphy.com/v1/gifs/random", params=data)
    return response.json()
