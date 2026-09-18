from telegram import Update
from telegram.ext import ContextTypes


async def status(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    testo = """
🤖 *CALCIOAI STATUS* ⚽

🟢 Bot:
Online

🧠 Motore AI:
Attivo

📊 Analisi statistiche:
Pronta

📈 AI Score:
Attivo

🎯 Mercati AI:
Attivi

💾 Storico pronostici:
Attivo

🌐 API Football:
In attesa dati

🚀 Versione:
CALCIOAI v1.0

⚠️ Le analisi sono statistiche
e non garantiscono risultati.
"""


    await update.message.reply_text(
        testo,
        parse_mode="Markdown"
    )