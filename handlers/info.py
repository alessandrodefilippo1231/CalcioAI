from telegram import Update
from telegram.ext import ContextTypes


async def info_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    testo = """

🔥 *CALCIOAI* ⚽🤖


Il tuo assistente AI per
l'analisi delle partite di calcio.


🧠 COSA ANALIZZA:

✔ Forma recente squadre

✔ Gol fatti e subiti

✔ Statistiche offensive e difensive

✔ Mercati Over/Under

✔ Gol/Gol

✔ AI Score

✔ Gestione del rischio


🔥 FUNZIONI DISPONIBILI:

⚽ Partite del giorno

⭐ Top Match AI

🎟 Schedina AI

📊 Analisi completa


🚀 CALCIOAI ENGINE

Un sistema che combina
statistiche, indicatori e
valutazioni automatiche.


⚠️ Le analisi sono basate
su dati statistici e non
rappresentano una garanzia
di risultato.

"""


    await update.message.reply_text(
        testo,
        parse_mode="Markdown"
    )