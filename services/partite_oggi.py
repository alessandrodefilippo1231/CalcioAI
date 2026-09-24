import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

from config import FOOTBALL_API_KEY


URL = "https://api.football-data.org/v4/matches"

CACHE_FILE = "cache/partite_oggi.json"

HEADERS = {
    "X-Auth-Token": FOOTBALL_API_KEY
}


# ============================================================
# COMPETIZIONI SUPPORTATE
# ============================================================

COMPETIZIONI = {
    "SA": {
        "lega": "Serie A",
        "paese": "Italy",
        "priority": 1,
    },
    "PL": {
        "lega": "Premier League",
        "paese": "England",
        "priority": 3,
    },
    "BL1": {
        "lega": "Bundesliga",
        "paese": "Germany",
        "priority": 7,
    },
    "PD": {
        "lega": "La Liga",
        "paese": "Spain",
        "priority": 5,
    },
    "FL1": {
        "lega": "Ligue 1",
        "paese": "France",
        "priority": 9,
    },
    "DED": {
        "lega": "Eredivisie",
        "paese": "Netherlands",
        "priority": 20,
    },
    "PPL": {
        "lega": "Primeira Liga",
        "paese": "Portugal",
        "priority": 20,
    },
    "ELC": {
        "lega": "Championship",
        "paese": "England",
        "priority": 4,
    },
    "BSA": {
        "lega": "Serie A Brasile",
        "paese": "Brazil",
        "priority": 20,
    },
}


# ============================================================
# DATA ITALIANA
# ============================================================

def data_oggi_italia():
    return datetime.now(
        ZoneInfo("Europe/Rome")
    ).strftime("%Y-%m-%d")


# ============================================================
# CACHE
# ============================================================

def carica_cache():
    if not os.path.exists(CACHE_FILE):
        return None

    try:
        with open(
            CACHE_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            dati = json.load(f)

        if not isinstance(dati, dict):
            return None

        if dati.get("data") != data_oggi_italia():
            return None

        partite = dati.get(
            "partite",
            []
        )

        if not partite:
            return None

        return partite

    except Exception:
        return None


def salva_cache(partite):
    os.makedirs(
        os.path.dirname(CACHE_FILE),
        exist_ok=True
    )

    dati = {
        "data": data_oggi_italia(),
        "partite": partite
    }

    with open(
        CACHE_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            dati,
            f,
            ensure_ascii=False,
            indent=2
        )


# ============================================================
# FILTRO PARTITE
# ============================================================

def partita_valida(partita):
    competition = partita.get(
        "competition",
        {}
    )

    code = competition.get(
        "code",
        ""
    )

    if code not in COMPETIZIONI:
        return False

    nome_competizione = competition.get(
        "name",
        ""
    ).lower()

    home_team = partita.get(
        "homeTeam",
        {}
    )

    away_team = partita.get(
        "awayTeam",
        {}
    )

    casa = home_team.get(
        "name",
        ""
    )

    trasferta = away_team.get(
        "name",
        ""
    )

    testo = (
        f"{nome_competizione} "
        f"{casa} "
        f"{trasferta}"
    ).lower()

    esclusioni = [
        "women",
        "woman",
        "female",
        " w ",
        "u19",
        "u20",
        "u21",
        "u23",
        "youth",
        "reserve",
        "reserves",
        " ii ",
        "friendly",
        "friendlies",
        "club friendly",
        "amateur",
    ]

    for parola in esclusioni:
        if parola in testo:
            return False

    return True


# ============================================================
# CONVERSIONE FOOTBALL-DATA → FORMATO CALCIOAI
# ============================================================

def converti_partita(partita):
    competition = partita.get(
        "competition",
        {}
    )

    code = competition.get(
        "code",
        ""
    )

    info_competizione = COMPETIZIONI.get(
        code,
        {}
    )

    home_team = partita.get(
        "homeTeam",
        {}
    )

    away_team = partita.get(
        "awayTeam",
        {}
    )

    utc_date = partita.get(
        "utcDate",
        ""
    )

    try:
        dt_utc = datetime.fromisoformat(
            utc_date.replace(
                "Z",
                "+00:00"
            )
        )

        dt_italia = dt_utc.astimezone(
            ZoneInfo("Europe/Rome")
        )

        ora = dt_italia.strftime(
            "%H:%M"
        )

        data_italia = dt_italia.strftime(
            "%Y-%m-%d"
        )

    except Exception:
        ora = ""
        data_italia = ""

    return {
        "id": partita.get("id"),

        "casa": home_team.get(
            "name",
            ""
        ),

        "trasferta": away_team.get(
            "name",
            ""
        ),

        "home_id": home_team.get(
            "id"
        ),

        "away_id": away_team.get(
            "id"
        ),

        "lega": info_competizione.get(
            "lega",
            competition.get(
                "name",
                ""
            )
        ),

        "paese": info_competizione.get(
            "paese",
            ""
        ),

        "ora": ora,

        "data": data_italia,

        "date": utc_date,

        "priority": info_competizione.get(
            "priority",
            20
        ),
    }


# ============================================================
# RECUPERO PARTITE DA FOOTBALL-DATA.ORG
# ============================================================

def recupera_partite(data_richiesta):
    print(
        f"🌐 RICHIESTA FOOTBALL-DATA.ORG: "
        f"{data_richiesta}"
    )

    try:
        risposta = requests.get(
            URL,
            headers=HEADERS,
            params={
                "dateFrom": data_richiesta,
                "dateTo": data_richiesta,
            },
            timeout=15
        )

        print(
            f"📡 STATUS API: "
            f"{risposta.status_code}"
        )

        risposta.raise_for_status()

        dati = risposta.json()

        partite = dati.get(
            "matches",
            []
        )

        print(
            f"📊 RISULTATI API: "
            f"{len(partite)}"
        )

        return partite

    except requests.RequestException as e:
        print(
            f"❌ ERRORE FOOTBALL-DATA.ORG: {e}"
        )
        return []

    except Exception as e:
        print(
            f"❌ ERRORE GENERICO API: {e}"
        )
        return []


# ============================================================
# FUNZIONE PRINCIPALE
# ============================================================

def partite_oggi(
    forza_aggiornamento=False,
    data_test=None
):
    """
    Recupera le partite del giorno.

    data_test permette di utilizzare
    una data specifica per i test.
    """

    data_richiesta = (
        data_test
        if data_test
        else data_oggi_italia()
    )

    print(
        "\n🌐 WEB APP - CARICAMENTO PARTITE"
    )

    print(
        f"📅 DATA CALCIOAI: "
        f"{data_richiesta}"
    )

    usa_cache = (
        data_test is None
        and not forza_aggiornamento
    )

    if usa_cache:
        cache = carica_cache()

        if cache:
            print(
                f"💾 CACHE UTILIZZATA: "
                f"{len(cache)} partite"
            )

            return cache

    partite_raw = recupera_partite(
        data_richiesta
    )

    partite_filtrate = []

    for partita in partite_raw:

        if not partita_valida(partita):
            continue

        partita_convertita = converti_partita(
            partita
        )

        partite_filtrate.append(
            partita_convertita
        )

    # Ordina per priorità del campionato
    # e successivamente per orario
    partite_filtrate.sort(
        key=lambda x: (
            x.get("priority", 20),
            x.get("ora", "99:99")
        )
    )

    print(
        f"✅ PARTITE FILTRATE: "
        f"{len(partite_filtrate)}"
    )

    if (
        data_test is None
        and partite_filtrate
    ):
        salva_cache(
            partite_filtrate
        )

        print(
            "💾 CACHE AGGIORNATA"
        )

    elif not partite_filtrate:
        print(
            "⚠️ NESSUNA PARTITA: "
            "cache non aggiornata"
        )

    print(
        f"⚽ Partite trovate: "
        f"{len(partite_filtrate)}"
    )

    return partite_filtrate