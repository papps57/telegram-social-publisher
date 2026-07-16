import os
import sys
import asyncio
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

_loop = asyncio.new_event_loop()


async def _init():
    await application.initialize()


_loop.run_until_complete(_init())


@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)

    _loop.run_until_complete(application.process_update(update))
    return "OK", 200


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "bot": "running"})


def main():
    async def _setup():
        await application.bot.set_webhook(
            url=f"https://{sys.argv[1]}/{TELEGRAM_BOT_TOKEN}",
            allowed_updates=["message", "callback_query"],
        )
        logger.info("Webhook configurato su %s", sys.argv[1])

    asyncio.run(_setup())


if __name__ == "__main__":
    main()
