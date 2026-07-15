import asyncio
import sys
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
    else:
        print("Avvio in polling... Premi Ctrl+C per fermare.")
        await app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    asyncio.run(main())
