import json
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests
from dotenv import load_dotenv


# ============================================================
# CARICAMENTO VARIABILI .ENV
# ============================================================

load_dotenv()


# ============================================================
# CONFIGURAZIONE
# ============================================================

BASE_URL = "https://api.football-data.org/v4"

CACHE_FILE = "cache/statistiche_cache.json"

NUMERO_PARTITE_STORICO = 5
GIORNI_STORICO_API = 120
CACHE_FALLBACK_ORE = 168

ROME_TZ = ZoneInfo("Europe/Rome")


# ============================================================
# COMPETIZIONI SUPPORTATE
# ============================================================

COMPETIZIONI_SUPPORTATE = {
    "SA": "Serie A",
    "PL": "Premier League",
    "BL1": "Bundesliga",
    "PD": "La Liga",
    "FL1": "Ligue 1",
    "CL": "Champions League",
}


# ============================================================
# STATISTICHE VUOTE
# ============================================================

def statistiche_vuote(competition_code=None):

    nome_competizione = COMPETIZIONI_SUPPORTATE.get(
        competition_code,
        "N/D"
    )

    return {
        "competizione": nome_competizione,
        "competizione_code": competition_code,

        "partite": 0,

        "vittorie": 0,
        "pareggi": 0,
        "sconfitte": 0,

        "gol_fatti": 0,
        "gol_subiti": 0,

        "media_gol_fatti": 0.0,
        "media_gol_subiti": 0.0,

        "over15": 0,
        "over25": 0,
        "under35": 0,
        "golgol": 0,

        "storico": [],
    }


# ============================================================
# CACHE
# ============================================================

def _assicura_cartella_cache():

    cartella = os.path.dirname(CACHE_FILE)

    if cartella:
        os.makedirs(
            cartella,
            exist_ok=True
        )


def _leggi_cache():

    if not os.path.exists(CACHE_FILE):
        return {}

    try:

        with open(
            CACHE_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            dati = json.load(f)

        if isinstance(dati, dict):
            return dati

    except Exception as e:

        print(
            f"⚠️ Errore lettura cache statistiche: {e}"
        )

    return {}


def _salva_cache(dati):

    _assicura_cartella_cache()

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
            f"⚠️ Errore salvataggio cache statistiche: {e}"
        )


def _cache_key(
    team_id,
    competition_code
):

    return f"{team_id}_{competition_code}"


def _prendi_cache_vecchia(
    team_id,
    competition_code
):

    """
    Compatibilità con eventuale vecchia cache
    che utilizzava solo team_id come chiave.
    """

    cache = _leggi_cache()

    dati = cache.get(
        str(team_id)
    )

    if not isinstance(dati, dict):

        dati = cache.get(
            team_id
        )

    if not isinstance(dati, dict):
        return None

    storico = dati.get(
        "storico"
    )

    if not isinstance(storico, list):
        return None

    storico_filtrato = []

    for partita in storico:

        if not isinstance(
            partita,
            dict
        ):
            continue

        codice = partita.get(
            "competizione_code"
        )

        if codice == competition_code:

            storico_filtrato.append(
                partita
            )

    if not storico_filtrato:
        return None

    nuovo = dict(
        dati
    )

    nuovo["storico"] = storico_filtrato[
        :NUMERO_PARTITE_STORICO
    ]

    nuovo["competizione_code"] = (
        competition_code
    )

    nuovo["competizione"] = (
        COMPETIZIONI_SUPPORTATE.get(
            competition_code,
            "N/D"
        )
    )

    return nuovo


def _cache_valida(dati):

    if not isinstance(
        dati,
        dict
    ):
        return False

    timestamp = dati.get(
        "timestamp"
    )

    if not timestamp:
        return False

    try:

        data_cache = datetime.fromisoformat(
            timestamp
        )

        if data_cache.tzinfo is None:

            data_cache = data_cache.replace(
                tzinfo=ROME_TZ
            )

        limite = (
            datetime.now(
                ROME_TZ
            )
            - timedelta(
                hours=CACHE_FALLBACK_ORE
            )
        )

        return data_cache >= limite

    except Exception:

        return False


# ============================================================
# DATA
# ============================================================

def _converti_data_italiana(
    data_utc
):

    if not data_utc:
        return "N/D"

    try:

        data = datetime.fromisoformat(
            data_utc.replace(
                "Z",
                "+00:00"
            )
        )

        data_italiana = data.astimezone(
            ROME_TZ
        )

        return data_italiana.strftime(
            "%d/%m/%Y"
        )

    except Exception:

        return "N/D"


# ============================================================
# COSTRUZIONE STORICO
# ============================================================

def _crea_storico(
    team_id,
    partite,
    competition_code
):

    storico = []

    for partita in partite:

        try:

            competition = partita.get(
                "competition",
                {}
            )

            codice_partita = competition.get(
                "code"
            )

            # Sicurezza: solo competizione richiesta
            if codice_partita != competition_code:
                continue

            home_team = partita.get(
                "homeTeam",
                {}
            )

            away_team = partita.get(
                "awayTeam",
                {}
            )

            score = partita.get(
                "score",
                {}
            )

            full_time = score.get(
                "fullTime",
                {}
            )

            home_id = home_team.get(
                "id"
            )

            away_id = away_team.get(
                "id"
            )

            gol_casa = full_time.get(
                "home"
            )

            gol_trasferta = full_time.get(
                "away"
            )

            if (
                home_id is None
                or away_id is None
                or gol_casa is None
                or gol_trasferta is None
            ):
                continue

            if int(home_id) == int(team_id):

                gol_fatti_team = int(
                    gol_casa
                )

                gol_subiti_team = int(
                    gol_trasferta
                )

            elif int(away_id) == int(team_id):

                gol_fatti_team = int(
                    gol_trasferta
                )

                gol_subiti_team = int(
                    gol_casa
                )

            else:

                continue

            if (
                gol_fatti_team
                > gol_subiti_team
            ):

                esito = "V"

            elif (
                gol_fatti_team
                == gol_subiti_team
            ):

                esito = "N"

            else:

                esito = "P"

            storico.append({

                "data": _converti_data_italiana(
                    partita.get(
                        "utcDate"
                    )
                ),

                "casa": home_team.get(
                    "name",
                    "N/D"
                ),

                "trasferta": away_team.get(
                    "name",
                    "N/D"
                ),

                "gol_casa": int(
                    gol_casa
                ),

                "gol_trasferta": int(
                    gol_trasferta
                ),

                "gol_fatti_team": (
                    gol_fatti_team
                ),

                "gol_subiti_team": (
                    gol_subiti_team
                ),

                "esito": esito,

                "competizione": competition.get(
                    "name",
                    COMPETIZIONI_SUPPORTATE.get(
                        competition_code,
                        "N/D"
                    )
                ),

                "competizione_code": (
                    competition_code
                ),
            })

        except Exception as e:

            print(
                f"⚠️ Errore creazione storico: {e}"
            )

    return storico[
        :NUMERO_PARTITE_STORICO
    ]


# ============================================================
# CALCOLO STATISTICHE
# ============================================================

def _calcola_da_storico(
    storico,
    competition_code
):

    statistiche = statistiche_vuote(
        competition_code
    )

    if not storico:
        return statistiche

    statistiche["storico"] = storico

    statistiche["partite"] = len(
        storico
    )

    for partita in storico:

        gf = int(
            partita.get(
                "gol_fatti_team",
                0
            )
            or 0
        )

        gs = int(
            partita.get(
                "gol_subiti_team",
                0
            )
            or 0
        )

        statistiche[
            "gol_fatti"
        ] += gf

        statistiche[
            "gol_subiti"
        ] += gs

        esito = partita.get(
            "esito"
        )

        if esito == "V":

            statistiche[
                "vittorie"
            ] += 1

        elif esito == "N":

            statistiche[
                "pareggi"
            ] += 1

        elif esito == "P":

            statistiche[
                "sconfitte"
            ] += 1

        gol_casa = int(
            partita.get(
                "gol_casa",
                0
            )
            or 0
        )

        gol_trasferta = int(
            partita.get(
                "gol_trasferta",
                0
            )
            or 0
        )

        totale = (
            gol_casa
            + gol_trasferta
        )

        if totale >= 2:

            statistiche[
                "over15"
            ] += 1

        if totale >= 3:

            statistiche[
                "over25"
            ] += 1

        if totale <= 3:

            statistiche[
                "under35"
            ] += 1

        if (
            gol_casa > 0
            and gol_trasferta > 0
        ):

            statistiche[
                "golgol"
            ] += 1

    numero_partite = statistiche[
        "partite"
    ]

    if numero_partite > 0:

        statistiche[
            "media_gol_fatti"
        ] = round(
            statistiche[
                "gol_fatti"
            ]
            / numero_partite,
            2
        )

        statistiche[
            "media_gol_subiti"
        ] = round(
            statistiche[
                "gol_subiti"
            ]
            / numero_partite,
            2
        )

        statistiche[
            "over15"
        ] = round(
            statistiche[
                "over15"
            ]
            / numero_partite
            * 100
        )

        statistiche[
            "over25"
        ] = round(
            statistiche[
                "over25"
            ]
            / numero_partite
            * 100
        )

        statistiche[
            "under35"
        ] = round(
            statistiche[
                "under35"
            ]
            / numero_partite
            * 100
        )

        statistiche[
            "golgol"
        ] = round(
            statistiche[
                "golgol"
            ]
            / numero_partite
            * 100
        )

    return statistiche


# ============================================================
# API FOOTBALL-DATA
# ============================================================

def ultime_partite(
    team_id,
    competition_code=None
):

    if not team_id:

        return statistiche_vuote(
            competition_code
        )

    if not competition_code:

        print(
            f"⚠️ Nessuna competizione specificata "
            f"per team {team_id}"
        )

        return statistiche_vuote()

    competition_code = str(
        competition_code
    ).upper().strip()

    if (
        competition_code
        not in COMPETIZIONI_SUPPORTATE
    ):

        print(
            f"⚠️ Competizione non supportata: "
            f"{competition_code}"
        )

        return statistiche_vuote(
            competition_code
        )

    # ========================================================
    # API KEY
    # ========================================================

    api_key = os.getenv(
        "FOOTBALL_API_KEY"
    )

    if not api_key:

        print(
            "❌ FOOTBALL_API_KEY non configurata"
        )

        return statistiche_vuote(
            competition_code
        )

    # ========================================================
    # CACHE
    # ========================================================

    cache = _leggi_cache()

    key = _cache_key(
        team_id,
        competition_code
    )

    cache_dati = cache.get(
        key
    )

    if (
        isinstance(
            cache_dati,
            dict
        )
        and _cache_valida(
            cache_dati
        )
        and isinstance(
            cache_dati.get(
                "storico"
            ),
            list
        )
        and len(
            cache_dati[
                "storico"
            ]
        ) > 0
    ):

        print(
            f"📦 Cache statistiche "
            f"{team_id} {competition_code}"
        )

        return cache_dati

    # ========================================================
    # CACHE VECCHIA
    # ========================================================

    cache_vecchia = _prendi_cache_vecchia(
        team_id,
        competition_code
    )

    # ========================================================
    # DATE API
    # ========================================================

    oggi = datetime.now(
        ROME_TZ
    ).date()

    data_da = (
        oggi
        - timedelta(
            days=GIORNI_STORICO_API
        )
    )

    params = {

        "status": "FINISHED",

        "dateFrom": data_da.isoformat(),

        "dateTo": oggi.isoformat(),

        "competitions": competition_code,
    }

    headers = {

        "X-Auth-Token": api_key,
    }

    url = (
        f"{BASE_URL}/teams/"
        f"{team_id}/matches"
    )

    # ========================================================
    # CHIAMATA API
    # ========================================================

    try:

        print(
            f"🌐 API statistiche: "
            f"team={team_id} "
            f"competition={competition_code}"
        )

        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=20
        )

        print(
            f"📡 Risposta API statistiche: "
            f"{response.status_code}"
        )

        # ====================================================
        # ERRORE API
        # ====================================================

        if response.status_code != 200:

            print(
                f"⚠️ API statistiche "
                f"{response.status_code}"
            )

            if cache_vecchia:

                print(
                    f"📦 Uso cache precedente "
                    f"{team_id} {competition_code}"
                )

                return cache_vecchia

            if cache_dati:

                print(
                    f"📦 Uso cache disponibile "
                    f"{team_id} {competition_code}"
                )

                return cache_dati

            return statistiche_vuote(
                competition_code
            )

        # ====================================================
        # JSON
        # ====================================================

        dati = response.json()

        partite = dati.get(
            "matches",
            []
        )

        print(
            f"📊 Partite ricevute API: "
            f"{len(partite)}"
        )

        # ====================================================
        # FILTRO COMPETIZIONE
        # ====================================================

        partite_filtrate = []

        for partita in partite:

            codice = partita.get(
                "competition",
                {}
            ).get(
                "code"
            )

            if codice == competition_code:

                partite_filtrate.append(
                    partita
                )

        # ====================================================
        # ORDINA
        # ====================================================

        partite_filtrate.sort(
            key=lambda x: x.get(
                "utcDate",
                ""
            ),
            reverse=True
        )

        partite_filtrate = (
            partite_filtrate[
                :NUMERO_PARTITE_STORICO
            ]
        )

        print(
            f"📊 Partite {competition_code} "
            f"dopo filtro: "
            f"{len(partite_filtrate)}"
        )

        # ====================================================
        # CREA STORICO
        # ====================================================

        storico = _crea_storico(
            team_id,
            partite_filtrate,
            competition_code
        )

        # ====================================================
        # CALCOLO
        # ====================================================

        statistiche = _calcola_da_storico(
            storico,
            competition_code
        )

        # ====================================================
        # TIMESTAMP
        # ====================================================

        statistiche[
            "timestamp"
        ] = datetime.now(
            ROME_TZ
        ).isoformat()

        # ====================================================
        # SALVATAGGIO CACHE
        # ====================================================

        cache = _leggi_cache()

        cache[key] = statistiche

        _salva_cache(
            cache
        )

        print(
            f"✅ Statistiche "
            f"{team_id} "
            f"{competition_code}: "
            f"{statistiche['partite']} partite"
        )

        return statistiche

    # ========================================================
    # ERRORI DI RETE
    # ========================================================

    except requests.RequestException as e:

        print(
            f"❌ Errore connessione API "
            f"statistiche: {e}"
        )

        if cache_dati:

            return cache_dati

        if cache_vecchia:

            return cache_vecchia

        return statistiche_vuote(
            competition_code
        )

    # ========================================================
    # ERRORE GENERICO
    # ========================================================

    except Exception as e:

        print(
            f"❌ Errore statistiche "
            f"{team_id} "
            f"{competition_code}: "
            f"{e}"
        )

        if cache_dati:

            return cache_dati

        if cache_vecchia:

            return cache_vecchia

        return statistiche_vuote(
            competition_code
        )