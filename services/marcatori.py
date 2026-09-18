import os
import json
import time
import requests

from config import FOOTBALL_API_KEY


# ============================================================
# CONFIG
# ============================================================

BASE_URL = "https://v3.football.api-sports.io"

HEADERS = {
    "x-apisports-key": FOOTBALL_API_KEY
}

CACHE_FILE = "cache/marcatori_serie_a.json"

# Il piano Free consente le statistiche giocatori
# solo per stagioni fino al 2024.
#
# Partiamo dalla più recente disponibile.
STAGIONI_DISPONIBILI = [2024, 2023, 2022]

CACHE_ROSA_ORE = 72
CACHE_STATISTICHE_ORE = 24

SERIE_A_LEAGUE_ID = 135


# ============================================================
# CACHE
# ============================================================

def _crea_cache():
    os.makedirs("cache", exist_ok=True)

    if not os.path.exists(CACHE_FILE):
        dati = {
            "rose_attuali": {},
            "statistiche": {}
        }

        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(dati, f, ensure_ascii=False, indent=2)


def _carica_cache():
    _crea_cache()

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            dati = json.load(f)

            if not isinstance(dati, dict):
                return {
                    "rose_attuali": {},
                    "statistiche": {}
                }

            dati.setdefault("rose_attuali", {})
            dati.setdefault("statistiche", {})

            return dati

    except Exception:
        return {
            "rose_attuali": {},
            "statistiche": {}
        }


def _salva_cache(dati):
    _crea_cache()

    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(
                dati,
                f,
                ensure_ascii=False,
                indent=2
            )

    except Exception as e:
        print(f"⚠️ ERRORE SALVATAGGIO CACHE MARCATORI: {e}")


def _cache_valida(timestamp, ore):
    if not timestamp:
        return False

    return (time.time() - timestamp) < (ore * 3600)


# ============================================================
# API
# ============================================================

def _api_get(endpoint, params):
    try:
        response = requests.get(
            f"{BASE_URL}/{endpoint}",
            headers=HEADERS,
            params=params,
            timeout=15
        )

        if response.status_code != 200:
            print(
                f"⚠️ API MARCATORI HTTP {response.status_code}: "
                f"{response.text[:300]}"
            )
            return None

        dati = response.json()

        errors = dati.get("errors")

        if errors:
            print(f"⚠️ API MARCATORI: {errors}")
            return None

        return dati

    except Exception as e:
        print(f"⚠️ ERRORE API MARCATORI: {e}")
        return None


# ============================================================
# ROSA ATTUALE
# ============================================================

def _prendi_rosa_attuale(team_id):
    """
    Recupera la rosa ATTUALE della squadra.

    Questo è fondamentale:
    le statistiche storiche possono contenere giocatori
    che oggi non fanno più parte della squadra.

    Esempio:
    Dovbyk nelle vecchie statistiche della Roma
    non deve essere considerato se non è più nella rosa attuale.
    """

    cache = _carica_cache()

    chiave = str(team_id)

    dati_cache = cache["rose_attuali"].get(chiave)

    if dati_cache:
        timestamp = dati_cache.get("timestamp")

        if _cache_valida(timestamp, CACHE_ROSA_ORE):
            return dati_cache.get("giocatori", [])

    dati = _api_get(
        "players/squads",
        {
            "team": team_id
        }
    )

    if not dati:
        return []

    response = dati.get("response", [])

    if not response:
        return []

    squadra = response[0]

    giocatori = squadra.get("players", [])

    rosa = []

    for giocatore in giocatori:
        player_id = giocatore.get("id")

        if not player_id:
            continue

        nome = giocatore.get("name", "Sconosciuto")

        posizione = giocatore.get("position", "")

        rosa.append({
            "id": player_id,
            "nome": nome,
            "posizione": posizione
        })

    cache["rose_attuali"][chiave] = {
        "timestamp": time.time(),
        "giocatori": rosa
    }

    _salva_cache(cache)

    return rosa


# ============================================================
# STATISTICHE STORICHE GIOCATORI
# ============================================================

def _prendi_statistiche_giocatori(team_id):
    """
    Recupera le statistiche disponibili dal piano Free.

    NON prova più 2026/2025 perché il piano Free non permette
    queste stagioni per le statistiche giocatori.

    Prima prova 2024.
    Se non trova dati, prova 2023.
    Poi 2022.
    """

    cache = _carica_cache()

    chiave = str(team_id)

    dati_cache = cache["statistiche"].get(chiave)

    if dati_cache:
        timestamp = dati_cache.get("timestamp")

        if _cache_valida(timestamp, CACHE_STATISTICHE_ORE):
            return dati_cache.get("giocatori", [])

    for stagione in STAGIONI_DISPONIBILI:

        dati = _api_get(
            "players",
            {
                "team": team_id,
                "season": stagione,
                "page": 1
            }
        )

        if not dati:
            continue

        risposta = dati.get("response", [])

        if not risposta:
            print(
                f"⚠️ NESSUN DATO: {team_id} stagione {stagione}"
            )
            continue

        giocatori = []

        for elemento in risposta:

            giocatore = elemento.get("player", {})
            statistiche = elemento.get("statistics", [])

            if not giocatore:
                continue

            stats = statistiche[0] if statistiche else {}

            giocatori.append({
                "id": giocatore.get("id"),
                "nome": giocatore.get("name", "Sconosciuto"),
                "stats": stats
            })

        if giocatori:

            cache["statistiche"][chiave] = {
                "timestamp": time.time(),
                "stagione": stagione,
                "giocatori": giocatori
            }

            _salva_cache(cache)

            print(
                f"✅ STATISTICHE GIOCATORI {team_id} "
                f"- STAGIONE {stagione}"
            )

            return giocatori

    return []


# ============================================================
# NORMALIZZAZIONE STATISTICHE
# ============================================================

def _numero(valore):
    try:
        if valore is None:
            return 0

        return float(valore)

    except Exception:
        return 0


def _normalizza_giocatore(giocatore):
    stats = giocatore.get("stats", {})

    games = stats.get("games", {}) or {}
    goals = stats.get("goals", {}) or {}
    shots = stats.get("shots", {}) or {}
    penalty = stats.get("penalty", {}) or {}

    minuti = _numero(games.get("minutes"))
    presenze = _numero(games.get("appearences"))
    titolare = _numero(games.get("lineups"))

    gol = _numero(goals.get("total"))
    assist = _numero(goals.get("assists"))

    tiri = _numero(shots.get("total"))
    tiri_porta = _numero(shots.get("on"))

    rigori = _numero(penalty.get("scored"))

    return {
        "id": giocatore.get("id"),
        "nome": giocatore.get("nome", "Sconosciuto"),
        "posizione": games.get("position", ""),
        "minuti": minuti,
        "presenze": presenze,
        "titolare": titolare,
        "gol": gol,
        "assist": assist,
        "tiri": tiri,
        "tiri_porta": tiri_porta,
        "rigori": rigori
    }


# ============================================================
# CALCOLO PUNTEGGIO
# ============================================================

def _calcola_score(giocatore, partita_casa=True):
    """
    Calcola un punteggio indicativo per stimare
    la probabilità di segnare.

    Non è una probabilità statistica ufficiale:
    è una stima interna del modello.
    """

    gol = giocatore["gol"]
    minuti = giocatore["minuti"]
    tiri = giocatore["tiri"]
    tiri_porta = giocatore["tiri_porta"]
    titolare = giocatore["titolare"]
    rigori = giocatore["rigori"]

    if minuti > 0:
        gol_90 = gol / (minuti / 90)
        tiri_90 = tiri / (minuti / 90)
        tiri_porta_90 = tiri_porta / (minuti / 90)
    else:
        gol_90 = 0
        tiri_90 = 0
        tiri_porta_90 = 0

    score = 0

    # Gol per 90
    score += gol_90 * 35

    # Volume di tiro
    score += tiri_90 * 7

    # Tiri nello specchio
    score += tiri_porta_90 * 12

    # Presenza da titolare
    if titolare >= 5:
        score += 8

    # Rigori
    if rigori > 0:
        score += 15

    # Piccolo bonus casa
    if partita_casa:
        score *= 1.05

    return score


# ============================================================
# PROBABILITÀ STIMATA
# ============================================================

def _probabilita(score):
    """
    Trasforma il punteggio interno in una percentuale
    prudente.

    Range massimo 75%.
    """

    if score <= 0:
        return 5

    probabilita = 5 + (score * 1.8)

    if probabilita > 75:
        probabilita = 75

    if probabilita < 5:
        probabilita = 5

    return round(probabilita)


# ============================================================
# SELEZIONE MARCATORI
# ============================================================

def _seleziona_marcatori(team_id, partita_casa=True):
    """
    Restituisce i migliori 3 candidati della squadra.

    Regola fondamentale:
    il giocatore DEVE appartenere alla rosa attuale.
    """

    rosa = _prendi_rosa_attuale(team_id)

    if not rosa:
        print(
            f"⚠️ ROSA ATTUALE NON DISPONIBILE: {team_id}"
        )
        return []

    statistiche = _prendi_statistiche_giocatori(team_id)

    if not statistiche:
        print(
            f"⚠️ STATISTICHE NON DISPONIBILI: {team_id}"
        )
        return []

    # ID dei giocatori attualmente in rosa
    ids_attuali = {
        giocatore["id"]
        for giocatore in rosa
        if giocatore.get("id")
    }

    # Mappa posizione attuale
    posizione_attuale = {
        giocatore["id"]: giocatore.get("posizione", "")
        for giocatore in rosa
        if giocatore.get("id")
    }

    candidati = []

    for giocatore in statistiche:

        player_id = giocatore.get("id")

        # ====================================================
        # FILTRO CRITICO:
        # SOLO GIOCATORI DELLA ROSA ATTUALE
        # ====================================================

        if player_id not in ids_attuali:
            continue

        normale = _normalizza_giocatore(giocatore)

        normale["posizione"] = posizione_attuale.get(
            player_id,
            normale["posizione"]
        )

        posizione = str(normale["posizione"]).lower()

        # Escludiamo portieri e difensori puri
        if any(
            parola in posizione
            for parola in [
                "goalkeeper",
                "defender"
            ]
        ):
            continue

        # Devono avere almeno qualche presenza/minuto
        if normale["minuti"] <= 0:
            continue

        score = _calcola_score(
            normale,
            partita_casa=partita_casa
        )

        normale["score"] = score
        normale["probabilita"] = _probabilita(score)

        candidati.append(normale)

    # Ordina dal più pericoloso al meno pericoloso
    candidati.sort(
        key=lambda x: (
            x["score"],
            x["gol"],
            x["tiri_porta"]
        ),
        reverse=True
    )

    return candidati[:3]


# ============================================================
# ANALISI DI TUTTE LE PARTITE
# ============================================================

def analizza_marcatori_partite(partite):
    """
    Analizza i marcatori delle partite ricevute.

    IMPORTANTE:
    - solo Serie A viene filtrata dal handler
    - non modifica schedina
    - non salva pronostici nello storico
    - usa la rosa attuale
    """

    risultati = []

    for partita in partite:

        home_id = partita.get("home_id")
        away_id = partita.get("away_id")

        if not home_id or not away_id:
            continue

        casa = partita.get(
            "casa",
            "Squadra casa"
        )

        trasferta = partita.get(
            "trasferta",
            "Squadra trasferta"
        )

        ora = partita.get(
            "ora",
            ""
        )

        print(
            f"\n⚽ ANALISI MARCATORI: "
            f"{casa} - {trasferta}"
        )

        marcatori_casa = _seleziona_marcatori(
            home_id,
            partita_casa=True
        )

        marcatori_trasferta = _seleziona_marcatori(
            away_id,
            partita_casa=False
        )

        risultati.append({
            "fixture_id": partita.get("id"),
            "casa": casa,
            "trasferta": trasferta,
            "ora": ora,
            "marcatori_casa": marcatori_casa,
            "marcatori_trasferta": marcatori_trasferta
        })

    return risultati