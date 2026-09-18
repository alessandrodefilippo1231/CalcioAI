from services.statistiche import ultime_partite
from services.ai_pronostico import genera_pronostico, calcola_indicatori
from services.ai_score import calcola_ai_score
from services.mercati_ai import calcola_mercati_ai, miglior_mercato
from services.decision_engine import scegli_pronostico
from services.ai_spiegazione import genera_spiegazione


def analizza_partita(partita):

    # ==========================================================
    # CONTROLLO STRUTTURA PARTITA
    # ==========================================================

    if "teams" not in partita:

        print("❌ DATI INSUFFICIENTI: manca 'teams'")

        return {
            "pronostico": "Dati insufficienti",
            "fiducia": 0,
            "rischio": "N/D",
            "ai_score": 0,
            "indicatori": {},
            "mercati": {},
            "migliori_mercati": [],
            "scelta_ai": {},
            "spiegazione": "Struttura partita non valida.",
            "analisi": "❌ Dati partita non disponibili."
        }

    if (
        "home" not in partita["teams"]
        or
        "away" not in partita["teams"]
    ):

        print("❌ DATI INSUFFICIENTI: manca home/away")

        return {
            "pronostico": "Dati insufficienti",
            "fiducia": 0,
            "rischio": "N/D",
            "ai_score": 0,
            "indicatori": {},
            "mercati": {},
            "migliori_mercati": [],
            "scelta_ai": {},
            "spiegazione": "Squadre non disponibili.",
            "analisi": "❌ Squadre della partita non disponibili."
        }

    casa = partita["teams"]["home"]
    trasferta = partita["teams"]["away"]

    nome_casa = casa.get(
        "name",
        "Casa"
    )

    nome_trasferta = trasferta.get(
        "name",
        "Trasferta"
    )

    print(
        f"🔎 ANALISI DATI: {nome_casa} - {nome_trasferta}"
    )

    # ==========================================================
    # CONTROLLO ID SQUADRE
    # ==========================================================

    home_id = casa.get("id")
    away_id = trasferta.get("id")

    if not home_id:

        print(
            f"❌ ID CASA MANCANTE: {nome_casa}"
        )

        return {
            "pronostico": "Dati insufficienti",
            "fiducia": 0,
            "rischio": "N/D",
            "ai_score": 0,
            "indicatori": {},
            "mercati": {},
            "migliori_mercati": [],
            "scelta_ai": {},
            "spiegazione": "ID squadra casa non disponibile.",
            "analisi": "❌ ID squadra casa non disponibile."
        }

    if not away_id:

        print(
            f"❌ ID TRASFERTA MANCANTE: {nome_trasferta}"
        )

        return {
            "pronostico": "Dati insufficienti",
            "fiducia": 0,
            "rischio": "N/D",
            "ai_score": 0,
            "indicatori": {},
            "mercati": {},
            "migliori_mercati": [],
            "scelta_ai": {},
            "spiegazione": "ID squadra trasferta non disponibile.",
            "analisi": "❌ ID squadra trasferta non disponibile."
        }

    # ==========================================================
    # RECUPERO STATISTICHE
    # ==========================================================

    try:

        stats_casa = ultime_partite(
            home_id
        )

        stats_trasferta = ultime_partite(
            away_id
        )

    except Exception as e:

        print(
            f"❌ ERRORE STATISTICHE: "
            f"{nome_casa} - {nome_trasferta} | {e}"
        )

        return {
            "pronostico": "Dati insufficienti",
            "fiducia": 0,
            "rischio": "N/D",
            "ai_score": 0,
            "indicatori": {},
            "mercati": {},
            "migliori_mercati": [],
            "scelta_ai": {},
            "spiegazione": "Errore nel recupero delle statistiche.",
            "analisi": "❌ Impossibile recuperare lo storico."
        }

    # ==========================================================
    # CONTROLLO STATISTICHE
    # ==========================================================

    if not stats_casa:

        print(
            f"❌ STATISTICHE CASA VUOTE: "
            f"{nome_casa} ({home_id})"
        )

    if not stats_trasferta:

        print(
            f"❌ STATISTICHE TRASFERTA VUOTE: "
            f"{nome_trasferta} ({away_id})"
        )

    if not stats_casa or not stats_trasferta:

        print(
            f"⚠️ DATI INSUFFICIENTI: "
            f"{nome_casa} - {nome_trasferta}"
        )

        return {
            "pronostico": "Dati insufficienti",
            "fiducia": 0,
            "rischio": "N/D",
            "ai_score": 0,
            "indicatori": {},
            "mercati": {},
            "migliori_mercati": [],
            "scelta_ai": {},
            "spiegazione": "Storico non disponibile.",
            "analisi": "❌ Storico non disponibile."
        }

    print(
        f"✅ STATISTICHE DISPONIBILI: "
        f"{nome_casa} - {nome_trasferta}"
    )

    # ==========================================================
    # CONTROLLO GOL
    # ==========================================================

    gol_fatti_casa = stats_casa.get(
        "gol_fatti",
        0
    )

    gol_fatti_trasferta = stats_trasferta.get(
        "gol_fatti",
        0
    )

    if (
        gol_fatti_casa == 0
        and
        gol_fatti_trasferta == 0
    ):

        print(
            f"⚠️ GOL FATTI ENTRAMBE 0: "
            f"{nome_casa} - {nome_trasferta}"
        )

        # NON blocchiamo immediatamente l'analisi.
        #
        # Uno 0 può indicare semplicemente
        # una statistica incompleta.
        #
        # Lasciamo decidere agli indicatori
        # e al Decision Engine.

    # ==========================================================
    # INDICATORI AI
    # ==========================================================

    try:

        indicatori = calcola_indicatori(
            stats_casa,
            stats_trasferta
        )

    except Exception as e:

        print(
            f"❌ ERRORE INDICATORI: "
            f"{nome_casa} - {nome_trasferta} | {e}"
        )

        return {
            "pronostico": "Dati insufficienti",
            "fiducia": 0,
            "rischio": "N/D",
            "ai_score": 0,
            "indicatori": {},
            "mercati": {},
            "migliori_mercati": [],
            "scelta_ai": {},
            "spiegazione": "Errore nel calcolo degli indicatori.",
            "analisi": "❌ Errore analisi indicatori."
        }

    print(
        f"📊 INDICATORI: "
        f"Over15={indicatori.get('over15', 0)} | "
        f"Over25={indicatori.get('over25', 0)} | "
        f"GolGol={indicatori.get('golgol', 0)} | "
        f"Under35={indicatori.get('under35', 0)}"
    )

    # ==========================================================
    # LEGA
    # ==========================================================

    lega = partita.get(
        "league",
        {}
    ).get(
        "name",
        "Campionato"
    )

    # ==========================================================
    # AI SCORE
    # ==========================================================

    try:

        ai_score = calcola_ai_score(
            stats_casa,
            stats_trasferta,
            indicatori,
            lega
        )

    except Exception as e:

        print(
            f"❌ ERRORE AI SCORE: "
            f"{nome_casa} - {nome_trasferta} | {e}"
        )

        return {
            "pronostico": "Dati insufficienti",
            "fiducia": 0,
            "rischio": "N/D",
            "ai_score": 0,
            "indicatori": indicatori,
            "mercati": {},
            "migliori_mercati": [],
            "scelta_ai": {},
            "spiegazione": "Errore AI Score.",
            "analisi": "❌ Errore nel calcolo AI Score."
        }

    print(
        f"🤖 AI SCORE: "
        f"{nome_casa} - {nome_trasferta} = {ai_score}/100"
    )

    # ==========================================================
    # PRONOSTICO BASE
    # ==========================================================

    try:

        pronostico = genera_pronostico(
            stats_casa,
            stats_trasferta,
            indicatori,
            ai_score
        )

    except Exception as e:

        print(
            f"❌ ERRORE PRONOSTICO: "
            f"{nome_casa} - {nome_trasferta} | {e}"
        )

        return {
            "pronostico": "Dati insufficienti",
            "fiducia": 0,
            "rischio": "N/D",
            "ai_score": ai_score,
            "indicatori": indicatori,
            "mercati": {},
            "migliori_mercati": [],
            "scelta_ai": {},
            "spiegazione": "Errore generazione pronostico.",
            "analisi": "❌ Errore nel pronostico."
        }

    # ==========================================================
    # RECUPERO FIDUCIA BASE
    # ==========================================================
    #
    # Il Learning 2.0 deve conoscere la fiducia reale
    # prodotta dall'analisi.
    #
    # Il valore utilizzato è la probabilità del pronostico base.
    #
    # In questo modo il Decision Engine potrà confrontare
    # storicamente le fasce di fiducia:
    #
    # 60-69
    # 70-79
    # 80-89
    # 90-100
    #
    # ==========================================================

    try:

        fiducia = pronostico.get(
            "fiducia",
            pronostico.get(
                "probabilita",
                0
            )
        )

    except AttributeError:

        fiducia = 0

    try:

        fiducia = float(
            fiducia
        )

    except (
        TypeError,
        ValueError
    ):

        fiducia = 0

    fiducia = max(
        0,
        min(
            fiducia,
            100
        )
    )

    print(
        f"🎯 FIDUCIA BASE: "
        f"{nome_casa} - {nome_trasferta} = "
        f"{fiducia:.0f}%"
    )

    # ==========================================================
    # MERCATI AI
    # ==========================================================

    try:

        mercati = calcola_mercati_ai(
            stats_casa,
            stats_trasferta,
            indicatori
        )

    except Exception as e:

        print(
            f"❌ ERRORE MERCATI AI: "
            f"{nome_casa} - {nome_trasferta} | {e}"
        )

        mercati = {}

    print(
        f"📊 MERCATI DISPONIBILI: {mercati}"
    )

    # ==========================================================
    # MIGLIORI MERCATI
    # ==========================================================

    try:

        migliori = miglior_mercato(
            mercati
        )

    except Exception as e:

        print(
            f"❌ ERRORE MIGLIORI MERCATI: {e}"
        )

        migliori = []

    # ==========================================================
    # DECISION ENGINE
    # ==========================================================

    try:

        scelta_ai = scegli_pronostico(
            mercati,
            ai_score,
            pronostico.get(
                "rischio",
                "N/D"
            ),
            stats_casa,
            stats_trasferta,
            indicatori,
            lega,
            fiducia=fiducia
        )

    except Exception as e:

        print(
            f"❌ ERRORE DECISION ENGINE: "
            f"{nome_casa} - {nome_trasferta} | {e}"
        )

        return {
            "pronostico": "Dati insufficienti",
            "fiducia": fiducia,
            "rischio": pronostico.get(
                "rischio",
                "N/D"
            ),
            "ai_score": ai_score,
            "indicatori": indicatori,
            "mercati": mercati,
            "migliori_mercati": migliori,
            "scelta_ai": {},
            "spiegazione": "Errore Decision Engine.",
            "analisi": "❌ Errore nella scelta del pronostico."
        }

    # ==========================================================
    # CONTROLLO SCELTA AI
    # ==========================================================

    if not scelta_ai:

        print(
            f"⚠️ NESSUNA SCELTA AI: "
            f"{nome_casa} - {nome_trasferta}"
        )

        return {
            "pronostico": "Dati insufficienti",
            "fiducia": fiducia,
            "rischio": pronostico.get(
                "rischio",
                "N/D"
            ),
            "ai_score": ai_score,
            "indicatori": indicatori,
            "mercati": mercati,
            "migliori_mercati": migliori,
            "scelta_ai": {},
            "spiegazione": "Nessun mercato selezionato.",
            "analisi": "❌ Nessun pronostico disponibile."
        }

    mercato_scelto = scelta_ai.get(
        "mercato",
        "Nessun mercato"
    )

    probabilita = scelta_ai.get(
        "probabilita",
        0
    )

    score_finale = scelta_ai.get(
        "score_finale",
        0
    )

    value_index = scelta_ai.get(
        "value_index",
        0
    )

    rischio = scelta_ai.get(
        "rischio",
        pronostico.get(
            "rischio",
            "N/D"
        )
    )

    # ==========================================================
    # SE DECISION ENGINE RIFIUTA
    # ==========================================================

    if mercato_scelto == "Nessun pronostico":

        print(
            f"⚠️ DECISION ENGINE HA RIFIUTATO: "
            f"{nome_casa} - {nome_trasferta} | "
            f"Value Index: {value_index}"
        )

    else:

        print(
            f"✅ PRONOSTICO AI: "
            f"{nome_casa} - {nome_trasferta} | "
            f"{mercato_scelto} | "
            f"Probabilità: {probabilita}% | "
            f"AI Score: {ai_score} | "
            f"Value Index: {value_index}"
        )

    # ==========================================================
    # SPIEGAZIONE AI
    # ==========================================================

    try:

        spiegazione = genera_spiegazione(
            stats_casa,
            stats_trasferta,
            mercato_scelto
        )

    except Exception as e:

        print(
            f"❌ ERRORE SPIEGAZIONE AI: {e}"
        )

        spiegazione = (
            "Analisi basata sui dati statistici "
            "recenti delle due squadre."
        )

    # ==========================================================
    # DATI STATISTICI
    # ==========================================================

    forma_casa = stats_casa.get(
        "forma",
        "N/D"
    )

    gol_subiti_casa = stats_casa.get(
        "gol_subiti",
        0
    )

    forma_trasferta = stats_trasferta.get(
        "forma",
        "N/D"
    )

    gol_subiti_trasferta = stats_trasferta.get(
        "gol_subiti",
        0
    )

    over15 = indicatori.get(
        "over15",
        0
    )

    over25 = indicatori.get(
        "over25",
        0
    )

    golgol = indicatori.get(
        "golgol",
        0
    )

    under35 = indicatori.get(
        "under35",
        0
    )

    # ==========================================================
    # COSTRUZIONE ANALISI
    # ==========================================================

    analisi = (

        f"🏆 {lega}\n\n"

        f"🏠 {nome_casa}\n"
        f"📈 Forma: {forma_casa}\n"
        f"⚽ Gol fatti: {gol_fatti_casa}\n"
        f"🥅 Gol subiti: {gol_subiti_casa}\n\n"

        f"✈️ {nome_trasferta}\n"
        f"📈 Forma: {forma_trasferta}\n"
        f"⚽ Gol fatti: {gol_fatti_trasferta}\n"
        f"🥅 Gol subiti: {gol_subiti_trasferta}\n\n"

        f"🎯 PRONOSTICO AI\n"
        f"{mercato_scelto}\n"
        f"📊 Probabilità: {probabilita}%\n"
        f"🤖 AI Score: {ai_score}/100\n"
        f"🧠 Decision Score: {score_finale}/100\n"
        f"💎 Value Index: {value_index}/100\n"
        f"⚠️ Rischio: {rischio}\n\n"

        f"🧠 MOTIVAZIONE AI\n"
        f"{spiegazione}\n\n"

        f"📊 INDICATORI AI\n"
        f"⚽ Over 1.5: {over15}%\n"
        f"⚽ Over 2.5: {over25}%\n"
        f"🤝 Gol/Gol: {golgol}%\n"
        f"🛡 Under 3.5: {under35}%\n\n"

        f"📈 MIGLIORI MERCATI AI\n"
    )

    # ==========================================================
    # AGGIUNTA MIGLIORI MERCATI
    # ==========================================================

    if migliori:

        for posizione, elemento in enumerate(
            migliori,
            start=1
        ):

            try:

                mercato, valore = elemento

                analisi += (
                    f"{posizione}️⃣ "
                    f"{mercato}: {valore}%\n"
                )

            except (
                ValueError,
                TypeError
            ):

                analisi += (
                    f"{posizione}️⃣ "
                    f"{elemento}\n"
                )

    else:

        analisi += (
            "Nessun mercato disponibile.\n"
        )

    # ==========================================================
    # RISULTATO FINALE
    # ==========================================================

    return {

        "pronostico": mercato_scelto,

        "fiducia": probabilita,

        "fiducia_base": fiducia,

        "rischio": rischio,

        "ai_score": ai_score,

        "indicatori": indicatori,

        "mercati": mercati,

        "migliori_mercati": migliori,

        "scelta_ai": scelta_ai,

        "spiegazione": spiegazione,

        "analisi": analisi
    }