import os
import asyncio

from dotenv import load_dotenv

from telegram.ext import (
    Application,
    CommandHandler
)

from handlers.analisi import analisi
from handlers.help import help_command
from handlers.partite import partite
from handlers.schedina import schedina
from handlers.top import top
from handlers.statistiche import statistiche
from handlers.aggiorna import aggiorna
from handlers.apprendimento import apprendimento
from handlers.oggi import oggi
from handlers.analizza import analizza
from handlers.info import info_command
from handlers.start import start
from handlers.status import status
from handlers.versione import versione
from handlers.id import id_command
from handlers.admin import admin
from handlers.mercati import mercati
from handlers.verifica import verifica
from handlers.storico import storico
from handlers.ranking import ranking
from handlers.analisi_raddoppio import analisi_raddoppio
from handlers.risultati import risultati
from handlers.marcatori import marcatori

from services.storico_ai import crea_database
from services.verifica_automatica import verifica_pronostici

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")


# ============================================================
# VERIFICA AUTOMATICA STORICO
# ============================================================

async def verifica_automatica_job(context):
    print("")
    print("⏰ CONTROLLO AUTOMATICO STORICO")

    try:
        risultati_verifica = await asyncio.to_thread(
            verifica_pronostici
        )

        if risultati_verifica:
            print("✅ CONTROLLO AUTOMATICO COMPLETATO")
        else:
            print("📚 NESSUN AGGIORNAMENTO STORICO")

    except Exception as e:
        print(
            "❌ ERRORE CONTROLLO AUTOMATICO:",
            e
        )


# ============================================================
# AVVIO BOT
# ============================================================

def main():

    # --------------------------------------------------------
    # DATABASE
    # --------------------------------------------------------

    crea_database()

    # --------------------------------------------------------
    # APPLICATION
    # --------------------------------------------------------

    app = Application.builder().token(
        BOT_TOKEN
    ).build()

    # --------------------------------------------------------
    # COMANDI
    # --------------------------------------------------------

    app.add_handler(
        CommandHandler("analisi", analisi)
    )

    app.add_handler(
        CommandHandler("help", help_command)
    )

    app.add_handler(
        CommandHandler("partite", partite)
    )

    app.add_handler(
        CommandHandler("oggi", oggi)
    )

    app.add_handler(
        CommandHandler("schedina", schedina)
    )

    app.add_handler(
        CommandHandler("top", top)
    )

    app.add_handler(
        CommandHandler("statistiche", statistiche)
    )

    app.add_handler(
        CommandHandler("aggiorna", aggiorna)
    )

    app.add_handler(
        CommandHandler("apprendimento", apprendimento)
    )

    app.add_handler(
        CommandHandler("analizza", analizza)
    )

    app.add_handler(
        CommandHandler("info", info_command)
    )

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("status", status)
    )

    app.add_handler(
        CommandHandler("versione", versione)
    )

    app.add_handler(
        CommandHandler("id", id_command)
    )

    app.add_handler(
        CommandHandler("admin", admin)
    )

    app.add_handler(
        CommandHandler("mercati", mercati)
    )

    app.add_handler(
        CommandHandler("verifica", verifica)
    )

    app.add_handler(
        CommandHandler("storico", storico)
    )

    app.add_handler(
        CommandHandler("ranking", ranking)
    )

    app.add_handler(
        CommandHandler(
            "raddoppio",
            analisi_raddoppio
        )
    )

    app.add_handler(
        CommandHandler(
            "risultati",
            risultati
        )
    )

    # --------------------------------------------------------
    # PROBABILI MARCATORI
    # --------------------------------------------------------

    app.add_handler(
        CommandHandler(
            "marcatori",
            marcatori
        )
    )

    # --------------------------------------------------------
    # VERIFICA AUTOMATICA
    # --------------------------------------------------------

    app.job_queue.run_repeating(
        verifica_automatica_job,
        interval=1800,
        first=30
    )

    # --------------------------------------------------------
    # MESSAGGI AVVIO
    # --------------------------------------------------------

    print("")
    print("🔥 CalcioAI avviato")
    print("🤖 Verifica automatica storico attiva")
    print("⏰ Controllo risultati ogni 30 minuti")
    print("🎯 Comando /risultati attivo")
    print("⚽ Comando /marcatori attivo")

    # --------------------------------------------------------
    # POLLING
    # --------------------------------------------------------

    app.run_polling(
        bootstrap_retries=5
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    main()