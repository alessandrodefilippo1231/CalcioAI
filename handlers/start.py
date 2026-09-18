from telegram import Update
from telegram.ext import ContextTypes


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    testo = """

🔥 *BENVENUTO SU CALCIOAI* ⚽🤖


Il tuo assistente intelligente
per l'analisi delle partite di calcio.


🧠 COSA PUOI FARE:

⚽ /partite
Lista partite del giorno


🔥 /top
TOP MATCH selezionati dall'AI


🎟 /schedina
Le migliori opportunità AI


📊 /analisi
Analisi completa delle partite


ℹ️ /info
Scopri CALCIOAI


🚀 CALCIOAI ENGINE

✔ Forma squadre
✔ Statistiche gol
✔ AI Score
✔ Mercati calcio
✔ Gestione rischio


Scrivi /help per vedere
tutti i comandi disponibili.


⚠️ Analisi basate su dati statistici.
Nessuna garanzia di risultato.
"""

    await update.message.reply_text(
        testo,
        parse_mode="Markdown"
    )