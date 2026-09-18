from config import FOOTBALL_API_KEY
import requests


SQUADRE_NOTE = {
    "napoli": {
        "id": 492,
        "nome": "Napoli"
    },
    "juventus": {
        "id": 496,
        "nome": "Juventus"
    },
    "inter": {
        "id": 505,
        "nome": "Inter"
    },
    "milan": {
        "id": 489,
        "nome": "Milan"
    },
    "roma": {
        "id": 497,
        "nome": "Roma"
    },
    "lazio": {
        "id": 487,
        "nome": "Lazio"
    }
}


def cerca_squadra(nome):

    nome = nome.lower().strip()


    # Prima controlla cache locale
    if nome in SQUADRE_NOTE:
        print("✅ USO CACHE SQUADRA:", nome)

        return SQUADRE_NOTE[nome]


    # Se non presente prova API

    url = (
        "https://v3.football.api-sports.io/teams"
        f"?search={nome}"
    )


    headers = {
        "x-apisports-key": FOOTBALL_API_KEY
    }


    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )


        dati = response.json().get("response", [])


        print("RISULTATO API SQUADRA:", len(dati))


        if dati:

            squadra = dati[0]["team"]

            return {
                "id": squadra["id"],
                "nome": squadra["name"]
            }


    except Exception as e:
        print("Errore ricerca squadra:", e)


    return None