from telegram import Update
from telegram.ext import ContextTypes

from services.storico_ai import statistiche_storico


async def statistiche(update: Update, context: ContextTypes.DEFAULT_TYPE):

    dati = statistiche_storico()

    await update.message.reply_text(

        "🔥 CALCIOAI PERFORMANCE\n\n"

        f"📊 Analisi salvate: {dati['totale']}\n\n"

        f"⏳ In attesa: {dati['attesa']}\n"

        f"✅ Corrette: {dati['corrette']}\n"

        f"❌ Errate: {dati['errate']}\n\n"

        f"🎯 Precisione AI: {dati['precisione']}%\n\n"

        f"🤖 AI Score medio: {dati['media_score']}/100\n\n"

        "🧠 Storico AI attivo ✅"

    )