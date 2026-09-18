from telegram import Update
from telegram.ext import ContextTypes

from services.apprendimento_ai import statistiche_mercati


async def ranking(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):


    mercati = statistiche_mercati()


    if not mercati:

        await update.message.reply_text(
            "⏳ Nessun dato sufficiente per creare il ranking AI."
        )

        return



    classifica = sorted(
        mercati.items(),
        key=lambda x: x[1]["precisione"],
        reverse=True
    )



    testo = (

        "🏆 CALCIOAI MARKET RANKING ⚽🤖\n\n"

    )



    posizione = 1



    for mercato, valori in classifica:


        if valori["totale"] < 5:

            affidabilita = "🔴 Bassa"


        elif valori["totale"] < 20:

            affidabilita = "🟡 Media"


        else:

            affidabilita = "🟢 Alta"



        testo += (

            f"{posizione}️⃣ {mercato}\n"

            f"🎯 Precisione: {valori['precisione']}%\n"

            f"📊 Analisi: {valori['totale']}\n"

            f"📈 Affidabilità: {affidabilita}\n\n"

        )


        posizione += 1



    await update.message.reply_text(
        testo
    )