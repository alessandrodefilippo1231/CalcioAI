import os
import json
import requests

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from dotenv import load_dotenv


# ============================================================
# CONFIGURAZIONE
# ============================================================

load_dotenv()

FOOTBALL_API_KEY = os.getenv(
    "FOOTBALL_API_KEY"
)

API_URL = (
    "https://v3.football.api-sports.io/fixtures"
)

CACHE_FILE = (
    "cache/partite_oggi.json"
)

# Fuso orario utilizzato da CalcioAI
TIMEZONE_ITALIA = ZoneInfo(
    "Europe/Rome"
)


# ============================================================
# LEAGUE CONSENTITE
# ============================================================

LEAGUE_CONSENTITE = {

    # Italia
    "Italy": [
        "Serie A",
        "Serie B"
    ],

    # Inghilterra
    "England": [
        "Premier League",
        "Championship"
    ],

    # Spagna
    "Spain": [
        "La Liga",
        "Segunda Division"
    ],

    # Germania
    "Germany": [
        "Bundesliga",
        "2. Bundesliga"
    ],

    # Francia
    "France": [
        "Ligue 1",
        "Ligue 2"
    ],

    # Olanda
    "Netherlands": [
        "Eredivisie"
    ],

    # Portogallo
    "Portugal": [
        "Primeira Liga"
    ],

    # Belgio
    "Belgium": [
        "Jupiler Pro League"
    ],

    # Turchia
    "Turkey": [
        "Super Lig"
    ],

    # Argentina
    "Argentina": [
        "Liga Profesional Argentina"
    ],

    # Brasile
    "Brazil": [
        "Serie A",
        "Serie B"
    ],

    # Messico
    "Mexico": [
        "Liga MX"
    ],

    # Colombia
    "Colombia": [
        "Primera A"
    ],

    # Ecuador
    "Ecuador": [
        "Liga Pro"
    ],

    # USA
    "USA": [
        "Major League Soccer"
    ]
}


# ============================================================
# PAROLE DA ESCLUDERE
# ============================================================

PAROLE_ESCLUSE = [

    "Women",
    "W",
    "U19",
    "U20",
    "U21",
    "U23",
    "Youth",
    "Reserve",
    "Reserves",
    "II",
    "Friendly",
    "Friendlies",
    "Club Friendlies",
    "Amateur"
]


# ============================================================
# CREA CARTELLA CACHE
# ============================================================

def crea_cache():

    cartella = os.path.dirname(
        CACHE_FILE
    )

    if cartella:

        os.makedirs(
            cartella,
            exist_ok=True
        )


# ============================================================
# DATA ODIERNA ITALIANA
# ============================================================

def data_oggi_italia():

    return datetime.now(
        TIMEZONE_ITALIA
    ).strftime(
        "%Y-%m-%d"
    )


# ============================================================
# CONTROLLO PARTITA VALIDA
# ============================================================

def partita_valida(partita):

    fixture = partita.get(
        "fixture",
        {}
    )

    league = partita.get(
        "league",
        {}
    )

    teams = partita.get(
        "teams",
        {}
    )

    casa = teams.get(
        "home",
        {}
    ).get(
        "name",
        ""
    )

    trasferta = teams.get(
        "away",
        {}
    ).get(
        "name",
        ""
    )

    nome_campionato = league.get(
        "name",
        ""
    )

    paese = league.get(
        "country",
        ""
    )

    # --------------------------------------------------------
    # CONTROLLO CAMPIONATO
    # --------------------------------------------------------

    campionati_paese = (
        LEAGUE_CONSENTITE.get(
            paese,
            []
        )
    )

    if nome_campionato not in campionati_paese:

        return False

    # --------------------------------------------------------
    # CONTROLLO NOMI ESCLUSI
    # --------------------------------------------------------

    testo = (
        f"{nome_campionato} "
        f"{casa} "
        f"{trasferta}"
    ).lower()

    for parola in PAROLE_ESCLUSE:

        if parola.lower() in testo:

            return False

    # --------------------------------------------------------
    # CONTROLLO SQUADRE
    # --------------------------------------------------------

    if not casa or not trasferta:

        return False

    # --------------------------------------------------------
    # CONTROLLO DATA
    # --------------------------------------------------------

    data_partita = fixture.get(
        "date"
    )

    if not data_partita:

        return False

    return True


# ============================================================
# PRIORITÀ CAMPIONATO
# ============================================================

def priorita_campionato(
    paese,
    campionato
):

    priorita = {

        "Serie A": 10,
        "Premier League": 10,
        "La Liga": 10,
        "Bundesliga": 10,
        "Ligue 1": 10,

        "Serie B": 8,
        "Championship": 8,
        "Segunda Division": 8,
        "2. Bundesliga": 8,
        "Ligue 2": 8,

        "Eredivisie": 7,
        "Primeira Liga": 7,
        "Jupiler Pro League": 7,
        "Super Lig": 7,

        "Liga Profesional Argentina": 7,
        "Serie A Brazil": 7,
        "Serie B Brazil": 6,

        "Liga MX": 6,
        "Primera A": 6,
        "Liga Pro": 6,
        "Major League Soccer": 6
    }

    return priorita.get(
        campionato,
        5
    )


# ============================================================
# SALVA CACHE
# ============================================================

def salva_cache(
    partite,
    data_cache=None
):

    try:

        crea_cache()

        if data_cache is None:

            data_cache = data_oggi_italia()

        # ----------------------------------------------------
        # NUOVA STRUTTURA CACHE
        # ----------------------------------------------------

        dati_cache = {

            "data": data_cache,

            "partite": partite

        }

        with open(
            CACHE_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                dati_cache,
                file,
                ensure_ascii=False,
                indent=4
            )

        print(
            "💾 CACHE PARTITE SALVATA:",
            len(partite),
            "| DATA:",
            data_cache
        )

    except Exception as e:

        print(
            "❌ ERRORE SALVATAGGIO CACHE:",
            e
        )


# ============================================================
# CARICA CACHE
# ============================================================

def carica_cache():

    try:

        if not os.path.exists(
            CACHE_FILE
        ):

            return None

        with open(
            CACHE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            dati = json.load(
                file
            )

        # ====================================================
        # NUOVA CACHE
        # ====================================================

        if isinstance(
            dati,
            dict
        ):

            data_cache = dati.get(
                "data"
            )

            partite = dati.get(
                "partite"
            )

            if not isinstance(
                partite,
                list
            ):

                print(
                    "⚠️ CACHE NON VALIDA"
                )

                return None

            oggi = data_oggi_italia()

            if data_cache != oggi:

                print(
                    "🗑️ CACHE VECCHIA:",
                    data_cache,
                    "| OGGI:",
                    oggi
                )

                return None

            print(
                "📦 CACHE VALIDA:",
                len(partite),
                "| DATA:",
                data_cache
            )

            return partite

        # ====================================================
        # VECCHIA CACHE LEGACY
        # ====================================================
        #
        # Se il vecchio file contiene direttamente una lista,
        # NON la utilizziamo.
        #
        # In questo modo evitiamo di utilizzare accidentalmente
        # la cache di ieri.
        # ====================================================

        if isinstance(
            dati,
            list
        ):

            print(
                "⚠️ CACHE LEGACY RILEVATA"
            )

            print(
                "🔄 CACHE VECCHIA IGNORATA"
            )

            return None

        return None

    except Exception as e:

        print(
            "⚠️ ERRORE LETTURA CACHE:",
            e
        )

        return None


# ============================================================
# PARTITE DI OGGI
# ============================================================

def partite_oggi(
    forza_aggiornamento=False
):

    oggi = data_oggi_italia()

    print(
        "📅 DATA CALCIOAI:",
        oggi
    )

    # ========================================================
    # CACHE
    # ========================================================

    if not forza_aggiornamento:

        cache = carica_cache()

        if cache is not None:

            print(
                "📦 USO CACHE PARTITE:",
                len(cache)
            )

            print(
                "✅ USO CACHE DEL GIORNO:",
                oggi
            )

            return cache

    else:

        print(
            "🔄 AGGIORNAMENTO FORZATO PARTITE"
        )

    # ========================================================
    # API KEY
    # ========================================================

    if not FOOTBALL_API_KEY:

        print(
            "❌ FOOTBALL_API_KEY NON TROVATA"
        )

        return []

    # ========================================================
    # RICHIESTA API
    # ========================================================

    headers = {

        "x-apisports-key":
            FOOTBALL_API_KEY

    }

    # --------------------------------------------------------
    # IMPORTANTE:
    # L'API-Football lavora con la data richiesta.
    # Utilizziamo la data italiana del giorno corrente.
    # --------------------------------------------------------

    params = {

        "date": oggi

    }

    print(
        "🌐 RICHIESTA API PARTITE:",
        oggi
    )

    try:

        response = requests.get(

            API_URL,

            headers=headers,

            params=params,

            timeout=15

        )

    except Exception as e:

        print(
            "❌ ERRORE API PARTITE:",
            e
        )

        return []

    # ========================================================
    # STATUS HTTP
    # ========================================================

    if response.status_code != 200:

        print(
            "❌ API ERROR:",
            response.status_code
        )

        try:

            print(
                response.text
            )

        except Exception:

            pass

        return []

    # ========================================================
    # JSON
    # ========================================================

    try:

        dati = response.json()

    except Exception as e:

        print(
            "❌ ERRORE JSON:",
            e
        )

        return []

    risultati = dati.get(
        "response",
        []
    )

    print(
        "📊 RISULTATI API:",
        len(risultati)
    )

    # ========================================================
    # FILTRAGGIO
    # ========================================================

    partite = []

    for partita in risultati:

        try:

            if not partita_valida(
                partita
            ):

                continue

            fixture = partita.get(
                "fixture",
                {}
            )

            league = partita.get(
                "league",
                {}
            )

            teams = partita.get(
                "teams",
                {}
            )

            fixture_id = fixture.get(
                "id"
            )

            data_completa = fixture.get(
                "date"
            )

            casa = teams.get(
                "home",
                {}
            ).get(
                "name"
            )

            trasferta = teams.get(
                "away",
                {}
            ).get(
                "name"
            )

            home_id = teams.get(
                "home",
                {}
            ).get(
                "id"
            )

            away_id = teams.get(
                "away",
                {}
            ).get(
                "id"
            )

            campionato = league.get(
                "name"
            )

            paese = league.get(
                "country"
            )

            # ------------------------------------------------
            # ORA
            # ------------------------------------------------

            ora = ""

            if data_completa:

                try:

                    # Convertiamo l'orario UTC
                    # nell'orario italiano.

                    data_utc = datetime.fromisoformat(
                        data_completa.replace(
                            "Z",
                            "+00:00"
                        )
                    )

                    data_italia = (
                        data_utc.astimezone(
                            TIMEZONE_ITALIA
                        )
                    )

                    ora = data_italia.strftime(
                        "%H:%M"
                    )

                except Exception:

                    try:

                        ora = data_completa[11:16]

                    except Exception:

                        ora = ""

            # ------------------------------------------------
            # PRIORITÀ
            # ------------------------------------------------

            priority = priorita_campionato(

                paese,

                campionato

            )

            # =================================================
            # STRUTTURA
            # =================================================

            partita_filtrata = {

                # ID
                "id": fixture_id,

                # SQUADRE
                "casa": casa,
                "trasferta": trasferta,

                # ID SQUADRE
                "home_id": home_id,
                "away_id": away_id,

                # CAMPIONATO
                "lega": campionato,
                "paese": paese,

                # ORARIO DISPLAY
                "ora": ora,

                # DATA COMPLETA
                "data": data_completa,

                # COMPATIBILITÀ
                "date": data_completa,

                # PRIORITÀ
                "priority": priority

            }

            partite.append(
                partita_filtrata
            )

        except Exception as e:

            print(
                "⚠️ ERRORE ELABORAZIONE PARTITA:",
                e
            )

    # ========================================================
    # ORDINAMENTO
    # ========================================================

    partite.sort(

        key=lambda x: (

            -x.get(
                "priority",
                0
            ),

            x.get(
                "data",
                ""
            )

        )

    )

    print(
        "✅ PARTITE FILTRATE:",
        len(partite)
    )

    # ========================================================
    # CACHE
    # ========================================================

    salva_cache(
        partite,
        oggi
    )

    return partite