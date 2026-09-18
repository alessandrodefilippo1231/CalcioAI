from telegram import Update
from telegram.ext import ContextTypes

from services.storico_ai import statistiche_mercati


async def mercati(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    dati = statistiche_mercati()


    if not dati:

        await update.message.reply_text(
            "📊 Nessun dato mercato disponibile.\n\n"
            "L'AI deve prima raccogliere pronostici."
        )

        return



    classifica = []


    for mercato, valori in dati.items():

        totale = valori.get("totale", 0)
        corrette = valori.get("corrette", 0)

        if totale > 0:

            precisione = round(
                corrette / totale * 100
            )

        else:

            precisione = 0


        classifica.append(
            (
                mercato,
                totale,
                corrette,
                precisione
            )
        )



    classifica.sort(
        key=lambda x: x[3],
        reverse=True
    )



    testo = (
        "🏆 *CALCIOAI PERFORMANCE MERCATI* ⚽🤖\n\n"
    )


    posizione = 1


    for mercato, totale, corrette, precisione in classifica:


        testo += (
            f"{posizione}️⃣ {mercato}\n"
            f"📊 Analisi: {totale}\n"
            f"✅ Corrette: {corrette}\n"
            f"🎯 Precisione: {precisione}%\n\n"
        )


        posizione += 1



    await update.message.reply_text(
        testo,
        parse_mode="Markdown"
    )