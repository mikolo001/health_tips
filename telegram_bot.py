
import asyncio

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from config import (
    TELEGRAM_BOT_TOKEN,
    client,
    MODEL_NAME,
    FOOTBALL_ANALYST_INSTRUCTIONS
)


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    welcome_message = """
Hello! 👋 Welcome to HealthMate AI.

I can help you understand general health topics,
nutrition, wellness, and common health questions.

I provide general health information, not a diagnosis.

For emergencies, seek emergency medical care immediately.

Please avoid sharing your passwords, address, or
unnecessary personal medical information.

Send me your health question whenever you're ready!
"""

    await update.message.reply_text(welcome_message)


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "Welcome to HealthMate AI!\n\n"
        "Send me a general health question to get started.\n\n"
        "/start - Start the assistant\n"
        "/help - Show this help message"
    )


def ask_healthmate(question):
    response = client.responses.create(
        model=MODEL_NAME,
        instructions=FOOTBALL_ANALYST_INSTRUCTIONS,
        input=question
    )

    return response.output_text


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    question = update.message.text

    # Tell the user the bot is working
    status_message = await update.message.reply_text(
        "HealthMate AI is preparing your answer... ⏳"
    )

    try:
        answer = await asyncio.to_thread(
            ask_healthmate,
            question
        )

        if not answer or not answer.strip():
            answer = (
                "I couldn't generate an answer this time. "
                "Please try asking again."
            )

        # Telegram limits the length of a single message.
        # Split longer answers into smaller messages.
        for index in range(0, len(answer), 4000):
            await update.message.reply_text(
                answer[index:index + 4000]
            )

        await status_message.delete()

    except Exception as error:
        print("HealthMate Telegram error:", error)

        await status_message.edit_text(
            "Sorry, I couldn't generate your answer. "
            "Please try again shortly."
        )


def main():
    if (
        not TELEGRAM_BOT_TOKEN
        or TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN"
    ):
        raise ValueError(
            "Please add your Telegram bot token to config.py."
        )

    application = (
        ApplicationBuilder()
        .token(TELEGRAM_BOT_TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("help", help_command)
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print("HealthMate AI Telegram bot is running!")

    application.run_polling()


if __name__ == "__main__":
    main()
