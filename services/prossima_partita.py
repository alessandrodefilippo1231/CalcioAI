import requests
from datetime import datetime, timedelta, timezone

from config import FOOTBALL_API_KEY


def prossima_partita(team_id):

    headers = {
        "x-apisports-key": FOOTBALL_API_KEY
    }


    oggi = datetime.now(timezone.utc)

    da = oggi.strftime("%Y-%m-%d")

    a = (
        oggi + timedelta(days=30)
    ).strftime("%Y-%m-%d")


    url = (
        "https://v3.football.api-sports.io/fixtures"
        f"?team={team_id}"
        f"&from={da}"
        f"&to={a}"
    )


    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )


        dati = response.json()


        print("RICERCA CALENDARIO")
        print("DAL:", da)
        print("AL:", a)
        print("RISULTATI:", dati.get("results"))
        print("ERRORI:", dati.get("errors"))


        partite = dati.get(
            "response",
            []
        )


        for partita in partite:

            stato = partita["fixture"]["status"]["short"]


            if stato == "NS":

                return partita



    except Exception as e:

        print(
            "Errore ricerca partita:",
            e
        )


    return None