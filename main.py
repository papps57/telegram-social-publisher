import asyncio
import sys
import signal
from telegram.ext import Application
from config import TELEGRAM_BOT_TOKEN
from bot import conversation_handler


async def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(conversation_handler)

    if len(sys.argv) > 1 and sys.argv[1] == "webhook":
        await app.run_webhook(
            listen="0.0.0.0",
            port=8443,
            url_path=TELEGRAM_BOT_TOKEN,
            webhook_url=f"https://{sys.argv[2]}/{TELEGRAM_BOT_TOKEN}",
        )
        return

    print("Avvio in polling... Premi Ctrl+C per fermare.")
    async with app:
        await app.start()
        await app.updater.start_polling(allowed_updates=["message", "callback_query"])
        stop = asyncio.Event()
        await stop.wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
