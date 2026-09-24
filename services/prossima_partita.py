import requests
from datetime import datetime, timedelta, timezone

from config import FOOTBALL_API_KEY


BASE_URL = "https://api.football-data.org/v4"


def prossima_partita(team_id):

    headers = {
        "X-Auth-Token": FOOTBALL_API_KEY
    }

    oggi = datetime.now(timezone.utc)

    da = oggi.strftime("%Y-%m-%d")

    a = (
        oggi + timedelta(days=30)
    ).strftime("%Y-%m-%d")

    url = (
        f"{BASE_URL}/teams/{team_id}/matches"
    )

    params = {
        "dateFrom": da,
        "dateTo": a,
        "status": "SCHEDULED"
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=15
        )

        print("RICERCA CALENDARIO")
        print("TEAM ID:", team_id)
        print("DAL:", da)
        print("AL:", a)
        print("STATUS API:", response.status_code)

        response.raise_for_status()

        dati = response.json()

        partite = dati.get(
            "matches",
            []
        )

        print(
            "RISULTATI:",
            len(partite)
        )

        for partita in partite:

            stato = partita.get(
                "status"
            )

            if stato == "SCHEDULED":

                return {
                    "fixture": {
                        "id": partita.get("id"),
                        "date": partita.get("utcDate"),
                        "status": {
                            "short": "NS",
                            "long": "Not Started"
                        }
                    },
                    "teams": {
                        "home": {
                            "id": partita.get(
                                "homeTeam",
                                {}
                            ).get("id"),
                            "name": partita.get(
                                "homeTeam",
                                {}
                            ).get("name")
                        },
                        "away": {
                            "id": partita.get(
                                "awayTeam",
                                {}
                            ).get("id"),
                            "name": partita.get(
                                "awayTeam",
                                {}
                            ).get("name")
                        }
                    },
                    "league": {
                        "id": partita.get(
                            "competition",
                            {}
                        ).get("id"),
                        "name": partita.get(
                            "competition",
                            {}
                        ).get("name"),
                        "country": partita.get(
                            "area",
                            {}
                        ).get("name")
                    }
                }

        print("NESSUNA PROSSIMA PARTITA TROVATA")

    except Exception as e:

        print(
            "Errore ricerca partita:",
            e
        )

    return None