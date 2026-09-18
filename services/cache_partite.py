import os
import json
from datetime import datetime


CACHE_FILE = "cache/partite_oggi.json"


def crea_cartella_cache():
    os.makedirs("cache", exist_ok=True)


def salva_partite(partite):
    crea_cartella_cache()

    dati = {
        "data": datetime.now().strftime("%Y-%m-%d"),
        "partite": partite
    }

    try:

        with open(
            CACHE_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                dati,
                file,
                ensure_ascii=False,
                indent=4
            )

        print(
            "💾 CACHE PARTITE SALVATA:",
            len(partite)
        )

        return True

    except Exception as e:

        print(
            "❌ ERRORE SALVATAGGIO CACHE PARTITE:",
            e
        )

        return False


def carica_partite():
    crea_cartella_cache()

    if not os.path.exists(CACHE_FILE):

        print(
            "📭 CACHE PARTITE NON ESISTE"
        )

        return []


    try:

        with open(
            CACHE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            dati = json.load(file)


        oggi = datetime.now().strftime(
            "%Y-%m-%d"
        )


        data_cache = dati.get(
            "data"
        )


        if data_cache != oggi:

            print(
                "🗑️ CACHE PARTITE VECCHIA:",
                data_cache
            )

            return []


        partite = dati.get(
            "partite",
            []
        )


        print(
            "📦 USO CACHE PARTITE:",
            len(partite)
        )


        return partite


    except Exception as e:

        print(
            "❌ ERRORE LETTURA CACHE PARTITE:",
            e
        )

        return []