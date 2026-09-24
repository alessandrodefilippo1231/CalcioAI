import requests
from config import FOOTBALL_API_KEY

URL = "https://api.football-data.org/v4/matches"

HEADERS = {
    "X-Auth-Token": FOOTBALL_API_KEY
}


def partite_di_oggi():
    risposta = requests.get(
        URL,
        headers=HEADERS,
        timeout=15
    )

    risposta.raise_for_status()

    return risposta.json()