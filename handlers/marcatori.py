from telegram import Update
from telegram.ext import ContextTypes

from services.partite_oggi import partite_oggi
from services.marcatori import analizza_marcatori_partite


# ============================================================
# /MARCATORI
# ============================================================

async def marcatori(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Mostra i probabili marcatori delle partite di Serie A
    in programma oggi.
    """

    try:
        await update.message.reply_text(
            "⚽ <b>CALCIOAI — PROBABILI MARCATORI</b>\n\n"
            "🔎 Cerco le partite di Serie A di oggi...",
            parse_mode="HTML"
        )

        # ====================================================
        # RECUPERO PARTITE
        # ====================================================

        partite = await __import__(
            "asyncio"
        ).to_thread(partite_oggi)

        if not partite:
            await update.message.reply_text(
                "⚠️ Non ci sono partite disponibili oggi."
            )
            return

        # ====================================================
        # SOLO SERIE A
        # ====================================================

        partite_serie_a = []

        for partita in partite:

            lega = str(
                partita.get("lega", "")
            ).lower()

            paese = str(
                partita.get("paese", "")
            ).lower()

            if (
                "serie a" in lega
                and (
                    "ital" in paese
                    or paese == ""
                )
            ):
                partite_serie_a.append(partita)

        if not partite_serie_a:
            await update.message.reply_text(
                "🇮🇹 <b>SERIE A</b>\n\n"
                "⚠️ Nessuna partita di Serie A "
                "in programma oggi.",
                parse_mode="HTML"
            )
            return

        # ====================================================
        # ANALISI MARCATORI
        # ====================================================

        risultati = await __import__(
            "asyncio"
        ).to_thread(
            analizza_marcatori_partite,
            partite_serie_a
        )

        if not risultati:
            await update.message.reply_text(
                "⚠️ Non sono riuscito a calcolare "
                "i probabili marcatori."
            )
            return

        # ====================================================
        # INTESTAZIONE
        # ====================================================

        await update.message.reply_text(
            "🇮🇹 <b>SERIE A — PROBABILI MARCATORI</b>\n\n"
            "📊 Analisi basata sui dati disponibili "
            "dei giocatori.\n"
            "🎯 Probabilità = stima AI preliminare.\n",
            parse_mode="HTML"
        )

        # ====================================================
        # FORMATTAZIONE PARTITE
        # ====================================================

        for risultato in risultati:

            casa = risultato.get(
                "casa",
                "Casa"
            )

            trasferta = risultato.get(
                "trasferta",
                "Trasferta"
            )

            marcatori_casa = risultato.get(
                "marcatori_casa",
                []
            )

            marcatori_trasferta = risultato.get(
                "marcatori_trasferta",
                []
            )

            partita = risultato.get(
                "partita",
                {}
            )

            ora = partita.get(
                "ora",
                ""
            )

            testo = (
                f"⚽ <b>{casa} — {trasferta}</b>\n"
            )

            if ora:
                testo += f"🕐 {ora}\n"

            testo += "\n"

            # =================================================
            # CASA
            # =================================================

            testo += f"🏠 <b>{casa}</b>\n"

            if marcatori_casa:

                for indice, giocatore in enumerate(
                    marcatori_casa,
                    start=1
                ):

                    nome = giocatore.get(
                        "nome",
                        "Sconosciuto"
                    )

                    probabilita = giocatore.get(
                        "probabilita",
                        0
                    )

                    gol = giocatore.get(
                        "gol",
                        0
                    )

                    tiri = giocatore.get(
                        "tiri",
                        0
                    )

                    rigori = giocatore.get(
                        "rigori",
                        0
                    )

                    icona = {
                        1: "🥇",
                        2: "🥈",
                        3: "🥉"
                    }.get(
                        indice,
                        "⚽"
                    )

                    testo += (
                        f"{icona} <b>{nome}</b> "
                        f"→ <b>{probabilita}%</b>\n"
                        f"   ⚽ Gol: {gol} | "
                        f"🎯 Tiri: {tiri}"
                    )

                    if rigori > 0:
                        testo += (
                            f" | 🎯 Rigori: {rigori}"
                        )

                    testo += "\n"

            else:
                testo += (
                    "⚠️ Nessun candidato disponibile.\n"
                )

            testo += "\n"

            # =================================================
            # TRASFERTA
            # =================================================

            testo += f"✈️ <b>{trasferta}</b>\n"

            if marcatori_trasferta:

                for indice, giocatore in enumerate(
                    marcatori_trasferta,
                    start=1
                ):

                    nome = giocatore.get(
                        "nome",
                        "Sconosciuto"
                    )

                    probabilita = giocatore.get(
                        "probabilita",
                        0
                    )

                    gol = giocatore.get(
                        "gol",
                        0
                    )

                    tiri = giocatore.get(
                        "tiri",
                        0
                    )

                    rigori = giocatore.get(
                        "rigori",
                        0
                    )

                    icona = {
                        1: "🥇",
                        2: "🥈",
                        3: "🥉"
                    }.get(
                        indice,
                        "⚽"
                    )

                    testo += (
                        f"{icona} <b>{nome}</b> "
                        f"→ <b>{probabilita}%</b>\n"
                        f"   ⚽ Gol: {gol} | "
                        f"🎯 Tiri: {tiri}"
                    )

                    if rigori > 0:
                        testo += (
                            f" | 🎯 Rigori: {rigori}"
                        )

                    testo += "\n"

            else:
                testo += (
                    "⚠️ Nessun candidato disponibile.\n"
                )

            testo += (
                "\n━━━━━━━━━━━━━━━━━━\n"
            )

            await update.message.reply_text(
                testo,
                parse_mode="HTML"
            )

    except Exception as e:

        print(
            "❌ ERRORE COMANDO /MARCATORI:",
            e
        )

        try:
            await update.message.reply_text(
                "❌ Si è verificato un errore "
                "durante l'analisi dei marcatori."
            )

        except Exception:
            pass