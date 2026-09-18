from telegram import Update
from telegram.ext import ContextTypes

import sqlite3


DATABASE = "database/calcioai.db"


ADMIN_ID = 505296696


async def storico(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != ADMIN_ID:

        await update.message.reply_text(
            "❌ Comando riservato al proprietario."
        )

        return


    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()


    cursor.execute("""
        SELECT
            id,
            casa,
            trasferta,
            pronostico,
            fiducia,
            ai_score,
            esito
        FROM storico
        ORDER BY id DESC
        LIMIT 10
    """)


    risultati = cursor.fetchall()


    conn.close()


    if not risultati:

        await update.message.reply_text(
            "📜 Nessun pronostico nello storico."
        )

        return


    testo = (
        "📜 *CALCIOAI STORICO*\n\n"
    )


    for riga in risultati:

        id_analisi = riga[0]
        casa = riga[1]
        trasferta = riga[2]
        pronostico = riga[3]
        fiducia = riga[4]
        score = riga[5]
        esito = riga[6]


        if esito is None:

            stato = "⏳ Da verificare"

        elif esito == "CORRETTO":

            stato = "✅ CORRETTO"

        else:

            stato = "❌ ERRATO"



        testo += (
            f"🆔 ID: {id_analisi}\n"
            f"⚽ {casa} - {trasferta}\n"
            f"🎯 {pronostico}\n"
            f"📊 Fiducia: {fiducia}%\n"
            f"🤖 Score: {score}\n"
            f"{stato}\n\n"
        )


    await update.message.reply_text(
        testo,
        parse_mode="Markdown"
    )