import os
import requests

from datetime import datetime, timezone

from dotenv import load_dotenv

from services.storico_ai import (
    pronostici_in_attesa,
    aggiorna_esito
)


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


# ============================================================
# STATI FINALI
# ============================================================

STATI_FINITE = {

    "FT",
    "AET",
    "PEN"

}


# ============================================================
# STATI DA ANNULLARE
# ============================================================

STATI_ANNULLATI = {

    "CANC",
    "ABD",
    "AWD",
    "WO"

}


# ============================================================
# CONVERSIONE DATA
# ============================================================

def converti_data(data):

    if not data:

        return None


    try:

        data = data.replace(
            "Z",
            "+00:00"
        )


        risultato = datetime.fromisoformat(
            data
        )


        if risultato.tzinfo is None:

            risultato = risultato.replace(
                tzinfo=timezone.utc
            )


        return risultato


    except Exception as e:

        print(

            "⚠️ ERRORE CONVERSIONE DATA:",

            data,

            e

        )

        return None


# ============================================================
# CONTROLLO DATA
# ============================================================

def partita_pronta_per_controllo(
    data_partita
):

    # --------------------------------------------------------
    # DATA COMPLETA
    # --------------------------------------------------------

    data = converti_data(
        data_partita
    )


    # --------------------------------------------------------
    # DATA NON DISPONIBILE / VECCHIO FORMATO
    # --------------------------------------------------------

    if data is None:

        # Se abbiamo solo HH:MM
        # lasciamo che sia API-Football
        # a dirci lo stato della partita.

        if (
            isinstance(
                data_partita,
                str
            )
            and
            len(data_partita) == 5
            and
            data_partita[2] == ":"
        ):

            print(

                "⚠️ DATA VECCHIO FORMATO:",

                data_partita,

                "→ controllo tramite API"

            )

            return True


        return False


    # --------------------------------------------------------
    # ORA ATTUALE
    # --------------------------------------------------------

    adesso = datetime.now(
        timezone.utc
    )


    # --------------------------------------------------------
    # DIFFERENZA
    # --------------------------------------------------------

    ore_passate = (

        adesso - data

    ).total_seconds() / 3600


    # --------------------------------------------------------
    # PARTITA TROPPO RECENTE
    # --------------------------------------------------------

    if ore_passate < 2:

        return False


    return True


# ============================================================
# RECUPERA RISULTATO DA API-FOOTBALL
# ============================================================

def recupera_risultato(
    fixture_id
):

    if not FOOTBALL_API_KEY:

        print(
            "❌ FOOTBALL_API_KEY NON TROVATA"
        )

        return None


    headers = {

        "x-apisports-key":
            FOOTBALL_API_KEY

    }


    params = {

        "id": fixture_id

    }


    try:

        response = requests.get(

            API_URL,

            headers=headers,

            params=params,

            timeout=15

        )


    except Exception as e:

        print(

            "❌ ERRORE RICHIESTA API:",

            fixture_id,

            e

        )

        return None


    # --------------------------------------------------------
    # HTTP
    # --------------------------------------------------------

    if response.status_code != 200:

        print(

            "❌ API ERROR:",

            response.status_code,

            "| fixture:",

            fixture_id

        )

        return None


    # --------------------------------------------------------
    # JSON
    # --------------------------------------------------------

    try:

        dati = response.json()

    except Exception as e:

        print(

            "❌ ERRORE JSON API:",

            fixture_id,

            e

        )

        return None


    risultati = dati.get(
        "response",
        []
    )


    if not risultati:

        print(

            "⚠️ RISULTATO NON TROVATO:",

            fixture_id

        )

        return None


    partita = risultati[0]


    fixture = partita.get(
        "fixture",
        {}
    )


    teams = partita.get(
        "teams",
        {}
    )


    goals = partita.get(
        "goals",
        {}
    )


    status = fixture.get(
        "status",
        {}
    ).get(
        "short"
    )


    casa = teams.get(
        "home",
        {}
    ).get(
        "name",
        "Casa"
    )


    trasferta = teams.get(
        "away",
        {}
    ).get(
        "name",
        "Trasferta"
    )


    gol_casa = goals.get(
        "home"
    )


    gol_trasferta = goals.get(
        "away"
    )


    # ========================================================
    # DATA REALE RECUPERATA DA API
    # ========================================================

    data_reale = fixture.get(
        "date"
    )


    return {

        "status": status,

        "casa": casa,

        "trasferta": trasferta,

        "gol_casa": gol_casa,

        "gol_trasferta": gol_trasferta,

        "data": data_reale

    }


# ============================================================
# CONTROLLA PRONOSTICO
# ============================================================

def controlla_pronostico(
    pronostico,
    gol_casa,
    gol_trasferta
):

    if (
        gol_casa is None
        or
        gol_trasferta is None
    ):

        return None


    totale_gol = (

        gol_casa
        +
        gol_trasferta

    )


    pronostico = (
        pronostico
        .strip()
        .lower()
    )


    # ========================================================
    # 1X2
    # ========================================================

    if pronostico == "1":

        return (
            gol_casa
            >
            gol_trasferta
        )


    if pronostico == "x":

        return (
            gol_casa
            ==
            gol_trasferta
        )


    if pronostico == "2":

        return (
            gol_casa
            <
            gol_trasferta
        )


    # ========================================================
    # OVER
    # ========================================================

    if pronostico in (
        "over 1.5",
        "over 1.5 gol"
    ):

        return totale_gol >= 2


    if pronostico in (
        "over 2.5",
        "over 2.5 gol"
    ):

        return totale_gol >= 3


    if pronostico in (
        "over 3.5",
        "over 3.5 gol"
    ):

        return totale_gol >= 4


    # ========================================================
    # UNDER
    # ========================================================

    if pronostico in (
        "under 1.5",
        "under 1.5 gol"
    ):

        return totale_gol <= 1


    if pronostico in (
        "under 2.5",
        "under 2.5 gol"
    ):

        return totale_gol <= 2


    if pronostico in (
        "under 3.5",
        "under 3.5 gol"
    ):

        return totale_gol <= 3


    # ========================================================
    # GOL / NO GOL
    # ========================================================

    if pronostico in (
        "goal",
        "gol",
        "gg"
    ):

        return (

            gol_casa > 0
            and
            gol_trasferta > 0

        )


    if pronostico in (
        "no goal",
        "no gol",
        "ng"
    ):

        return (

            gol_casa == 0
            or
            gol_trasferta == 0

        )


    # ========================================================
    # DOPPIA CHANCE
    # ========================================================

    if pronostico == "1x":

        return (
            gol_casa
            >=
            gol_trasferta
        )


    if pronostico == "x2":

        return (
            gol_casa
            <=
            gol_trasferta
        )


    if pronostico == "12":

        return (
            gol_casa
            !=
            gol_trasferta
        )


    # ========================================================
    # MERCATO NON RICONOSCIUTO
    # ========================================================

    print(

        "⚠️ MERCATO NON RICONOSCIUTO:",

        pronostico

    )


    return None


# ============================================================
# VERIFICA SINGOLO PRONOSTICO
# ============================================================

def verifica_singolo(
    pronostico
):

    id_analisi = pronostico[
        "id"
    ]

    fixture_id = pronostico[
        "fixture_id"
    ]

    mercato = pronostico[
        "pronostico"
    ]

    casa_storico = pronostico[
        "casa"
    ]

    trasferta_storico = pronostico[
        "trasferta"
    ]


    print(

        "🔎 CONTROLLO:",

        casa_storico,

        "-",

        trasferta_storico,

        "|",

        mercato

    )


    # ========================================================
    # CONTROLLO DATA
    # ========================================================

    if not partita_pronta_per_controllo(

        pronostico[
            "data_partita"
        ]

    ):

        print(

            "⏳ PARTITA TROPPO RECENTE:",

            fixture_id

        )

        return {

            "stato": "ATTESA"

        }


    # ========================================================
    # API
    # ========================================================

    risultato = recupera_risultato(

        fixture_id

    )


    if risultato is None:

        return {

            "stato": "ERRORE"

        }


    status = risultato[
        "status"
    ]


    # ========================================================
    # PARTITA ANNULLATA
    # ========================================================

    if status in STATI_ANNULLATI:

        aggiorna_esito(

            id_analisi,

            f"Stato partita: {status}",

            "ANNULLATA"

        )


        print(

            "🚫 PARTITA ANNULLATA:",

            casa_storico,

            "-",

            trasferta_storico

        )


        return {

            "stato": "ANNULLATA"

        }


    # ========================================================
    # PARTITA NON FINITA
    # ========================================================

    if status not in STATI_FINITE:

        print(

            "⏳ PARTITA NON FINITA:",

            casa_storico,

            "-",

            trasferta_storico,

            "| Stato:",

            status

        )


        return {

            "stato": "IN_CORSO"

        }


    # ========================================================
    # RISULTATO
    # ========================================================

    gol_casa = risultato[
        "gol_casa"
    ]

    gol_trasferta = risultato[
        "gol_trasferta"
    ]


    if (
        gol_casa is None
        or
        gol_trasferta is None
    ):

        print(

            "⚠️ GOL NON DISPONIBILI:",

            fixture_id

        )

        return {

            "stato": "ERRORE"

        }


    risultato_testo = (

        f"{gol_casa}-{gol_trasferta}"

    )


    # ========================================================
    # VERIFICA PRONOSTICO
    # ========================================================

    corretto = controlla_pronostico(

        mercato,

        gol_casa,

        gol_trasferta

    )


    if corretto is None:

        print(

            "⚠️ IMPOSSIBILE VERIFICARE:",

            mercato

        )

        return {

            "stato": "NON_RICONOSCIUTO"

        }


    # ========================================================
    # ESITO
    # ========================================================

    if corretto:

        esito = "CORRETTO"

    else:

        esito = "ERRATO"


    # ========================================================
    # AGGIORNA DATABASE
    # ========================================================

    aggiorna_esito(

        id_analisi,

        risultato_testo,

        esito

    )


    print(

        "🏁 RISULTATO:",

        casa_storico,

        "-",

        trasferta_storico,

        "|",

        risultato_testo,

        "|",

        mercato,

        "|",

        esito

    )


    return {

        "stato": esito,

        "risultato": risultato_testo,

        "pronostico": mercato

    }


# ============================================================
# VERIFICA AUTOMATICA COMPLETA
# ============================================================

def verifica_pronostici():

    print(
        ""
    )

    print(
        "🤖 AVVIO VERIFICA AUTOMATICA"
    )


    pronostici = pronostici_in_attesa()


    if not pronostici:

        print(
            "📚 NESSUN PRONOSTICO DA VERIFICARE"
        )

        return []


    print(

        "📚 PRONOSTICI IN ATTESA:",

        len(pronostici)

    )


    risultati = []


    # ========================================================
    # CONTROLLO PRONOSTICI
    # ========================================================

    for pronostico in pronostici:

        try:

            risultato = verifica_singolo(

                pronostico

            )


            risultati.append({

                "id": pronostico[
                    "id"
                ],

                "casa": pronostico[
                    "casa"
                ],

                "trasferta": pronostico[
                    "trasferta"
                ],

                "pronostico": pronostico[
                    "pronostico"
                ],

                **risultato

            })


        except Exception as e:

            print(

                "❌ ERRORE VERIFICA:",

                pronostico.get(
                    "casa",
                    ""
                ),

                "-",

                pronostico.get(
                    "trasferta",
                    ""
                ),

                "|",

                e

            )


    # ========================================================
    # RIEPILOGO
    # ========================================================

    corretti = sum(

        1

        for r in risultati

        if r.get(
            "stato"
        ) == "CORRETTO"

    )


    errati = sum(

        1

        for r in risultati

        if r.get(
            "stato"
        ) == "ERRATO"

    )


    annullati = sum(

        1

        for r in risultati

        if r.get(
            "stato"
        ) == "ANNULLATA"

    )


    attesa = sum(

        1

        for r in risultati

        if r.get(
            "stato"
        ) in (
            "ATTESA",
            "IN_CORSO"
        )

    )


    print(
        ""
    )

    print(
        "📊 RIEPILOGO VERIFICA:"
    )

    print(
        "✅ CORRETTI:",
        corretti
    )

    print(
        "❌ ERRATI:",
        errati
    )

    print(
        "🚫 ANNULLATI:",
        annullati
    )

    print(
        "⏳ ANCORA IN ATTESA:",
        attesa
    )

    print(
        "🤖 VERIFICA AUTOMATICA COMPLETATA"
    )


    return risultati