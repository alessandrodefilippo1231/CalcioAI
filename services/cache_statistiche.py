import json
import os
from datetime import datetime, timedelta


CACHE_FILE = "cache/statistiche_cache.json"


def _crea_cartella():
    os.makedirs("cache", exist_ok=True)


def _leggi_cache():
    _crea_cartella()

    if not os.path.exists(CACHE_FILE):
        return {}

    try:
        with open(
            CACHE_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception:

        return {}


def _scrivi_cache(cache):
    _crea_cartella()

    with open(
        CACHE_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            cache,
            f,
            ensure_ascii=False,
            indent=4
        )


def prendi_statistiche(team_id):
    """
    Restituisce le statistiche dalla cache
    se non sono vecchie di 24 ore.
    """

    cache = _leggi_cache()

    team_id = str(team_id)

    if team_id not in cache:
        return None

    try:

        salvata = datetime.fromisoformat(
            cache[team_id]["data"]
        )

        differenza = datetime.now() - salvata

        # Cache valida per 24 ore
        if differenza > timedelta(hours=24):

            return None

        print(
            f"✅ CACHE STATISTICHE: {team_id}"
        )

        return cache[team_id]["statistiche"]

    except Exception:

        return None


def salva_statistiche(team_id, statistiche):
    """
    Salva le statistiche della squadra
    nella cache.
    """

    cache = _leggi_cache()

    team_id = str(team_id)

    cache[team_id] = {

        "data": datetime.now().isoformat(),

        "statistiche": statistiche

    }

    _scrivi_cache(cache)

    print(
        f"💾 STATISTICHE SALVATE: {team_id}"
    )


def svuota_cache():
    """
    Elimina completamente la cache.
    """

    if os.path.exists(CACHE_FILE):

        os.remove(
            CACHE_FILE
        )

        print(
            "🗑 Cache statistiche eliminata."
        )