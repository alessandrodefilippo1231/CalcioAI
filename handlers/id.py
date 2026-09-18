from telegram import Update
from telegram.ext import ContextTypes


async def id_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        f"Il tuo ID Telegram è: {update.effective_user.id}"
    )