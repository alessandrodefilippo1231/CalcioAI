import requests

from config import FOOTBALL_API_KEY


BASE_URL = "https://api.football-data.org/v4"


# ID DELLE SQUADRE SU FOOTBALL-DATA.ORG
SQUADRE_NOTE = {
    "napoli": {
        "id": 113,
        "nome": "SSC Napoli"
    },
    "juventus": {
        "id": 109,
        "nome": "Juventus FC"
    },
    "inter": {
        "id": 108,
        "nome": "FC Internazionale Milano"
    },
    "milan": {
        "id": 98,
        "nome": "AC Milan"
    },
    "roma": {
        "id": 100,
        "nome": "AS Roma"
    },
    "lazio": {
        "id": 110,
        "nome": "SS Lazio"
    }
}


def cerca_squadra(nome):

    nome = nome.lower().strip()

    # ---------------------------------------------------------
    # 1. CONTROLLA CACHE LOCALE
    # ---------------------------------------------------------

    if nome in SQUADRE_NOTE:

        print("✅ USO CACHE SQUADRA:", nome)

        return SQUADRE_NOTE[nome]

    # ---------------------------------------------------------
    # 2. RICERCA NELLE COMPETIZIONI PRINCIPALI
    # ---------------------------------------------------------

    headers = {
        "X-Auth-Token": FOOTBALL_API_KEY
    }

    competizioni = [
        "SA",    # Serie A
        "PL",    # Premier League
        "BL1",   # Bundesliga
        "PD",    # La Liga
        "FL1",   # Ligue 1
        "DED",   # Eredivisie
        "PPL"    # Primeira Liga
    ]

    try:

        for competizione in competizioni:

            url = (
                f"{BASE_URL}/competitions/"
                f"{competizione}/teams"
            )

            response = requests.get(
                url,
                headers=headers,
                timeout=15
            )

            if response.status_code != 200:
                continue

            dati = response.json()

            squadre = dati.get(
                "teams",
                []
            )

            for squadra in squadre:

                nome_api = squadra.get(
                    "name",
                    ""
                )

                short_name = squadra.get(
                    "shortName",
                    ""
                )

                tla = squadra.get(
                    "tla",
                    ""
                )

                valori = [
                    nome_api,
                    short_name,
                    tla
                ]

                for valore in valori:

                    if not valore:
                        continue

                    valore_normalizzato = (
                        valore
                        .lower()
                        .strip()
                    )

                    if (
                        nome == valore_normalizzato
                        or nome in valore_normalizzato
                    ):

                        risultato = {
                            "id": squadra.get("id"),
                            "nome": nome_api
                        }

                        print(
                            "✅ SQUADRA TROVATA:",
                            risultato
                        )

                        return risultato

        print(
            "⚠️ SQUADRA NON TROVATA:",
            nome
        )

    except Exception as e:

        print(
            "Errore ricerca squadra:",
            e
        )

    return None