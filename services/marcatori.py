import json
import os
from typing import Any, Dict, List, Optional

import requests

from config import FOOTBALL_API_KEY


BASE_URL = "https://api.football-data.org/v4"

HEADERS = {
    "X-Auth-Token": FOOTBALL_API_KEY
}

CACHE_FILE = "cache/marcatori_serie_a.json"


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


def _carica_cache() -> Dict[str, Any]:
    if not os.path.exists(CACHE_FILE):
        return {}

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _salva_cache(cache: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def _prendi_rosa_attuale(team_id: int) -> List[Dict[str, Any]]:
    cache = _carica_cache()
    cache_key = f"rosa_{team_id}"

    if cache_key in cache:
        print(f"✅ USO CACHE ROSA: {team_id}")
        return cache[cache_key]

    url = f"{BASE_URL}/teams/{team_id}"

    try:
        risposta = requests.get(
            url,
            headers=HEADERS,
            timeout=15
        )

        print(
            f"📡 API ROSA: "
            f"{risposta.status_code} teams/{team_id}"
        )

        if risposta.status_code != 200:
            print(
                f"❌ ERRORE ROSA {team_id}: "
                f"{risposta.text}"
            )
            return []

        dati = risposta.json()

        rosa = dati.get("squad", [])

        cache[cache_key] = rosa
        _salva_cache(cache)

        return rosa

    except Exception as e:
        print(
            f"❌ ERRORE RECUPERO ROSA {team_id}: {e}"
        )
        return []


def _prendi_statistiche_giocatori(
    team_id: int,
    competition_code: str
) -> List[Dict[str, Any]]:
    cache = _carica_cache()
    cache_key = f"{competition_code}_{team_id}"

    if cache_key in cache:
        print(
            f"✅ USO CACHE MARCATORI "
            f"{competition_code} TEAM {team_id}"
        )
        return cache[cache_key]

    print(
        f"📊 RECUPERO MARCATORI "
        f"{competition_code} - TEAM {team_id}"
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

        if risposta.status_code != 200:
            print(
                f"❌ ERRORE MARCATORI "
                f"{competition_code}: {risposta.text}"
            )
            return []

        dati = risposta.json()

        marcatori = []

        for elemento in dati.get("scorers", []):
            team = elemento.get("team", {})

            if team.get("id") != team_id:
                continue

            marcatori.append(elemento)

        cache[cache_key] = marcatori
        _salva_cache(cache)

        print(
            f"✅ MARCATORI {competition_code} "
            f"TEAM {team_id}: {len(marcatori)}"
        )

        return marcatori

    except Exception as e:
        print(
            f"❌ ERRORE API MARCATORI "
            f"{competition_code} TEAM {team_id}: {e}"
        )
        return []


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

    continuita = min(presenze / 30, 1.0)
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


def _seleziona_marcatori(
    team_id: int,
    competition_code: str,
    partita_casa: bool = True
) -> List[Dict[str, Any]]:

    rosa = _prendi_rosa_attuale(team_id)

    statistiche = _prendi_statistiche_giocatori(
        team_id,
        competition_code
    )

    if not statistiche:
        return []

    rosa_map = {}

    for giocatore in rosa:
        giocatore_id = giocatore.get("id")

        if giocatore_id is not None:
            rosa_map[giocatore_id] = giocatore

    risultati = []

    for elemento in statistiche:

        player = elemento.get("player", {})

        player_id = player.get("id")

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

        if "goal" in posizione.lower():
            continue

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
                "score": round(score, 1),
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


def _trova_competizione(
    lega: str
) -> Optional[str]:

    if not lega:
        return None

    lega_normalizzata = lega.strip().lower()

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


def analizza_marcatori_partite(
    partite: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    risultati_finali = []

    for partita in partite:

        fixture_id = partita.get("id")

        casa = partita.get("casa")
        trasferta = partita.get("trasferta")
        ora = partita.get("ora", "")

        competition_code = (
            partita.get("competition_code")
            or partita.get("competizione_code")
            or partita.get("competition")
        )

        if competition_code not in COMPETIZIONI_SUPPORTATE:
            competition_code = _trova_competizione(
                partita.get("lega", "")
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

        print(
            f"🏆 COMPETIZIONE: "
            f"{COMPETIZIONI_SUPPORTATE.get(competition_code, competition_code)} "
            f"({competition_code})"
        )

        home_id = partita.get("home_id")
        away_id = partita.get("away_id")

        if not home_id or not away_id:
            print(
                f"⚠️ ID SQUADRE MANCANTI: "
                f"{casa} / {trasferta}"
            )
            continue

        marcatori_casa = _seleziona_marcatori(
            home_id,
            competition_code,
            partita_casa=True
        )

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