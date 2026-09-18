from telegram import Update
from telegram.ext import ContextTypes

from services.storico_ai import aggiorna_esito


ADMIN_ID = 505296696


async def verifica(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != ADMIN_ID:

        await update.message.reply_text(
            "❌ Comando riservato al proprietario."
        )

        return


    if len(context.args) < 2:

        await update.message.reply_text(
            "Uso corretto:\n\n"
            "/verifica ID CORRETTO\n"
            "/verifica ID ERRATO\n\n"
            "Esempio:\n"
            "/verifica 1 CORRETTO"
        )

        return


    try:

        id_analisi = int(context.args[0])

    except ValueError:

        await update.message.reply_text(
            "❌ ID non valido."
        )

        return


    esito = context.args[1].upper()


    if esito not in [
        "CORRETTO",
        "ERRATO",
        "ANNULLATA"
    ]:

        await update.message.reply_text(
            "❌ Usa solo CORRETTO o ERRATO."
        )

        return



    aggiorna_esito(
        id_analisi,
        "Verificato manualmente",
        esito
    )


    await update.message.reply_text(

        "✅ Storico aggiornato\n\n"
        f"🆔 Analisi: {id_analisi}\n"
        f"📊 Esito: {esito}"

    )