from telegram import Update
from telegram.ext import ContextTypes


async def versione(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    testo = """
🚀 *CALCIOAI ENGINE* ⚽🤖


📌 Versione:
CALCIOAI v1.0.0


🔥 MODULI ATTIVI:


✅ Match Engine

✅ AI Score

✅ Decision Engine

✅ Mercati AI

✅ Gestione rischio

✅ Storico pronostici

✅ Analisi statistiche


🧠 Sistema:
Statistiche + Indicatori + Valutazione AI


🛠 Stato:
Sistema operativo


⚠️ Le analisi sono basate
su dati statistici e non
garantiscono risultati.
"""


    await update.message.reply_text(
        testo,
        parse_mode="Markdown"
    )