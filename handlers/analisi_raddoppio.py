from telegram import Update
from telegram.ext import ContextTypes

from services.partite_oggi import partite_oggi
from services.analisi_ai import analizza_partita


def calcola_raddoppio_score(
    ai_score,
    probabilita,
    value_index,
    rischio,
    indicatori=None,
    storico_totale=0,
    precisione_storica=0
):
    """
    Calcola il Raddoppio Score da 0 a 100.

    Il punteggio considera:

    - AI Score
    - Probabilità
    - Value Index
    - Indicatori del mercato
    - Storico del mercato
    - Rischio

    Lo storico viene utilizzato solo quando realmente disponibile.
    """

    ai_score = float(ai_score or 0)
    probabilita = float(probabilita or 0)
    value_index = float(value_index or 0)

    storico_totale = int(storico_totale or 0)
    precisione_storica = float(
        precisione_storica or 0
    )

    indicatori = indicatori or {}

    # ==========================================================
    # BASE
    # ==========================================================

    score = (
        ai_score * 0.30
        +
        probabilita * 0.25
        +
        value_index * 0.25
    )

    # ==========================================================
    # COERENZA AI SCORE / PROBABILITÀ / VALUE
    # ==========================================================

    media = (
        ai_score
        +
        probabilita
        +
        value_index
    ) / 3

    differenze = [
        abs(ai_score - probabilita),
        abs(ai_score - value_index),
        abs(probabilita - value_index)
    ]

    differenza_media = sum(differenze) / len(differenze)

    if differenza_media <= 5:

        score += 3

    elif differenza_media <= 10:

        score += 1

    elif differenza_media >= 20:

        score -= 4

    # ==========================================================
    # INDICATORI
    # ==========================================================

    valori_indicatori = []

    for chiave in (
        "over15",
        "over25",
        "golgol",
        "under35"
    ):

        valore = indicatori.get(
            chiave,
            0
        )

        try:

            valore = float(valore or 0)

        except (TypeError, ValueError):

            valore = 0

        if valore > 0:

            valori_indicatori.append(
                valore
            )

    if valori_indicatori:

        media_indicatori = (
            sum(valori_indicatori)
            /
            len(valori_indicatori)
        )

        # Gli indicatori rafforzano leggermente
        # il punteggio, ma non possono dominarlo.

        if media_indicatori >= 75:

            score += 4

        elif media_indicatori >= 65:

            score += 2

        elif media_indicatori < 45:

            score -= 2

    # ==========================================================
    # COERENZA INDICATORI
    # ==========================================================

    if valori_indicatori:

        massimo = max(
            valori_indicatori
        )

        minimo = min(
            valori_indicatori
        )

        differenza_indicatori = (
            massimo - minimo
        )

        if differenza_indicatori <= 15:

            score += 2

        elif differenza_indicatori >= 40:

            score -= 2

    # ==========================================================
    # STORICO MERCATO
    # ==========================================================

    if storico_totale >= 20:

        if precisione_storica >= 85:

            score += 6

        elif precisione_storica >= 80:

            score += 5

        elif precisione_storica >= 75:

            score += 3

        elif precisione_storica >= 70:

            score += 1

        elif precisione_storica <= 50:

            score -= 6

        elif precisione_storica <= 60:

            score -= 3

    elif storico_totale >= 10:

        if precisione_storica >= 85:

            score += 4

        elif precisione_storica >= 80:

            score += 3

        elif precisione_storica >= 75:

            score += 2

        elif precisione_storica >= 70:

            score += 1

        elif precisione_storica <= 50:

            score -= 4

    elif storico_totale >= 5:

        if precisione_storica >= 80:

            score += 2

        elif precisione_storica <= 50:

            score -= 2

    # ==========================================================
    # RISCHIO
    # ==========================================================

    rischio_testo = str(
        rischio
    ).lower()

    if "basso" in rischio_testo:

        score += 5

    elif "medio" in rischio_testo:

        score += 2

    elif "alto" in rischio_testo:

        score -= 10

    # ==========================================================
    # NORMALIZZAZIONE
    # ==========================================================

    score = max(
        0,
        min(score, 100)
    )

    return round(
        score,
        2
    )


async def analisi_raddoppio(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    try:

        partite = partite_oggi()

        if not partite:

            await update.message.reply_text(
                "⏳ Nessuna partita disponibile oggi."
            )

            return

        await update.message.reply_text(
            "🤖 CALCIOAI RADDOPPIO\n\n"
            "⏳ Sto analizzando le partite di oggi...\n"
            "📊 Statistiche + AI Score + Mercati + "
            "Value Index + Indicatori + Storico"
        )

        risultati = []

        for partita in partite:

            try:

                dati_partita = {

                    "fixture": {
                        "id": partita["id"],
                        "date": partita["ora"]
                    },

                    "league": {
                        "name": partita["lega"],
                        "country": partita.get(
                            "paese",
                            ""
                        )
                    },

                    "teams": {

                        "home": {
                            "id": partita["home_id"],
                            "name": partita["casa"]
                        },

                        "away": {
                            "id": partita["away_id"],
                            "name": partita["trasferta"]
                        }

                    }

                }

                analisi = analizza_partita(
                    dati_partita
                )

                if not analisi:

                    continue

                pronostico = analisi.get(
                    "pronostico",
                    "Dati insufficienti"
                )

                probabilita = analisi.get(
                    "fiducia",
                    0
                )

                ai_score = analisi.get(
                    "ai_score",
                    0
                )

                rischio = analisi.get(
                    "rischio",
                    "N/D"
                )

                indicatori = analisi.get(
                    "indicatori",
                    {}
                )

                scelta_ai = analisi.get(
                    "scelta_ai",
                    {}
                )

                value_index = scelta_ai.get(
                    "value_index",
                    0
                )

                storico_totale = scelta_ai.get(
                    "storico_totale",
                    0
                )

                precisione_storica = scelta_ai.get(
                    "precisione_storica",
                    0
                )

                if pronostico in (
                    "Dati insufficienti",
                    "Nessun pronostico"
                ):

                    continue

                # ==================================================
                # FILTRO RADDOPPIO
                # ==================================================

                if ai_score < 75:

                    continue

                if probabilita < 80:

                    continue

                if value_index < 75:

                    continue

                if "Alto" in str(rischio):

                    continue

                # ==================================================
                # RADDOPPIO SCORE
                # ==================================================

                raddoppio_score = calcola_raddoppio_score(

                    ai_score=ai_score,

                    probabilita=probabilita,

                    value_index=value_index,

                    rischio=rischio,

                    indicatori=indicatori,

                    storico_totale=storico_totale,

                    precisione_storica=precisione_storica

                )

                risultati.append({

                    "partita": partita,

                    "pronostico": pronostico,

                    "probabilita": probabilita,

                    "ai_score": ai_score,

                    "value_index": value_index,

                    "rischio": rischio,

                    "indicatori": indicatori,

                    "storico_totale": storico_totale,

                    "precisione_storica": precisione_storica,

                    "raddoppio_score": raddoppio_score

                })

            except Exception as e:

                print(
                    "⚠️ ERRORE ANALISI RADDOPPIO:",
                    partita.get(
                        "casa",
                        "Casa"
                    ),
                    "-",
                    partita.get(
                        "trasferta",
                        "Trasferta"
                    ),
                    "|",
                    e
                )

                continue

        # ==========================================================
        # NESSUNA PARTITA
        # ==========================================================

        if not risultati:

            await update.message.reply_text(

                "❌ Nessuna partita supera il filtro "
                "Raddoppio AI.\n\n"

                "🎯 FILTRO ATTIVO\n"
                "🤖 AI Score ≥ 75\n"
                "📊 Probabilità ≥ 80%\n"
                "💎 Value Index ≥ 75\n"
                "🟢🔵 Rischio Alto escluso"

            )

            return

        # ==========================================================
        # CLASSIFICA
        # ==========================================================

        risultati.sort(

            key=lambda x: (

                x["raddoppio_score"],

                x["value_index"],

                x["ai_score"],

                x["probabilita"],

                x["precisione_storica"]

            ),

            reverse=True

        )

        # ==========================================================
        # MASSIMO 2 PARTITE
        # ==========================================================

        risultati = risultati[:2]

        # ==========================================================
        # MESSAGGIO
        # ==========================================================

        messaggio = (

            "🔥 CALCIOAI - RADDOPPIO AI\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"

            "🎯 PARTITE SELEZIONATE\n\n"

        )

        for posizione, risultato in enumerate(
            risultati,
            start=1
        ):

            partita = risultato["partita"]

            messaggio += (

                f"{posizione}️⃣ "
                f"{partita['casa']} - "
                f"{partita['trasferta']}\n"

                f"🏆 {partita['lega']}\n"
                f"🕐 {partita['ora']}\n\n"

                f"🎯 {risultato['pronostico']}\n"

                f"📊 Probabilità: "
                f"{risultato['probabilita']}%\n"

                f"🤖 AI Score: "
                f"{risultato['ai_score']}/100\n"

                f"💎 Value Index: "
                f"{risultato['value_index']}/100\n"

                f"🔥 Raddoppio Score: "
                f"{risultato['raddoppio_score']}/100\n"

                f"⚠️ Rischio: "
                f"{risultato['rischio']}\n\n"

                "━━━━━━━━━━━━━━━━━━━━\n\n"

            )

        messaggio += (

            "💰 STRATEGIA RADDOPPIO\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"

            "1️⃣ Partita → €1\n"
            "2️⃣ Se ERRATA → €2\n"
            "3️⃣ Se ERRATA → €4\n"
            "4️⃣ Se ERRATA → €8\n"
            "5️⃣ Se ERRATA → €16\n"
            "6️⃣ Se ERRATA → €32\n\n"

            "🎯 FILTRO AI ATTIVO\n"

            "🤖 AI Score ≥ 75\n"
            "📊 Probabilità ≥ 80%\n"
            "💎 Value Index ≥ 75\n"
            "🟢🔵 Rischio Alto escluso\n\n"

            "🔥 Raddoppio Score definitivo:\n"
            "AI Score + Probabilità + Value Index + "
            "Indicatori + Storico + Rischio.\n\n"

            "⚠️ Simulazione statistica: "
            "non garantisce risultati."

        )

        await update.message.reply_text(
            messaggio
        )

    except Exception as e:

        print(
            "❌ ERRORE GENERALE RADDOPPIO AI:",
            e
        )

        await update.message.reply_text(
            f"❌ Errore Raddoppio AI:\n{e}"
        )