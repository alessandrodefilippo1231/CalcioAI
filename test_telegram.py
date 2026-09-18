import asyncio
import os

from dotenv import load_dotenv
from telegram import Bot


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")


async def main():

    bot = Bot(BOT_TOKEN)

    try:

        me = await bot.get_me()

        print("✅ TELEGRAM OK")
        print("BOT:", me.username)
        print("ID:", me.id)

    except Exception as e:

        print("❌ ERRORE TELEGRAM")
        print(type(e).__name__)
        print(e)

    finally:

        await bot.shutdown()


asyncio.run(main())