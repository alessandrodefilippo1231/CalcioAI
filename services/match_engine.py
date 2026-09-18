from services.analisi_ai import analizza_partita
from services.storico_ai import salva_pronostico


# ============================================================
# LIMITI
# ============================================================

MAX_PARTITE_SCHEDINA = 10
MAX_PARTITE_TOP = 10
MAX_SCHEDINA = 3

MAX_NUOVE_SQUADRE_SCHEDINA = 4


# ============================================================
# PREPARA PARTITA
# ============================================================

def prepara_partita(partita):

    # --------------------------------------------------------
    # Se la partita arriva già con la struttura completa
    # --------------------------------------------------------

    if (
        partita.get("teams")
        and partita.get("league")
    ):

        fixture_originale = partita.get(
            "fixture",
            {}
        )

        data_completa = (
            fixture_originale.get("date")
            or partita.get("data")
            or partita.get("date")
            or ""
        )

        return {

            "fixture": {

                "id": (
                    fixture_originale.get("id")
                    or partita.get("id")
                ),

                "date": data_completa
            },

            "teams": partita["teams"],

            "league": partita["league"]

        }

    # --------------------------------------------------------
    # Partita proveniente da partite_oggi()
    # --------------------------------------------------------

    fixture_id = partita.get(
        "id"
    )

    casa = partita.get(
        "casa"
    )

    trasferta = partita.get(
        "trasferta"
    )

    home_id = partita.get(
        "home_id"
    )

    away_id = partita.get(
        "away_id"
    )

    lega = partita.get(
        "lega"
    )

    paese = partita.get(
        "paese"
    )

    # ========================================================
    # DATA COMPLETA
    # ========================================================

    data_completa = (
        partita.get("data")
        or partita.get("date")
        or partita.get("fixture_date")
        or ""
    )

    return {

        "fixture": {

            "id": fixture_id,

            "date": data_completa

        },

        "teams": {

            "home": {

                "id": home_id,

                "name": casa

            },

            "away": {

                "id": away_id,

                "name": trasferta

            }

        },

        "league": {

            "name": lega,

            "country": paese

        }

    }


# ============================================================
# ANALIZZA PARTITA
# ============================================================

def analizza_match(
    partita
):

    try:

        partita_preparata = prepara_partita(
            partita
        )

        return analizza_partita(
            partita_preparata
        )

    except Exception as e:

        print(
            "❌ ERRORE ANALISI PARTITA:",
            partita.get(
                "casa",
                ""
            ),
            "-",
            partita.get(
                "trasferta",
                ""
            ),
            "|",
            e
        )

        return None


# ============================================================
# TROVA TOP MATCH
# ============================================================

def trova_top_match(
    partite
):

    risultati = []

    squadre_usate = set()

    for partita in partite:

        if len(risultati) >= MAX_PARTITE_TOP:

            break

        try:

            analisi = analizza_match(
                partita
            )

            if not analisi:

                continue

            # ------------------------------------------------
            # DATI
            # ------------------------------------------------

            fiducia = analisi.get(
                "fiducia",
                0
            )

            ai_score = analisi.get(
                "ai_score",
                0
            )

            rischio = analisi.get(
                "rischio",
                ""
            )

            scelta = analisi.get(
                "scelta_ai",
                {}
            )

            if not isinstance(
                scelta,
                dict
            ):

                scelta = {}

            pronostico = scelta.get(
                "pronostico"
            ) or analisi.get(
                "pronostico"
            )

            value_index = scelta.get(
                "value_index",
                analisi.get(
                    "value_index",
                    0
                )
            )

            # ------------------------------------------------
            # FILTRI QUALITÀ
            # ------------------------------------------------

            if fiducia < 70:

                continue

            if ai_score < 75:

                continue

            if value_index < 75:

                continue

            if str(
                rischio
            ).lower() in (
                "alto",
                "high",
                "🔴 alto"
            ):

                continue

            if not pronostico:

                continue

            # ------------------------------------------------
            # SQUADRE
            # ------------------------------------------------

            casa = partita.get(
                "casa",
                ""
            )

            trasferta = partita.get(
                "trasferta",
                ""
            )

            chiave_casa = (
                casa.lower().strip()
            )

            chiave_trasferta = (
                trasferta.lower().strip()
            )

            if (
                chiave_casa in squadre_usate
                or
                chiave_trasferta in squadre_usate
            ):

                continue

            # ------------------------------------------------
            # RISULTATO
            # ------------------------------------------------

            risultati.append({

                "partita": partita,

                "analisi": analisi,

                "pronostico": pronostico,

                "fiducia": fiducia,

                "ai_score": ai_score,

                "value_index": value_index,

                "rischio": rischio

            })

            squadre_usate.add(
                chiave_casa
            )

            squadre_usate.add(
                chiave_trasferta
            )

            print(
                "🔥 TOP MATCH:",
                casa,
                "-",
                trasferta,
                "|",
                pronostico,
                "| Fiducia:",
                fiducia,
                "| Score:",
                ai_score,
                "| Value Index:",
                value_index
            )

        except Exception as e:

            print(
                "❌ ERRORE TOP MATCH:",
                e
            )

    return risultati


# ============================================================
# TROVA SCHEDINA
# ============================================================

def trova_schedina(
    partite
):

    print("")

    print(
        "🎯 AVVIO SCHEDINA AI"
    )

    # ========================================================
    # ANALISI CANDIDATI
    # ========================================================

    analizzati = []

    for partita in partite:

        try:

            analisi = analizza_match(
                partita
            )

            if not analisi:

                continue

            fiducia = analisi.get(
                "fiducia",
                0
            )

            ai_score = analisi.get(
                "ai_score",
                0
            )

            rischio = analisi.get(
                "rischio",
                ""
            )

            scelta = analisi.get(
                "scelta_ai",
                {}
            )

            if not isinstance(
                scelta,
                dict
            ):

                scelta = {}

            pronostico = scelta.get(
                "pronostico"
            ) or analisi.get(
                "pronostico"
            )

            value_index = scelta.get(
                "value_index",
                analisi.get(
                    "value_index",
                    0
                )
            )

            # ------------------------------------------------
            # FILTRI
            # ------------------------------------------------

            if not pronostico:

                continue

            if str(
                rischio
            ).lower() in (
                "alto",
                "high",
                "🔴 alto"
            ):

                continue

            if value_index < 70:

                continue

            if fiducia < 75:

                continue

            analizzati.append({

                "partita": partita,

                "analisi": analisi,

                "pronostico": pronostico,

                "fiducia": fiducia,

                "ai_score": ai_score,

                "value_index": value_index,

                "rischio": rischio

            })

        except Exception as e:

            print(
                "❌ ERRORE ANALISI SCHEDINA:",
                e
            )

    print(
        "🎯 CANDIDATE SCHEDINA:",
        len(analizzati)
    )

    # ========================================================
    # ORDINA PER QUALITÀ
    # ========================================================

    analizzati.sort(
        key=lambda x: (
            x.get(
                "value_index",
                0
            ),
            x.get(
                "fiducia",
                0
            ),
            x.get(
                "ai_score",
                0
            )
        ),
        reverse=True
    )

    # ========================================================
    # COSTRUZIONE SCHEDINA
    # ========================================================

    schedina = []

    mercati_usati = set()

    squadre_usate = set()

    # ========================================================
    # PRIMA FASE
    # MERCATI DIVERSI
    # ========================================================

    for elemento in analizzati:

        if len(schedina) >= MAX_SCHEDINA:

            break

        pronostico = elemento[
            "pronostico"
        ]

        partita = elemento[
            "partita"
        ]

        casa = partita.get(
            "casa",
            ""
        )

        trasferta = partita.get(
            "trasferta",
            ""
        )

        chiave_casa = (
            casa.lower().strip()
        )

        chiave_trasferta = (
            trasferta.lower().strip()
        )

        # ------------------------------------------------
        # Evita stessa squadra
        # ------------------------------------------------

        if (
            chiave_casa in squadre_usate
            or
            chiave_trasferta in squadre_usate
        ):

            continue

        # ------------------------------------------------
        # Evita stesso mercato
        # ------------------------------------------------

        mercato_base = (
            pronostico.lower().strip()
        )

        if mercato_base in mercati_usati:

            continue

        schedina.append(
            elemento
        )

        mercati_usati.add(
            mercato_base
        )

        squadre_usate.add(
            chiave_casa
        )

        squadre_usate.add(
            chiave_trasferta
        )

    # ========================================================
    # SE NON ARRIVIAMO A 3
    # RIEMPI CON I MIGLIORI
    # ========================================================

    if len(schedina) < MAX_SCHEDINA:

        for elemento in analizzati:

            if len(schedina) >= MAX_SCHEDINA:

                break

            if elemento in schedina:

                continue

            partita = elemento[
                "partita"
            ]

            casa = partita.get(
                "casa",
                ""
            )

            trasferta = partita.get(
                "trasferta",
                ""
            )

            chiave_casa = (
                casa.lower().strip()
            )

            chiave_trasferta = (
                trasferta.lower().strip()
            )

            if (
                chiave_casa in squadre_usate
                or
                chiave_trasferta in squadre_usate
            ):

                continue

            schedina.append(
                elemento
            )

            squadre_usate.add(
                chiave_casa
            )

            squadre_usate.add(
                chiave_trasferta
            )

    # ========================================================
    # SALVATAGGIO STORICO
    # ========================================================

    print("")

    print(
        "💾 SALVATAGGIO SCHEDINA NELLO STORICO..."
    )

    salvati = 0

    for elemento in schedina:

        try:

            partita = elemento[
                "partita"
            ]

            analisi = elemento[
                "analisi"
            ]

            salvato = salva_pronostico(
                partita,
                analisi
            )

            if salvato:

                salvati += 1

        except Exception as e:

            print(
                "❌ ERRORE SALVATAGGIO STORICO:",
                e
            )

    print(
        "💾 PRONOSTICI SALVATI:",
        salvati,
        "/",
        len(schedina)
    )

    # ========================================================
    # RISULTATO
    # ========================================================

    return schedina