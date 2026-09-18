from telegram import Update
from telegram.ext import ContextTypes

from services.partite_oggi import partite_oggi
from services.match_engine import trova_schedina


async def schedina(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    print("")
    print("🎯 AVVIO COMANDO /SCHEDINA")

    # ==========================================================
    # RECUPERO PARTITE
    # ==========================================================

    try:

        partite = await partite_oggi()

    except TypeError:

        try:
            partite = partite_oggi()
        except Exception as e:

            print(
                f"❌ ERRORE RECUPERO PARTITE: {e}"
            )

            await update.message.reply_text(
                "❌ Errore durante il recupero delle partite."
            )

            return

    except Exception as e:

        print(
            f"❌ ERRORE RECUPERO PARTITE: {e}"
        )

        await update.message.reply_text(
            "❌ Errore durante il recupero delle partite."
        )

        return

    # ==========================================================
    # CONTROLLO PARTITE
    # ==========================================================

    if not partite:

        print(
            "⚠️ NESSUNA PARTITA DISPONIBILE"
        )

        await update.message.reply_text(
            "🔥 Nessuna partita disponibile per la schedina AI."
        )

        return

    print(
        f"📦 PARTITE DISPONIBILI: {len(partite)}"
    )

    # ==========================================================
    # GENERAZIONE SCHEDINA
    # ==========================================================

    try:

        classifica = trova_schedina(
            partite
        )

    except Exception as e:

        print(
            f"❌ ERRORE MATCH ENGINE: {e}"
        )

        await update.message.reply_text(
            "❌ Errore durante la generazione della schedina AI."
        )

        return

    # ==========================================================
    # NESSUNA SCHEDINA
    # ==========================================================

    if not classifica:

        print(
            "⚠️ NESSUNA PARTITA VALIDA PER LA SCHEDINA"
        )

        await update.message.reply_text(
            "🔥 Nessuna partita abbastanza affidabile "
            "per la schedina AI."
        )

        return

    # ==========================================================
    # INTESTAZIONE
    # ==========================================================

    testo = (
        "🔥 *CALCIOAI SCHEDINA AI*\n\n"
    )

    # ==========================================================
    # TOTALI
    # ==========================================================

    totale_fiducia = 0
    totale_score = 0
    totale_decision = 0

    numero_partite = 0

    # ==========================================================
    # MASSIMO 3 PARTITE
    # ==========================================================

    for posizione, elemento in enumerate(
        classifica[:3],
        start=1
    ):

        partita = elemento.get(
            "partita",
            {}
        )

        analisi = elemento.get(
            "analisi",
            {}
        )

        # ======================================================
        # NOMI SQUADRE
        # ======================================================

        try:

            casa = partita["teams"]["home"]["name"]

            trasferta = partita["teams"]["away"]["name"]

        except Exception:

            casa = partita.get(
                "casa",
                "Casa"
            )

            trasferta = partita.get(
                "trasferta",
                "Trasferta"
            )

        # ======================================================
        # DATI ANALISI
        # ======================================================

        pronostico = analisi.get(
            "pronostico",
            elemento.get(
                "pronostico",
                "Nessun pronostico"
            )
        )

        fiducia = analisi.get(
            "fiducia",
            elemento.get(
                "fiducia",
                0
            )
        )

        ai_score = analisi.get(
            "ai_score",
            elemento.get(
                "ai_score",
                0
            )
        )

        scelta_ai = analisi.get(
            "scelta_ai",
            {}
        )

        if not isinstance(
            scelta_ai,
            dict
        ):

            scelta_ai = {}

        decision_score = scelta_ai.get(
            "score_finale",
            0
        )

        rischio = analisi.get(
            "rischio",
            elemento.get(
                "rischio",
                "N/D"
            )
        )

        # ======================================================
        # CONTROLLO PRONOSTICO
        # ======================================================

        if (
            not pronostico
            or pronostico == "Nessun pronostico"
            or pronostico == "Dati insufficienti"
        ):

            print(
                f"⚠️ PRONOSTICO NON VALIDO: "
                f"{casa} - {trasferta}"
            )

            continue

        # ======================================================
        # TESTO PARTITA
        # ======================================================

        testo += (
            f"{posizione}️⃣ "
            f"{casa} - {trasferta}\n"

            f"🎯 {pronostico}\n"

            f"📊 Fiducia: "
            f"{fiducia}%\n"

            f"🤖 AI Score: "
            f"{ai_score}/100\n"

            f"🧠 Decision Score: "
            f"{decision_score}/100\n"

            f"⚠️ Rischio: "
            f"{rischio}\n\n"
        )

        # ======================================================
        # TOTALI
        # ======================================================

        totale_fiducia += fiducia

        totale_score += ai_score

        totale_decision += decision_score

        numero_partite += 1

    # ==========================================================
    # CONTROLLO PARTITE VALIDE
    # ==========================================================

    if numero_partite == 0:

        await update.message.reply_text(
            "🔥 Nessuna partita valida per la schedina AI."
        )

        return

    # ==========================================================
    # MEDIE
    # ==========================================================

    fiducia_media = round(
        totale_fiducia / numero_partite
    )

    score_medio = round(
        totale_score / numero_partite
    )

    decision_medio = round(
        totale_decision / numero_partite
    )

    # ==========================================================
    # RIEPILOGO
    # ==========================================================

    testo += (
        "━━━━━━━━━━━━━━\n"

        f"⭐ Fiducia media: "
        f"{fiducia_media}%\n"

        f"🤖 AI Score medio: "
        f"{score_medio}/100\n"

        f"🧠 Decision Score medio: "
        f"{decision_medio}/100\n\n"

        "📚 Pronostici salvati nello storico.\n\n"

        "⚠️ Analisi generata da CalcioAI."
    )

    # ==========================================================
    # INVIO TELEGRAM
    # ==========================================================

    await update.message.reply_text(
        testo,
        parse_mode="Markdown"
    )