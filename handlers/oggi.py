from telegram import Update
from telegram.ext import ContextTypes

from services.partite_oggi import partite_oggi


async def oggi(update: Update, context: ContextTypes.DEFAULT_TYPE):

    partite = partite_oggi()


    if not partite:

        await update.message.reply_text(
            "⚽ Nessuna partita disponibile oggi."
        )

        return



    testo = (
        "🔥 CALCIOAI PARTITE DI OGGI\n\n"
        "📊 Selezione automatica AI\n"
        "━━━━━━━━━━━━━━\n\n"
    )


    for numero, partita in enumerate(
        partite[:20],
        start=1
    ):


        testo += (

            f"{numero}️⃣ {partita['casa']} 🆚 "
            f"{partita['trasferta']}\n\n"

            f"🏆 {partita['lega']}\n"

            f"🕒 Ore {partita['ora']}\n\n"

            f"🤖 Analizza con AI:\n"
            f"/analizza {numero}\n"

            "━━━━━━━━━━━━━━\n\n"

        )


    await update.message.reply_text(
        testo
    )