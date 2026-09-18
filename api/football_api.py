import requests
from config import FOOTBALL_API_KEY

URL = "https://v3.football.api-sports.io/fixtures"

HEADERS = {
    "x-apisports-key": FOOTBALL_API_KEY
}


def partite_di_oggi():
    params = {
        "live": "all"
    }

    risposta = requests.get(URL, headers=HEADERS, params=params)

    return risposta.json()