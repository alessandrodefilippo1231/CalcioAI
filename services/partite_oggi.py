import json
import os
import threading
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

from config import FOOTBALL_API_KEY


# ============================================================
# CONFIGURAZIONE
# ============================================================

BASE_URL = "https://api.football-data.org/v4/competitions"

CACHE_FILE = "cache/partite_oggi.json"

HEADERS = {
    "X-Auth-Token": FOOTBALL_API_KEY
}

# Evita che due richieste contemporanee
# interroghino Football-Data.org nello stesso momento.
_RICHIESTA_LOCK = threading.Lock()

# Secondi di attesa prima di ritentare dopo un 429.
RETRY_429_SECONDS = 3


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

    "ELC": {
        "lega": "Championship",
        "paese": "England",
        "priority": 4,
    },

    "PD": {
        "lega": "La Liga",
        "paese": "Spain",
        "priority": 5,
    },

    "BL1": {
        "lega": "Bundesliga",
        "paese": "Germany",
        "priority": 7,
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

def carica_cache(data_richiesta):
    """
    Carica la cache relativa alla data richiesta.

    La nuova cache permette di conservare più date:
    {
        "date": {
            "2026-10-02": [...],
            "2026-10-10": [...]
        }
    }

    Mantiene anche compatibilità con il vecchio formato:
    {
        "data": "2026-10-02",
        "partite": [...]
    }
    """

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

        # ----------------------------------------------------
        # NUOVO FORMATO
        # ----------------------------------------------------

        date_cache = dati.get("date")

        if isinstance(date_cache, dict):

            partite = date_cache.get(
                data_richiesta,
                []
            )

            if isinstance(partite, list) and partite:
                return partite

        # ----------------------------------------------------
        # VECCHIO FORMATO
        # ----------------------------------------------------

        if dati.get("data") == data_richiesta:

            partite = dati.get(
                "partite",
                []
            )

            if isinstance(partite, list) and partite:
                return partite

        return None

    except Exception as e:

        print(
            f"⚠️ ERRORE LETTURA CACHE: {e}"
        )

        return None


def salva_cache(
    data_richiesta,
    partite
):
    """
    Salva le partite associate alla specifica data.

    Non cancella le cache delle altre date.
    """

    os.makedirs(
        os.path.dirname(CACHE_FILE),
        exist_ok=True
    )

    dati = {}

    # --------------------------------------------------------
    # CARICA EVENTUALE CACHE ESISTENTE
    # --------------------------------------------------------

    if os.path.exists(CACHE_FILE):

        try:

            with open(
                CACHE_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                dati = json.load(f)

        except Exception:
            dati = {}

    # --------------------------------------------------------
    # CONVERSIONE DAL VECCHIO FORMATO
    # --------------------------------------------------------

    if not isinstance(dati, dict):
        dati = {}

    date_cache = dati.get(
        "date"
    )

    if not isinstance(date_cache, dict):

        date_cache = {}

        vecchia_data = dati.get(
            "data"
        )

        vecchie_partite = dati.get(
            "partite",
            []
        )

        if (
            vecchia_data
            and isinstance(vecchie_partite, list)
            and vecchie_partite
        ):

            date_cache[
                vecchia_data
            ] = vecchie_partite

    # --------------------------------------------------------
    # AGGIORNA LA DATA
    # --------------------------------------------------------

    date_cache[
        data_richiesta
    ] = partite

    dati = {
        "date": date_cache
    }

    # --------------------------------------------------------
    # SALVATAGGIO
    # --------------------------------------------------------

    try:

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

    except Exception as e:

        print(
            f"⚠️ ERRORE SALVATAGGIO CACHE: {e}"
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

        "id": partita.get(
            "id"
        ),

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
# RECUPERO DI UNA SINGOLA COMPETIZIONE
# ============================================================

def recupera_competizione(
    codice,
    data_richiesta
):

    url = (
        f"{BASE_URL}/"
        f"{codice}/matches"
    )

    print(
        f"🌐 {codice}: "
        f"{data_richiesta}"
    )

    try:

        risposta = requests.get(
            url,
            headers=HEADERS,
            params={
                "dateFrom": data_richiesta,
                "dateTo": data_richiesta,
            },
            timeout=15
        )

        print(
            f"📡 {codice} STATUS: "
            f"{risposta.status_code}"
        )

        # ----------------------------------------------------
        # RATE LIMIT
        # ----------------------------------------------------

        if risposta.status_code == 429:

            print(
                f"⏳ {codice}: "
                f"RATE LIMIT 429"
            )

            return []

        risposta.raise_for_status()

        dati = risposta.json()

        partite = dati.get(
            "matches",
            []
        )

        print(
            f"⚽ {codice}: "
            f"{len(partite)} partite"
        )

        return partite

    except requests.RequestException as e:

        print(
            f"❌ ERRORE {codice}: {e}"
        )

        return []

    except Exception as e:

        print(
            f"❌ ERRORE GENERICO {codice}: {e}"
        )

        return []


# ============================================================
# RECUPERO TUTTE LE COMPETIZIONI
# ============================================================

def recupera_partite(data_richiesta):

    print(
        "\n🌐 RICHIESTA FOOTBALL-DATA.ORG"
    )

    print(
        f"📅 DATA: {data_richiesta}"
    )

    tutte_le_partite = []

    richieste_429 = 0

    for codice in COMPETIZIONI:

        partite = recupera_competizione(
            codice,
            data_richiesta
        )

        if not partite:
            # Non sappiamo se sia realmente 0 partite
            # oppure un errore/rate limit.
            richieste_429 += 1

        tutte_le_partite.extend(
            partite
        )

    print(
        f"📊 TOTALE RISULTATI API: "
        f"{len(tutte_le_partite)}"
    )

    return tutte_le_partite


# ============================================================
# FILTRA + CONVERTE + ORDINA
# ============================================================

def prepara_partite(partite_raw):

    # --------------------------------------------------------
    # FILTRO + CONVERSIONE
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # RIMOZIONE DUPLICATI
    # --------------------------------------------------------

    partite_uniche = {}

    for partita in partite_filtrate:

        fixture_id = partita.get(
            "id"
        )

        if fixture_id is not None:

            partite_uniche[
                fixture_id
            ] = partita

    partite_filtrate = list(
        partite_uniche.values()
    )

    # --------------------------------------------------------
    # ORDINAMENTO
    # --------------------------------------------------------

    partite_filtrate.sort(
        key=lambda x: (
            x.get(
                "priority",
                20
            ),
            x.get(
                "ora",
                "99:99"
            )
        )
    )

    return partite_filtrate


# ============================================================
# RIEPILOGO CAMPIONATI
# ============================================================

def stampa_riepilogo(partite):

    if not partite:
        return

    campionati = {}

    for partita in partite:

        lega = partita.get(
            "lega",
            "Altro"
        )

        campionati[lega] = (
            campionati.get(
                lega,
                0
            ) + 1
        )

    if campionati:

        print(
            "🏆 CAMPIONATI TROVATI:"
        )

        for lega, numero in campionati.items():

            print(
                f"   • {lega}: "
                f"{numero}"
            )


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

    La cache ora è separata per data.

    Esempi:

        partite_oggi()
        -> usa la cache di oggi

        partite_oggi(data_test="2026-10-10")
        -> usa la cache del 10/10 se presente

        partite_oggi(
            forza_aggiornamento=True,
            data_test="2026-10-10"
        )
        -> forza un nuovo recupero API
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

    # ========================================================
    # CACHE
    # ========================================================

    if not forza_aggiornamento:

        cache = carica_cache(
            data_richiesta
        )

        if cache:

            print(
                f"💾 CACHE UTILIZZATA: "
                f"{len(cache)} partite"
            )

            return cache

    # ========================================================
    # BLOCCO RICHIESTE CONTEMPORANEE
    # ========================================================

    with _RICHIESTA_LOCK:

        # ----------------------------------------------------
        # RICONTROLLA LA CACHE DOPO AVER ACQUISITO IL LOCK
        #
        # Questo è fondamentale:
        #
        # Richiesta A entra
        # → API
        # → salva cache
        #
        # Richiesta B aspetta
        # → quando entra trova la cache
        # → NON richiama le API
        # ----------------------------------------------------

        if not forza_aggiornamento:

            cache = carica_cache(
                data_richiesta
            )

            if cache:

                print(
                    f"💾 CACHE UTILIZZATA "
                    f"DOPO ATTESA: "
                    f"{len(cache)} partite"
                )

                return cache

        # ====================================================
        # API
        # ====================================================

        partite_raw = recupera_partite(
            data_richiesta
        )

        # ====================================================
        # FILTRO + CONVERSIONE
        # ====================================================

        partite_filtrate = prepara_partite(
            partite_raw
        )

        print(
            f"✅ PARTITE FILTRATE: "
            f"{len(partite_filtrate)}"
        )

        # ====================================================
        # RIEPILOGO
        # ====================================================

        stampa_riepilogo(
            partite_filtrate
        )

        # ====================================================
        # CONTROLLO RISULTATO
        # ====================================================

        if partite_filtrate:

            salva_cache(
                data_richiesta,
                partite_filtrate
            )

            print(
                f"💾 CACHE AGGIORNATA "
                f"PER {data_richiesta}"
            )

        else:

            print(
                "⚠️ NESSUNA PARTITA "
                "RECUPERATA DALLE API"
            )

            # ------------------------------------------------
            # FALLBACK CACHE
            #
            # Se l'API ha risposto 429 ma avevamo una cache
            # precedente, la utilizziamo.
            # ------------------------------------------------

            cache_precedente = carica_cache(
                data_richiesta
            )

            if cache_precedente:

                print(
                    f"♻️ FALLBACK CACHE: "
                    f"{len(cache_precedente)} partite"
                )

                return cache_precedente

        print(
            f"⚽ Partite trovate: "
            f"{len(partite_filtrate)}"
        )

        return partite_filtrate