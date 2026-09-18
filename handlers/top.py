from telegram import Update
from telegram.ext import ContextTypes

from datetime import datetime
from zoneinfo import ZoneInfo

from services.match_engine import trova_top_match



async def top(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    classifica = trova_top_match()


    if not classifica:

        await update.message.reply_text(
            "🔥 Nessun TOP MATCH disponibile oggi."
        )

        return



    testo = (
        "🔥 *CALCIOAI TOP MATCH AI* 🔥\n\n"
        "Le migliori partite selezionate "
        "dal motore AI.\n\n"
    )



    for posizione, elemento in enumerate(
        classifica[:5],
        start=1
    ):

        partita = elemento["partita"]

        analisi = elemento["analisi"]


        casa = partita["teams"]["home"]["name"]

        trasferta = partita["teams"]["away"]["name"]



        data_utc = partita["fixture"]["date"]


        ora = datetime.fromisoformat(
            data_utc.replace(
                "Z",
                "+00:00"
            )
        ).astimezone(
            ZoneInfo("Europe/Rome")
        ).strftime("%H:%M")



        rischio = analisi.get(
            "rischio",
            "N/D"
        )


        if rischio == "🟢 Basso":
            emoji_rischio = "🟢"

        elif rischio == "🟡 Medio":
            emoji_rischio = "🟡"

        else:
            emoji_rischio = "🔴"



        testo += (
            f"🏅 *TOP {posizione}*\n\n"
            f"⚽ {casa} - {trasferta}\n"
            f"🏆 {partita['league']['name']}\n"
            f"🕒 {ora}\n\n"

            f"🎯 Pronostico:\n"
            f"{analisi['pronostico']}\n\n"

            f"🤖 AI Score: "
            f"{analisi['ai_score']}/100\n"

            f"🧠 Decision Score: "
            f"{analisi.get('scelta_ai', {}).get('score_finale', 0)}/100\n"

            f"📊 Fiducia: "
            f"{analisi['fiducia']}%\n"

            f"⚠️ Rischio: "
            f"{emoji_rischio} {rischio}\n\n"

            "━━━━━━━━━━━━━━\n\n"
        )



    await update.message.reply_text(
        testo,
        parse_mode="Markdown"
    )