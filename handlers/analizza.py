from telegram import Update
from telegram.ext import ContextTypes

from services.seleziona_partita import seleziona_partita
from services.statistiche import ultime_partite
from services.ai_pronostico import genera_pronostico, calcola_indicatori
from services.ai_score import calcola_ai_score, analizza_componenti_score
from services.ai_spiegazione import genera_spiegazione
from services.affidabilita_ai import livello_affidabilita
from services.mercati_ai import calcola_mercati_ai, miglior_mercato
from services.storico_ai import salva_pronostico
from services.decision_engine import scegli_pronostico


BANDIERE = {
    "Italy": "🇮🇹",
    "England": "🏴",
    "Spain": "🇪🇸",
    "Germany": "🇩🇪",
    "France": "🇫🇷",
    "Portugal": "🇵🇹",
    "Netherlands": "🇳🇱",
    "Belgium": "🇧🇪",
    "Turkey": "🇹🇷",
    "Brazil": "🇧🇷",
    "Argentina": "🇦🇷",
    "Mexico": "🇲🇽",
    "USA": "🇺🇸",
    "Colombia": "🇨🇴",
    "Ecuador": "🇪🇨"
}


async def analizza(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:

        await update.message.reply_text(
            "Scrivi il numero della partita.\n\n"
            "Esempio:\n"
            "/analizza 10"
        )

        return


    numero = context.args[0]

    partita = seleziona_partita(numero)

    if partita is None:

        await update.message.reply_text(
            "❌ Partita non trovata."
        )

        return


    lega = partita["lega"]

    bandiera = BANDIERE.get(
        partita.get("paese", ""),
        "🌍"
    )

    home = partita["casa"]
    away = partita["trasferta"]

    home_id = partita["home_id"]
    away_id = partita["away_id"]


    await update.message.reply_text(
        "🤖 Analisi AI in corso..."
    )


    # ==========================================================
    # STATISTICHE
    # ==========================================================

    statistiche_casa = ultime_partite(home_id)

    statistiche_ospite = ultime_partite(away_id)


    if not statistiche_casa or not statistiche_ospite:

        await update.message.reply_text(
            "❌ Dati statistici insufficienti per questa partita."
        )

        return


    # ==========================================================
    # INDICATORI AI
    # ==========================================================

    indicatori = calcola_indicatori(
        statistiche_casa,
        statistiche_ospite
    )


    # ==========================================================
    # AI SCORE
    # ==========================================================

    ai_score_base = calcola_ai_score(
        statistiche_casa,
        statistiche_ospite,
        indicatori,
        lega
    )


    # ==========================================================
    # COMPONENTI SCORE
    # ==========================================================

    componenti_score = analizza_componenti_score(
        statistiche_casa,
        statistiche_ospite,
        indicatori
    )


    testo_score = ""

    for nome, valore in componenti_score.items():

        simbolo = "+" if valore >= 0 else ""

        testo_score += (
            f"{nome}: {simbolo}{valore}\n"
        )


    # ==========================================================
    # PRONOSTICO BASE
    # ==========================================================

    pronostico_base = genera_pronostico(
        statistiche_casa,
        statistiche_ospite,
        indicatori,
        ai_score_base
    )


    # ==========================================================
    # MERCATI AI
    # ==========================================================

    mercati = calcola_mercati_ai(
        statistiche_casa,
        statistiche_ospite,
        indicatori
    )


    if not mercati:

        await update.message.reply_text(
            "❌ Nessun mercato disponibile per questa partita."
        )

        return


    # ==========================================================
    # DECISION ENGINE
    # ==========================================================

    scelta_ai = scegli_pronostico(
        mercati,
        ai_score_base,
        pronostico_base["rischio"],
        statistiche_casa,
        statistiche_ospite,
        indicatori,
        lega
    )


    if not scelta_ai:

        await update.message.reply_text(
            "❌ Il Decision Engine non ha trovato un pronostico."
        )

        return


    # ==========================================================
    # RISULTATO DECISION ENGINE
    # ==========================================================

    mercato_scelto = scelta_ai.get(
        "mercato",
        "Nessun pronostico"
    )

    probabilita = scelta_ai.get(
        "probabilita",
        0
    )

    value_index = scelta_ai.get(
        "value_index",
        0
    )

    classifica = scelta_ai.get(
        "classifica",
        []
    )


    # ==========================================================
    # RISCHIO
    # ==========================================================

    rischio = pronostico_base.get(
        "rischio",
        "N/D"
    )


    # ==========================================================
    # AI SCORE FINALE
    # ==========================================================

    ai_score = calcola_ai_score(
        statistiche_casa,
        statistiche_ospite,
        indicatori,
        lega,
        mercato_scelto
    )


    # ==========================================================
    # AFFIDABILITÀ
    # ==========================================================

    affidabilita = livello_affidabilita(
        ai_score
    )


    # ==========================================================
    # SPIEGAZIONE AI
    # ==========================================================

    spiegazione = genera_spiegazione(
        statistiche_casa,
        statistiche_ospite,
        mercato_scelto
    )


    # ==========================================================
    # MIGLIORI MERCATI
    # ==========================================================

    migliori = miglior_mercato(
        mercati
    )


    testo_mercati = ""


    if migliori:

        for posizione, elemento in enumerate(
            migliori,
            start=1
        ):

            try:

                mercato, valore = elemento

                testo_mercati += (
                    f"{posizione}️⃣ "
                    f"{mercato}: {valore}%\n"
                )

            except (ValueError, TypeError):

                testo_mercati += (
                    f"{posizione}️⃣ "
                    f"{elemento}\n"
                )

    else:

        testo_mercati = (
            "Nessun mercato disponibile.\n"
        )


    # ==========================================================
    # CLASSIFICA VALUE INDEX
    # ==========================================================

    testo_classifica = ""


    for posizione, elemento in enumerate(
        classifica,
        start=1
    ):

        try:

            mercato, score = elemento

            probabilita_mercato = mercati.get(
                mercato,
                0
            )

            testo_classifica += (
                f"{posizione}️⃣ {mercato}\n"
                f"💎 Value Index: {score}/100\n"
                f"📊 Probabilità: {probabilita_mercato}%\n\n"
            )

        except (ValueError, TypeError):

            testo_classifica += (
                f"{posizione}️⃣ {elemento}\n\n"
            )


    # ==========================================================
    # SALVATAGGIO STORICO
    # ==========================================================

    salva_pronostico(

        {
            "fixture": {
                "id": partita["id"],
                "date": partita["ora"]
            },

            "league": {
                "name": lega
            },

            "casa": home,

            "trasferta": away
        },

        {
            "pronostico": mercato_scelto,

            "fiducia": probabilita,

            "ai_score": ai_score,

            "rischio": rischio
        }
    )


    # ==========================================================
    # STATISTICHE
    # ==========================================================

    testo_statistiche = (

        f"🏠 {home}\n"
        f"📈 Forma: "
        f"{statistiche_casa.get('forma', 'N/D')}\n"
        f"⚽ Gol fatti: "
        f"{statistiche_casa.get('gol_fatti', 0)}\n"
        f"🥅 Gol subiti: "
        f"{statistiche_casa.get('gol_subiti', 0)}\n\n"

        f"✈️ {away}\n"
        f"📈 Forma: "
        f"{statistiche_ospite.get('forma', 'N/D')}\n"
        f"⚽ Gol fatti: "
        f"{statistiche_ospite.get('gol_fatti', 0)}\n"
        f"🥅 Gol subiti: "
        f"{statistiche_ospite.get('gol_subiti', 0)}"

    )


    # ==========================================================
    # MESSAGGIO FINALE
    # ==========================================================

    testo = (

        "🔥 CALCIOAI ANALISI AI\n\n"

        f"{bandiera} {lega}\n"
        f"🕒 {partita['ora']}\n\n"

        f"⚽ {home}\n"
        f"🆚 {away}\n\n"

        f"{testo_statistiche}\n\n"

        "🎯 PRONOSTICO AI\n"
        f"{mercato_scelto}\n"
        f"📊 Probabilità: {probabilita}%\n"
        f"🤖 AI Score: {ai_score}/100\n"
        f"💎 Value Index: {value_index}/100\n"
        f"⚠️ Rischio: {rischio}\n\n"

        "🧠 ANALISI SCORE AI\n"
        f"{testo_score}\n"

        "🧠 AFFIDABILITÀ AI\n"
        f"{affidabilita['barra']} "
        f"{affidabilita['percentuale']}%\n"
        f"{affidabilita['livello']}\n\n"

        "🧠 MOTIVAZIONE AI\n"
        f"{spiegazione}\n\n"

        "🏆 MERCATI CONSIGLIATI AI\n"
        f"{testo_classifica}\n"

        "📈 MERCATI AI\n"
        f"{testo_mercati}\n"

        "\n📊 INDICATORI AI\n"
        f"⚽ Over 1.5 Gol: "
        f"{indicatori.get('over15', 0)}%\n"
        f"⚽ Over 2.5 Gol: "
        f"{indicatori.get('over25', 0)}%\n"
        f"🤝 Gol/Gol: "
        f"{indicatori.get('golgol', 0)}%\n"
        f"🛡 Under 3.5 Gol: "
        f"{indicatori.get('under35', 0)}%\n\n"

        "🤖 Analisi generata da CalcioAI."
    )


    await update.message.reply_text(
        testo
    )