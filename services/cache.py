import json
import os
from datetime import datetime, timedelta


CACHE_DIR = "cache"
PARTITE_FILE = os.path.join(CACHE_DIR, "partite_cache.json")


def _crea_cartella():
    os.makedirs(CACHE_DIR, exist_ok=True)


# ============================================================
# CACHE PARTITE
# ============================================================

def salva_partite(partite):
    """
    Salva le partite del giorno su file.
    """

    _crea_cartella()

    dati = {
        "data": datetime.now().strftime("%Y-%m-%d"),
        "partite": partite
    }

    try:
        with open(PARTITE_FILE, "w", encoding="utf-8") as f:
            json.dump(
                dati,
                f,
                ensure_ascii=False,
                indent=4
            )

        print(f"💾 PARTITE SALVATE IN CACHE: {len(partite)}")

    except Exception as e:
        print("❌ ERRORE SALVATAGGIO CACHE PARTITE:", e)


def leggi_partite():
    """
    Recupera le partite salvate solo se appartengono a oggi.
    """

    _crea_cartella()

    if not os.path.exists(PARTITE_FILE):
        return None

    try:
        with open(PARTITE_FILE, "r", encoding="utf-8") as f:
            dati = json.load(f)

        oggi = datetime.now().strftime("%Y-%m-%d")

        if dati.get("data") != oggi:
            return None

        partite = dati.get("partite", [])

        if partite:
            print(
                f"✅ CACHE PARTITE UTILIZZATA: {len(partite)}"
            )

        return partite

    except Exception as e:
        print("❌ ERRORE LETTURA CACHE PARTITE:", e)
        return None


def svuota_partite():
    """
    Elimina la cache delle partite.
    """

    if os.path.exists(PARTITE_FILE):
        os.remove(PARTITE_FILE)
        print("🗑 Cache partite eliminata.")


# ============================================================
# CACHE GENERICA IN MEMORIA
# ============================================================

_cache = {}


def salva_cache(chiave, dati, durata=600):
    """
    Salva dati temporanei in memoria.
    """

    _cache[chiave] = {
        "dati": dati,
        "scadenza": datetime.now() + timedelta(seconds=durata)
    }


def leggi_cache(chiave):
    """
    Recupera dati dalla cache temporanea.
    """

    elemento = _cache.get(chiave)

    if elemento is None:
        return None

    if datetime.now() > elemento["scadenza"]:
        del _cache[chiave]
        return None

    return elemento["dati"]


def elimina_cache(chiave):
    """
    Cancella una cache specifica.
    """

    if chiave in _cache:
        del _cache[chiave]


def pulisci_cache():
    """
    Cancella tutte le cache temporanee.
    """

    _cache.clear()