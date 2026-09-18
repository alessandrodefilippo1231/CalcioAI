from telegram import Update
from telegram.ext import ContextTypes


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    testo = """

🔥 *CALCIOAI COMANDI* ⚽🤖


⚽ /partite

📅 Lista delle partite di oggi
con orari e campionati.


🔥 /top

⭐ TOP 5 MATCH AI

Le partite selezionate dal
motore di intelligenza artificiale.


🎟 /schedina

🎯 Schedina AI

Le migliori 3 opportunità
secondo l'algoritmo.


📊 /analisi

Analisi completa della partita:

• Forma squadre
• Gol fatti/subiti
• Indicatori AI
• Mercati migliori
• Rischio


ℹ️ /info

Informazioni sul progetto
CALCIOAI.


🤖 *Motore CALCIOAI*

✔ AI Score
✔ Analisi statistiche
✔ Forma recente
✔ Mercati Over/Under
✔ Gol/Gol
✔ Gestione rischio


⚠️ Le analisi sono statistiche
e non garantiscono risultati.

"""


    await update.message.reply_text(
        testo,
        parse_mode="Markdown"
    )