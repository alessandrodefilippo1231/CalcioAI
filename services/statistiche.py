from config import FOOTBALL_API_KEY

from services.cache_statistiche import (
    prendi_statistiche,
    salva_statistiche
)

import requests
from datetime import datetime, timedelta, timezone


# ============================================================
# CONFIGURAZIONE
# ============================================================

BASE_URL = "https://api.football-data.org/v4"

# Numero massimo di partite utilizzate per la forma
NUMERO_ULTIME_PARTITE = 5


# ============================================================
# STATISTICHE VUOTE
# ============================================================

def statistiche_vuote():

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
        "X-Auth-Token": FOOTBALL_API_KEY
    }


    # ========================================================
    # DATA DI RICERCA
    # ========================================================

    oggi = datetime.now(timezone.utc)

    data_fine = oggi.strftime("%Y-%m-%d")

    # Cerchiamo abbastanza indietro per trovare
    # le ultime partite concluse.
    data_inizio = (
        oggi - timedelta(days=120)
    ).strftime("%Y-%m-%d")


    # ========================================================
    # URL FOOTBALL-DATA.ORG
    # ========================================================

    url = (
        f"{BASE_URL}/teams/"
        f"{team_id}/matches"
    )


    params = {

        "dateFrom": data_inizio,

        "dateTo": data_fine,

        "status": "FINISHED",

        "limit": 100

    }


    try:

        print(
            "🌐 RICERCA ULTIME PARTITE"
        )

        print(
            "TEAM ID:",
            team_id
        )

        print(
            "DAL:",
            data_inizio
        )

        print(
            "AL:",
            data_fine
        )


        response = requests.get(

            url,

            headers=headers,

            params=params,

            timeout=15

        )


        print(
            "📡 STATUS API:",
            response.status_code
        )


        response.raise_for_status()


        dati = response.json()


        partite = dati.get(
            "matches",
            []
        )


        print(
            "📊 RISULTATI API:",
            len(partite)
        )


    except Exception as e:

        print(
            "❌ ERRORE RICERCA STATISTICHE:",
            e
        )

        return statistiche_vuote()


    # ========================================================
    # CONTROLLO DATI
    # ========================================================

    if not partite:

        print(
            "⚠️ NESSUNA PARTITA DISPONIBILE"
        )

        return statistiche_vuote()


    # ========================================================
    # ORDINA PARTITE
    # ========================================================

    partite = sorted(

        partite,

        key=lambda x: x.get(
            "utcDate",
            ""
        ),

        reverse=True

    )


    # ========================================================
    # PRENDI SOLO PARTITE CON RISULTATO
    # ========================================================

    partite_valide_lista = []


    for partita in partite:

        status = partita.get(
            "status"
        )


        if status != "FINISHED":

            continue


        score = partita.get(
            "score",
            {}
        )


        full_time = score.get(
            "fullTime",
            {}
        )


        gol_home = full_time.get(
            "home"
        )

        gol_away = full_time.get(
            "away"
        )


        if gol_home is None or gol_away is None:

            continue


        partite_valide_lista.append(
            partita
        )


    # ========================================================
    # ULTIME 5
    # ========================================================

    ultime = partite_valide_lista[
        :NUMERO_ULTIME_PARTITE
    ]


    if not ultime:

        print(
            "⚠️ NESSUNA PARTITA CON RISULTATO VALIDO"
        )

        return statistiche_vuote()


    print(
        "✅ ULTIME PARTITE ANALIZZATE:",
        len(ultime)
    )


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

        home_team = partita.get(
            "homeTeam",
            {}
        )

        away_team = partita.get(
            "awayTeam",
            {}
        )


        home_id = home_team.get(
            "id"
        )

        away_id = away_team.get(
            "id"
        )


        score = partita.get(
            "score",
            {}
        )


        full_time = score.get(
            "fullTime",
            {}
        )


        gol_home = full_time.get(
            "home"
        )

        gol_away = full_time.get(
            "away"
        )


        if gol_home is None or gol_away is None:

            continue


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

        elif away_id == team_id:

            fatti = gol_away

            subiti = gol_home


            if gol_away > gol_home:

                vittorie += 1


            elif gol_home == gol_away:

                pareggi += 1


            else:

                sconfitte += 1


        else:

            continue


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
    # CONTROLLO FINALE
    # ========================================================

    if partite_valide == 0:

        print(
            "⚠️ NESSUNA PARTITA VALIDA PER IL TEAM"
        )

        return statistiche_vuote()


    # ========================================================
    # CALCOLO MEDIE
    # ========================================================

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