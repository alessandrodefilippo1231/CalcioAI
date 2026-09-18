from config import FOOTBALL_API_KEY

from services.cache_statistiche import (
    prendi_statistiche,
    salva_statistiche
)

import requests
from datetime import datetime, timedelta


# ============================================================
# CONFIGURAZIONE
# ============================================================

# NON usare automaticamente stagioni vecchie.
# 2024 viene utilizzata solo come ultima possibilità
# per verificare se esistono dati API.
STAGIONI_DISPONIBILI = [
    2026,
    2025,
    2024
]


# ============================================================
# ULTIME PARTITE
# ============================================================

def ultime_partite(team_id):

    # ========================================================
    # CACHE
    # ========================================================

    dati_cache = prendi_statistiche(team_id)

    if dati_cache is not None:

        print("✅ USO CACHE STATISTICHE")

        return dati_cache


    # ========================================================
    # HEADERS API
    # ========================================================

    headers = {
        "x-apisports-key": FOOTBALL_API_KEY
    }


    partite = []


    # ========================================================
    # RICERCA STAGIONE
    # ========================================================

    for stagione in STAGIONI_DISPONIBILI:

        url = (
            "https://v3.football.api-sports.io/fixtures"
            f"?team={team_id}"
            f"&season={stagione}"
        )


        try:

            response = requests.get(
                url,
                headers=headers,
                timeout=15
            )


            dati = response.json()


            risultati = dati.get(
                "response",
                []
            )


            print(
                "STAGIONE:",
                stagione,
                "RISULTATI:",
                len(risultati)
            )


            if risultati:

                partite = risultati

                print(
                    "✅ DATI TROVATI STAGIONE:",
                    stagione
                )

                break


        except Exception as e:

            print(
                "❌ ERRORE STAGIONE:",
                stagione,
                e
            )


    # ========================================================
    # CONTROLLO DATI
    # ========================================================

    if not partite:

        print(
            "⚠️ NESSUNA PARTITA DISPONIBILE"
        )


        return {

            "forma": "N/D",

            "gol_fatti": 0,

            "gol_subiti": 0,

            "media_gol_fatti": 0,

            "media_gol_subiti": 0,

            "over15": 0,

            "over25": 0,

            "golgol": 0,

            "partite_analizzate": 0

        }


    # ========================================================
    # ORDINA PARTITE
    # ========================================================

    partite = sorted(
        partite,
        key=lambda x: x["fixture"]["date"],
        reverse=True
    )


    # ========================================================
    # PRENDI SOLO PARTITE CON RISULTATO
    # ========================================================

    partite_valide_lista = []


    for partita in partite:

        gol_home = partita["goals"]["home"]

        gol_away = partita["goals"]["away"]


        if gol_home is None or gol_away is None:

            continue


        # Controlliamo che la partita sia realmente conclusa

        status = partita["fixture"]["status"]["short"]


        if status not in [
            "FT",
            "AET",
            "PEN"
        ]:

            continue


        partite_valide_lista.append(
            partita
        )


    # ========================================================
    # ULTIME 5
    # ========================================================

    ultime = partite_valide_lista[:5]


    if not ultime:

        print(
            "⚠️ NESSUNA PARTITA CON RISULTATO VALIDO"
        )


        return {

            "forma": "N/D",

            "gol_fatti": 0,

            "gol_subiti": 0,

            "media_gol_fatti": 0,

            "media_gol_subiti": 0,

            "over15": 0,

            "over25": 0,

            "golgol": 0,

            "partite_analizzate": 0

        }


    # ========================================================
    # CONTATORI
    # ========================================================

    vittorie = 0

    pareggi = 0

    sconfitte = 0


    gol_fatti = 0

    gol_subiti = 0


    over15 = 0

    over25 = 0

    golgol = 0


    partite_valide = 0


    # ========================================================
    # ANALISI ULTIME 5
    # ========================================================

    for partita in ultime:


        gol_home = partita["goals"]["home"]

        gol_away = partita["goals"]["away"]


        home_id = partita["teams"]["home"]["id"]


        # ====================================================
        # SQUADRA CASA
        # ====================================================

        if home_id == team_id:

            fatti = gol_home

            subiti = gol_away


            if gol_home > gol_away:

                vittorie += 1


            elif gol_home == gol_away:

                pareggi += 1


            else:

                sconfitte += 1


        # ====================================================
        # SQUADRA TRASFERTA
        # ====================================================

        else:

            fatti = gol_away

            subiti = gol_home


            if gol_away > gol_home:

                vittorie += 1


            elif gol_home == gol_away:

                pareggi += 1


            else:

                sconfitte += 1


        # ====================================================
        # GOL
        # ====================================================

        gol_fatti += fatti

        gol_subiti += subiti


        totale_gol = (
            fatti +
            subiti
        )


        # ====================================================
        # OVER 1.5
        # ====================================================

        if totale_gol >= 2:

            over15 += 1


        # ====================================================
        # OVER 2.5
        # ====================================================

        if totale_gol >= 3:

            over25 += 1


        # ====================================================
        # GOAL
        # ====================================================

        if (
            fatti > 0
            and
            subiti > 0
        ):

            golgol += 1


        partite_valide += 1


    # ========================================================
    # CALCOLO MEDIE
    # ========================================================

    if partite_valide > 0:


        media_gol_fatti = round(
            gol_fatti /
            partite_valide,
            2
        )


        media_gol_subiti = round(
            gol_subiti /
            partite_valide,
            2
        )


        percentuale_over15 = round(
            (
                over15 /
                partite_valide
            ) * 100
        )


        percentuale_over25 = round(
            (
                over25 /
                partite_valide
            ) * 100
        )


        percentuale_golgol = round(
            (
                golgol /
                partite_valide
            ) * 100
        )


    else:

        media_gol_fatti = 0

        media_gol_subiti = 0

        percentuale_over15 = 0

        percentuale_over25 = 0

        percentuale_golgol = 0


    # ========================================================
    # STATISTICHE FINALI
    # ========================================================

    statistiche = {

        "forma":
        f"{vittorie}V "
        f"{pareggi}P "
        f"{sconfitte}S",


        "gol_fatti":
        gol_fatti,


        "gol_subiti":
        gol_subiti,


        "media_gol_fatti":
        media_gol_fatti,


        "media_gol_subiti":
        media_gol_subiti,


        "over15":
        percentuale_over15,


        "over25":
        percentuale_over25,


        "golgol":
        percentuale_golgol,


        "partite_analizzate":
        partite_valide

    }


    # ========================================================
    # LOG
    # ========================================================

    print(
        "📊 STATISTICHE FINALI:",
        statistiche
    )


    # ========================================================
    # SALVA CACHE
    # ========================================================

    salva_statistiche(
        team_id,
        statistiche
    )


    return statistiche