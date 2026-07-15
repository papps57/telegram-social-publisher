import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from config import PAGES, ALLOWED_USER_IDS, token_days_left
from utils import download_image, cleanup_temp
from meta_publisher import publish_all

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

SELECT_PAGE, AWAIT_CONTENT, CONFIRM_POST = range(3)


async def _check_auth(update: Update):
    user = update.effective_user
    if user and user.id in ALLOWED_USER_IDS:
        return True
    await update.effective_message.reply_text("Non sei autorizzato a usare questo bot.")
    return False


def _preview_text(text):
    return text[:200] + "..." if len(text) > 200 else text


def _page_name(context):
    return PAGES[context.user_data["selected_page"]]["name"]


async def _remind_token(message):
    days = token_days_left()
    if days is None:
        return
    if days <= 0:
        await message.reply_text(
            "ATTENZIONE: Il token Facebook potrebbe essere scaduto!\n"
            "Apri SETUP.md e rigeneralo seguendo il punto 5."
        )
    elif days <= 10:
        await message.reply_text(
            f"Promemoria: il token Facebook scadrà tra {days} giorni.\n"
            "Rigeneralo seguendo il punto 5 di SETUP.md."
        )


async def start(update: Update, context):
    if not await _check_auth(update):
        return ConversationHandler.END

    await _remind_token(update.effective_message)

    context.user_data.clear()

    keyboard = [
        [InlineKeyboardButton(p["name"], callback_data=f"page_{i}")]
        for i, p in enumerate(PAGES)
    ]
    await update.effective_message.reply_text(
        "Seleziona la pagina su cui pubblicare:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return SELECT_PAGE


async def select_page(update: Update, context):
    query = update.callback_query
    await query.answer()

    idx = int(query.data.split("_")[1])
    context.user_data["selected_page"] = idx

    await query.edit_message_text(
        f"Pagina selezionata: {_page_name(context)}\n\n"
        "Ora invia il testo e le foto (max 10) da pubblicare.\n"
        "Puoi mandare tutto in un album con didascalia,\n"
        "oppure testo e foto separati.\n"
        "Quando hai finito usa /done."
    )
    return AWAIT_CONTENT


async def _flush_album(context):
    album = context.user_data.pop("pending_album", None)
    if not album:
        return
    text_from_album = album.get("caption", "")
    if text_from_album and not context.user_data.get("post_text"):
        context.user_data["post_text"] = text_from_album
    for file_id in album.get("file_ids", []):
        if len(context.user_data.get("image_paths", [])) >= 10:
            break
        path = await download_image(file_id, context.bot)
        context.user_data.setdefault("image_paths", []).append(path)


async def receive_text(update: Update, context):
    if "selected_page" not in context.user_data:
        await update.effective_message.reply_text("Usa /start per selezionare prima una pagina.")
        return AWAIT_CONTENT

    context.user_data["post_text"] = update.effective_message.text or ""
    await update.effective_message.reply_text("Testo ricevuto. Invia le foto o /done per pubblicare.")
    return AWAIT_CONTENT


async def receive_single_photo(update: Update, context):
    if "selected_page" not in context.user_data:
        await update.effective_message.reply_text("Usa /start per selezionare prima una pagina.")
        return AWAIT_CONTENT

    msg = update.effective_message
    path = await download_image(msg.photo[-1].file_id, context.bot)
    context.user_data.setdefault("image_paths", []).append(path)

    if msg.caption:
        context.user_data["post_text"] = msg.caption

    count = len(context.user_data["image_paths"])
    if count >= 10:
        await msg.reply_text("Foto massime raggiunte (10).")
        return await _ask_confirmation(update, context)
    await msg.reply_text(f"Foto {count}/10. Altre foto o /done.")
    return AWAIT_CONTENT


async def receive_album_photo(update: Update, context):
    if "selected_page" not in context.user_data:
        return AWAIT_CONTENT

    msg = update.effective_message
    mg_id = msg.media_group_id

    if context.user_data.get("pending_album", {}).get("id") != mg_id:
        await _flush_album(context)
        context.user_data["pending_album"] = {"id": mg_id, "file_ids": [], "caption": ""}

    album = context.user_data["pending_album"]
    album["file_ids"].append(msg.photo[-1].file_id)
    if msg.caption:
        album["caption"] = msg.caption

    return AWAIT_CONTENT


async def done(update: Update, context):
    if "selected_page" not in context.user_data:
        await update.effective_message.reply_text("Usa /start per iniziare.")
        return ConversationHandler.END

    await _flush_album(context)

    image_paths = context.user_data.get("image_paths", [])
    text = context.user_data.get("post_text", "")
    if not image_paths:
        await update.effective_message.reply_text("Nessuna foto ricevuta. Invia almeno una foto.")
        return AWAIT_CONTENT

    return await _ask_confirmation(update, context)


async def _ask_confirmation(update, context):
    text = context.user_data.get("post_text", "")
    image_paths = context.user_data.get("image_paths", [])

    keyboard = [
        [
            InlineKeyboardButton("Pubblica", callback_data="confirm"),
            InlineKeyboardButton("Annulla", callback_data="cancel"),
        ]
    ]

    info = (
        f"Pubblicare su {_page_name(context)} + Instagram?\n\n"
        f"Testo: {_preview_text(text)}\n"
        f"Immagini: {len(image_paths)}\n\n"
        "Confermi?"
    )

    await update.effective_message.reply_text(info, reply_markup=InlineKeyboardMarkup(keyboard))
    return CONFIRM_POST


async def confirm_post(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "cancel":
        cleanup_temp(context.user_data.get("image_paths", []))
        context.user_data.clear()
        await query.edit_message_text("Annullato.")
        return ConversationHandler.END

    page = PAGES[context.user_data["selected_page"]]
    text = context.user_data.get("post_text", "")
    image_paths = context.user_data.get("image_paths", [])

    await query.edit_message_text("Pubblicazione in corso... attendi.")

    try:
        result = publish_all(page, text, image_paths)
        msg = (
            "Pubblicato!\n\n"
            f"Facebook: {result['facebook']['url']}\n"
            f"Instagram: {result['instagram']['url']}"
        )
    except Exception as e:
        logger.exception("Pubblicazione fallita")
        msg = f"Errore durante la pubblicazione:\n{e}"

    cleanup_temp(image_paths)
    context.user_data.clear()
    await query.edit_message_text(msg)
    await _remind_token(query.message)
    return ConversationHandler.END


async def cancel(update: Update, context):
    cleanup_temp(context.user_data.get("image_paths", []))
    context.user_data.clear()
    await update.effective_message.reply_text("Operazione annullata.")
    return ConversationHandler.END


conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        SELECT_PAGE: [CallbackQueryHandler(select_page, pattern=r"^page_\d+$")],
        AWAIT_CONTENT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.CAPTION, receive_text),
            MessageHandler(filters.PHOTO & ~filters.MEDIA_GROUP, receive_single_photo),
            MessageHandler(filters.MEDIA_GROUP, receive_album_photo),
            CommandHandler("done", done),
        ],
        CONFIRM_POST: [
            CallbackQueryHandler(confirm_post, pattern=r"^(confirm|cancel)$")
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
