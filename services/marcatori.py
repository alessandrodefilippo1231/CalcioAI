import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests

from config import FOOTBALL_API_KEY


BASE_URL = "https://api.football-data.org/v4"

HEADERS = {
    "X-Auth-Token": FOOTBALL_API_KEY
}

CACHE_FILE = "cache/marcatori_serie_a.json"

# Cache:
# Rosa = 72 ore
# Marcatori competizione = 24 ore
CACHE_ROSA_ORE = 72
CACHE_MARCATORI_ORE = 24


COMPETIZIONI_SUPPORTATE = {
    "SA": "Serie A",
    "PL": "Premier League",
    "BL1": "Bundesliga",
    "PD": "La Liga",
    "FL1": "Ligue 1",
    "DED": "Eredivisie",
    "PPL": "Primeira Liga",
    "ELC": "Championship",
    "BSA": "Serie A Brasile",
}


# ============================================================
# CACHE
# ============================================================

def _carica_cache() -> Dict[str, Any]:
    if not os.path.exists(CACHE_FILE):
        return {}

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ ERRORE LETTURA CACHE MARCATORI: {e}")
        return {}


def _salva_cache(cache: Dict[str, Any]) -> None:
    try:
        os.makedirs(
            os.path.dirname(CACHE_FILE),
            exist_ok=True
        )

        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(
                cache,
                f,
                ensure_ascii=False,
                indent=2
            )

    except Exception as e:
        print(f"⚠️ ERRORE SALVATAGGIO CACHE MARCATORI: {e}")


def _cache_valida(
    elemento: Dict[str, Any],
    ore: int
) -> bool:

    try:
        data = elemento.get("data")

        if not data:
            return False

        salvata = datetime.fromisoformat(data)

        differenza = datetime.now() - salvata

        return differenza <= timedelta(hours=ore)

    except Exception:
        return False


# ============================================================
# ROSA ATTUALE
# ============================================================

def _prendi_rosa_attuale(
    team_id: int
) -> List[Dict[str, Any]]:

    cache = _carica_cache()

    cache_key = f"rosa_{team_id}"

    elemento_cache = cache.get(cache_key)

    # CACHE VALIDA
    if isinstance(elemento_cache, dict):

        rosa = elemento_cache.get("dati")

        if (
            rosa is not None
            and _cache_valida(
                elemento_cache,
                CACHE_ROSA_ORE
            )
        ):
            print(
                f"✅ USO CACHE ROSA: {team_id}"
            )

            return rosa

    # CACHE VECCHIA USATA COME FALLBACK
    rosa_fallback = []

    if isinstance(elemento_cache, dict):

        dati_vecchi = elemento_cache.get("dati")

        if dati_vecchi:
            print(
                f"⏰ CACHE ROSA SCADUTA: {team_id}"
            )

            rosa_fallback = dati_vecchi

    # API
    url = f"{BASE_URL}/teams/{team_id}"

    try:

        print(
            f"🌐 RICHIESTA API ROSA: {team_id}"
        )

        risposta = requests.get(
            url,
            headers=HEADERS,
            timeout=15
        )

        print(
            f"📡 API ROSA: "
            f"{risposta.status_code} "
            f"teams/{team_id}"
        )

        # RATE LIMIT
        if risposta.status_code == 429:

            print(
                f"⚠️ RATE LIMIT ROSA {team_id}"
            )

            if rosa_fallback:

                print(
                    f"♻️ USO VECCHIA CACHE ROSA: "
                    f"{team_id}"
                )

                return rosa_fallback

            return []

        # ALTRI ERRORI
        if risposta.status_code != 200:

            print(
                f"❌ ERRORE ROSA {team_id}: "
                f"{risposta.text}"
            )

            if rosa_fallback:

                print(
                    f"♻️ USO VECCHIA CACHE ROSA: "
                    f"{team_id}"
                )

                return rosa_fallback

            return []

        dati = risposta.json()

        rosa = dati.get(
            "squad",
            []
        )

        if not isinstance(rosa, list):
            rosa = []

        # SALVA CACHE
        cache[cache_key] = {
            "data": datetime.now().isoformat(),
            "dati": rosa
        }

        _salva_cache(cache)

        print(
            f"💾 ROSA SALVATA IN CACHE: "
            f"{team_id} "
            f"({len(rosa)} giocatori)"
        )

        return rosa

    except Exception as e:

        print(
            f"❌ ERRORE RECUPERO ROSA "
            f"{team_id}: {e}"
        )

        if rosa_fallback:

            print(
                f"♻️ USO VECCHIA CACHE ROSA: "
                f"{team_id}"
            )

            return rosa_fallback

        return []


# ============================================================
# STATISTICHE MARCATORI
# ============================================================

def _prendi_statistiche_giocatori(
    team_id: int,
    competition_code: str
) -> List[Dict[str, Any]]:

    cache = _carica_cache()

    # La risposta dell'endpoint scorers è della competizione,
    # quindi NON dobbiamo salvarla separatamente per ogni team.
    #
    # Prima:
    # SA_108
    # SA_112
    #
    # Ora:
    # scorers_SA
    #
    # Così la stessa chiamata API viene utilizzata per
    # tutte le squadre della competizione.

    cache_key = f"scorers_{competition_code}"

    elemento_cache = cache.get(cache_key)

    # CACHE VALIDA
    if isinstance(elemento_cache, dict):

        dati_cache = elemento_cache.get("dati")

        if (
            dati_cache is not None
            and _cache_valida(
                elemento_cache,
                CACHE_MARCATORI_ORE
            )
        ):

            print(
                f"✅ USO CACHE MARCATORI: "
                f"{competition_code}"
            )

            return _filtra_marcatori_team(
                dati_cache,
                team_id
            )

    # CACHE VECCHIA
    marcatori_fallback = []

    if isinstance(elemento_cache, dict):

        dati_vecchi = elemento_cache.get("dati")

        if dati_vecchi:

            print(
                f"⏰ CACHE MARCATORI SCADUTA: "
                f"{competition_code}"
            )

            marcatori_fallback = dati_vecchi

    # API
    print(
        f"🌐 RICHIESTA API MARCATORI: "
        f"{competition_code}"
    )

    url = (
        f"{BASE_URL}/competitions/"
        f"{competition_code}/scorers"
    )

    try:

        risposta = requests.get(
            url,
            headers=HEADERS,
            params={"limit": 100},
            timeout=15
        )

        print(
            f"📡 API MARCATORI: "
            f"{risposta.status_code} "
            f"competitions/{competition_code}/scorers"
        )

        # RATE LIMIT
        if risposta.status_code == 429:

            print(
                f"⚠️ RATE LIMIT MARCATORI: "
                f"{competition_code}"
            )

            if marcatori_fallback:

                print(
                    f"♻️ USO VECCHIA CACHE MARCATORI: "
                    f"{competition_code}"
                )

                return _filtra_marcatori_team(
                    marcatori_fallback,
                    team_id
                )

            return []

        # ALTRI ERRORI
        if risposta.status_code != 200:

            print(
                f"❌ ERRORE MARCATORI "
                f"{competition_code}: "
                f"{risposta.text}"
            )

            if marcatori_fallback:

                print(
                    f"♻️ USO VECCHIA CACHE MARCATORI: "
                    f"{competition_code}"
                )

                return _filtra_marcatori_team(
                    marcatori_fallback,
                    team_id
                )

            return []

        dati = risposta.json()

        marcatori = dati.get(
            "scorers",
            []
        )

        if not isinstance(marcatori, list):
            marcatori = []

        # SALVA RISPOSTA COMPLETA
        cache[cache_key] = {
            "data": datetime.now().isoformat(),
            "dati": marcatori
        }

        _salva_cache(cache)

        print(
            f"💾 MARCATORI SALVATI IN CACHE: "
            f"{competition_code} "
            f"({len(marcatori)} giocatori)"
        )

        return _filtra_marcatori_team(
            marcatori,
            team_id
        )

    except Exception as e:

        print(
            f"❌ ERRORE API MARCATORI "
            f"{competition_code} TEAM {team_id}: {e}"
        )

        if marcatori_fallback:

            print(
                f"♻️ USO VECCHIA CACHE MARCATORI: "
                f"{competition_code}"
            )

            return _filtra_marcatori_team(
                marcatori_fallback,
                team_id
            )

        return []


def _filtra_marcatori_team(
    marcatori: List[Dict[str, Any]],
    team_id: int
) -> List[Dict[str, Any]]:

    risultati = []

    for elemento in marcatori:

        team = elemento.get(
            "team",
            {}
        )

        if team.get("id") == team_id:

            risultati.append(
                elemento
            )

    return risultati


# ============================================================
# CALCOLO PROBABILITÀ
# ============================================================

def _calcola_probabilita(
    presenze: float,
    gol: float,
    assist: float,
    rigori: float,
    partita_casa: bool
) -> tuple[float, float]:

    if presenze <= 0:
        return 0.0, 5.0

    gol_per_presenza = gol / presenze
    assist_per_presenza = assist / presenze
    rigori_per_presenza = rigori / presenze

    punti_gol = gol_per_presenza * 150
    punti_assist = assist_per_presenza * 60
    punti_rigori = rigori_per_presenza * 25

    continuita = min(
        presenze / 30,
        1.0
    )

    punti_continuita = continuita * 5

    score = (
        punti_gol
        + punti_assist
        + punti_rigori
        + punti_continuita
    )

    probabilita = 5 + score

    if partita_casa:
        probabilita *= 1.05

    probabilita = max(
        5,
        min(probabilita, 75)
    )

    return (
        round(score, 1),
        round(probabilita, 1)
    )


# ============================================================
# SELEZIONE MARCATORI
# ============================================================

def _seleziona_marcatori(
    team_id: int,
    competition_code: str,
    partita_casa: bool = True
) -> List[Dict[str, Any]]:

    rosa = _prendi_rosa_attuale(
        team_id
    )

    statistiche = _prendi_statistiche_giocatori(
        team_id,
        competition_code
    )

    if not statistiche:
        return []

    rosa_map = {}

    for giocatore in rosa:

        giocatore_id = giocatore.get(
            "id"
        )

        if giocatore_id is not None:

            rosa_map[
                giocatore_id
            ] = giocatore

    risultati = []

    for elemento in statistiche:

        player = elemento.get(
            "player",
            {}
        )

        player_id = player.get(
            "id"
        )

        if not player_id:
            continue

        nome = (
            player.get("name")
            or player.get("lastName")
            or "Giocatore"
        )

        posizione = (
            player.get("section")
            or player.get("position")
            or ""
        )

        presenze = elemento.get(
            "playedMatches",
            0
        ) or 0

        gol = elemento.get(
            "goals",
            0
        ) or 0

        assist = elemento.get(
            "assists",
            0
        ) or 0

        rigori = elemento.get(
            "penalties",
            0
        ) or 0

        try:
            presenze = float(presenze)
        except (TypeError, ValueError):
            presenze = 0.0

        try:
            gol = float(gol)
        except (TypeError, ValueError):
            gol = 0.0

        try:
            assist = float(assist)
        except (TypeError, ValueError):
            assist = 0.0

        try:
            rigori = float(rigori)
        except (TypeError, ValueError):
            rigori = 0.0

        # Escludi portieri
        if "goal" in posizione.lower():
            continue

        # Escludi giocatori senza produzione offensiva
        if (
            gol <= 0
            and assist <= 0
            and rigori <= 0
        ):
            continue

        score, probabilita = _calcola_probabilita(
            presenze=presenze,
            gol=gol,
            assist=assist,
            rigori=rigori,
            partita_casa=partita_casa
        )

        # Bonus rosa attuale
        if player_id in rosa_map:
            score += 2

        risultati.append(
            {
                "id": player_id,
                "nome": nome,
                "posizione": posizione,
                "presenze": presenze,
                "gol": gol,
                "assist": assist,
                "rigori": rigori,
                "score": round(
                    score,
                    1
                ),
                "probabilita": probabilita,
                "competition_code": competition_code,
            }
        )

    risultati.sort(
        key=lambda x: (
            x["probabilita"],
            x["score"],
            x["gol"],
            x["assist"],
            x["presenze"],
        ),
        reverse=True
    )

    return risultati[:3]


# ============================================================
# TROVA COMPETIZIONE
# ============================================================

def _trova_competizione(
    lega: str
) -> Optional[str]:

    if not lega:
        return None

    lega_normalizzata = (
        lega.strip().lower()
    )

    if "serie a brasile" in lega_normalizzata:
        return "BSA"

    if "brasile" in lega_normalizzata:
        return "BSA"

    if "serie a" in lega_normalizzata:
        return "SA"

    if "premier league" in lega_normalizzata:
        return "PL"

    if "bundesliga" in lega_normalizzata:
        return "BL1"

    if "la liga" in lega_normalizzata:
        return "PD"

    if "ligue 1" in lega_normalizzata:
        return "FL1"

    if "eredivisie" in lega_normalizzata:
        return "DED"

    if "primeira liga" in lega_normalizzata:
        return "PPL"

    if "championship" in lega_normalizzata:
        return "ELC"

    return None


# ============================================================
# ANALISI MARCATORI PARTITE
# ============================================================

def analizza_marcatori_partite(
    partite: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    risultati_finali = []

    for partita in partite:

        fixture_id = partita.get(
            "id"
        )

        casa = partita.get(
            "casa"
        )

        trasferta = partita.get(
            "trasferta"
        )

        ora = partita.get(
            "ora",
            ""
        )

        competition_code = (
            partita.get(
                "competition_code"
            )
            or partita.get(
                "competizione_code"
            )
            or partita.get(
                "competition"
            )
        )

        if (
            competition_code
            not in COMPETIZIONI_SUPPORTATE
        ):

            competition_code = _trova_competizione(
                partita.get(
                    "lega",
                    ""
                )
            )

        if not competition_code:

            print(
                f"⚠️ COMPETIZIONE NON SUPPORTATA: "
                f"{partita.get('lega')}"
            )

            continue

        print()
        print(
            f"⚽ ANALISI MARCATORI: "
            f"{casa} - {trasferta}"
        )

        nome_competizione = (
            COMPETIZIONI_SUPPORTATE.get(
                competition_code,
                competition_code
            )
        )

        print(
            f"🏆 COMPETIZIONE: "
            f"{nome_competizione} "
            f"({competition_code})"
        )

        home_id = partita.get(
            "home_id"
        )

        away_id = partita.get(
            "away_id"
        )

        if not home_id or not away_id:

            print(
                f"⚠️ ID SQUADRE MANCANTI: "
                f"{casa} / {trasferta}"
            )

            continue

        # CASA
        marcatori_casa = _seleziona_marcatori(
            home_id,
            competition_code,
            partita_casa=True
        )

        # TRASFERTA
        marcatori_trasferta = _seleziona_marcatori(
            away_id,
            competition_code,
            partita_casa=False
        )

        risultati_finali.append(
            {
                "fixture_id": fixture_id,
                "casa": casa,
                "trasferta": trasferta,
                "ora": ora,
                "competition_code": competition_code,
                "marcatori_casa": marcatori_casa,
                "marcatori_trasferta": marcatori_trasferta,
            }
        )

    return risultati_finali