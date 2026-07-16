import os
import sys
import logging
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application
from config import TELEGRAM_BOT_TOKEN
from bot import conversation_handler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
application.add_handler(conversation_handler)

_initialized = False


async def _ensure_init():
    global _initialized
    if not _initialized:
        await application.initialize()
        _initialized = True


@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)

    async def process():
        await _ensure_init()
        await application.process_update(update)

    import asyncio
    asyncio.run(process())
    return "OK", 200


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "bot": "running"})


def main():
    import asyncio

    async def _setup():
        await _ensure_init()
        await application.bot.set_webhook(
            url=f"https://{sys.argv[1]}/{TELEGRAM_BOT_TOKEN}",
            allowed_updates=["message", "callback_query"],
        )
        logger.info("Webhook configurato su %s", sys.argv[1])

    asyncio.run(_setup())


if __name__ == "__main__":
    main()
