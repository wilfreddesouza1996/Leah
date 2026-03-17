import asyncio
import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from leah.agent import LeahAgent
from leah.config import settings

logging.basicConfig(level=logging.WARNING)

agent: LeahAgent | None = None


def _authorized(update: Update) -> bool:
    if settings.telegram_allowed_user_id is None:
        return True
    return update.effective_user.id == settings.telegram_allowed_user_id


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _authorized(update):
        return
    await update.message.reply_text("Hey. What do you need?")


async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _authorized(update):
        return
    agent.memory.clear()
    await update.message.reply_text("Memory cleared.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _authorized(update):
        return

    chat_id = update.effective_chat.id
    user_input = update.message.text

    async def keep_typing():
        while True:
            await context.bot.send_chat_action(chat_id=chat_id, action="typing")
            await asyncio.sleep(4)

    typing_task = asyncio.create_task(keep_typing())
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, agent.chat, user_input)
    finally:
        typing_task.cancel()

    # Telegram's per-message limit is 4096 chars
    for i in range(0, len(response), 4096):
        await update.message.reply_text(response[i : i + 4096])


def main() -> None:
    global agent

    if not settings.telegram_bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in .env")

    if settings.telegram_allowed_user_id is None:
        print("Warning: TELEGRAM_ALLOWED_USER_ID not set — anyone can talk to Leah.")

    print("Starting Leah...")
    agent = LeahAgent()

    app = Application.builder().token(settings.telegram_bot_token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Leah is online on Telegram. Press Ctrl+C to stop.")
    app.run_polling(drop_pending_updates=True)
