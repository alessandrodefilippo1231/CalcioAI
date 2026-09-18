from telegram import Update
from telegram.ext import ContextTypes

from services.storico_ai import (
    statistiche_storico,
    media_fiducia,
    ultimo_pronostico
)

# Inserisci qui il tuo ID Telegram
ADMIN_ID = 505296696


async def admin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    if user_id != ADMIN_ID:

        await update.message.reply_text(
            "❌ Comando riservato al proprietario."
        )

        return

    stats = statistiche_storico()

    fiducia = media_fiducia()

    ultimo = ultimo_pronostico()

    testo = (
        "👑 *CALCIOAI ADMIN* ⚽🤖\n\n"

        "🤖 Stato bot:\n"
        "🟢 Online\n\n"

        f"📊 Analisi salvate: {stats['totale']}\n"
        f"⏳ In attesa: {stats['attesa']}\n"
        f"✅ Corrette: {stats['corrette']}\n"
        f"❌ Errate: {stats['errate']}\n"
        f"📈 Precisione: {stats['precisione']}%\n"
        f"🤖 AI Score medio: {stats['media_score']}\n"
        f"🎯 Fiducia media: {fiducia}%\n\n"
    )

    if ultimo:

        testo += (
            "📝 *Ultimo pronostico*\n\n"
            f"{ultimo['casa']} - {ultimo['trasferta']}\n"
            f"🎯 {ultimo['pronostico']}\n"
            f"📊 Fiducia: {ultimo['fiducia']}%\n\n"
        )

    testo += (
        "🌐 API Football:\n"
        "In attesa dati\n\n"

        "🚀 Versione:\n"
        "CALCIOAI v1.0.0"
    )

    await update.message.reply_text(
        testo,
        parse_mode="Markdown"
    )