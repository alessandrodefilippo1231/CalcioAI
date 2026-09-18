from telegram import Update
from telegram.ext import ContextTypes

from services.partite_oggi import partite_oggi


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
    "Colombia": "🇨🇴",
    "Ecuador": "🇪🇨",
    "Switzerland": "🇨🇭",
    "Austria": "🇦🇹",
    "Denmark": "🇩🇰",
    "Sweden": "🇸🇪",
    "Norway": "🇳🇴",
    "Greece": "🇬🇷",

}


async def partite(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

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


    for indice, partita in enumerate(
        partite,
        start=1
    ):


        paese = partita.get(
            "paese",
            ""
        )


        bandiera = BANDIERE.get(
            paese,
            "🌍"
        )


        testo += (

            f"{indice}️⃣ {bandiera} "
            f"{partita['casa']} 🆚 "
            f"{partita['trasferta']}\n\n"

            f"🏆 {partita['lega']}\n"

            f"🕒 Ore {partita['ora']}\n"

            f"🤖 Analizza con AI:\n"
            f"/analizza {indice}\n"

            "━━━━━━━━━━━━━━\n\n"

        )


    await update.message.reply_text(
        testo
    )