from telegram import Update
from telegram.ext import ContextTypes

from services.verifica_risultati import verifica_tutte



async def aggiorna(update: Update, context: ContextTypes.DEFAULT_TYPE):


    risultati = verifica_tutte()


    if not risultati:

        await update.message.reply_text(
            "⏳ Nessun risultato disponibile da verificare."
        )

        return



    testo = "🔥 CALCIOAI VERIFICA RISULTATI\n\n"


    for partita in risultati:

        testo += (
            f"⚽ {partita['partita']}\n"
            f"🎯 Pronostico: {partita['pronostico']}\n"
            f"📌 Risultato: {partita['risultato']}\n"
            f"📊 Esito: {partita['esito']}\n\n"
        )



    await update.message.reply_text(
        testo
    )