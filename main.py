from telegram.ext import CommandHandler, ApplicationBuilder, ContextTypes
from xkcd import getComic, getLatestComic, getRandomComic
import logging
import re
import os.path

latestComic = 0

def load_env(path=".env"):
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, value = line.split("=", 1)
            os.environ[key] = value


async def start(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hey! I'm xkcd bot. "
        "Here is my list of commands:\n"
        "/xkcd - Type in the comic number and I'll find it for you! Type nothing and I'll send you the latest xkcd.\n"
        "/random - I'll send you a random xkcd."
    )


async def xkcd(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.text == "/xkcd" or update.message.text == "/xkcd latest":
        setLatestComic()
        comic = getLatestComic()
        await send_comic(update, comic)

    elif update.message.text == "/xkcd random":
        await random(update, context)

    else:
        xkcdNumber = int(re.search(r"\d+", update.message.text).group())
        comic = getComic(xkcdNumber)
        await send_comic(update, comic)


async def random(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    setLatestComic()
    await send_comic(update, getRandomComic(latestComic))


async def send_comic(update, comic):
    num = comic["num"]
    title = comic["safe_title"]
    alt = comic["alt"]
    await update.message.reply_photo(photo=comic["img"])
    await update.message.reply_html(
        f'{num}. <a href="https://m.xkcd.com/{num}">{title}</a>\n'
        f'<i>{alt}</i>',
        disable_web_page_preview=True
    )


def setLatestComic():
    global latestComic
    comic = getLatestComic()
    latestComic = comic["num"]


def main() -> None:
    # Set up logging to stdout. Todo: Actually make a log file.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Configure updater with our API token.
    try:
        load_env()
    except FileNotFoundError:
        print("No environment file found. Proceeding.")

    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("No Telegram token provided. Add one to the `.env` file")
    # updater = Updater(token)
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("xkcd", xkcd))
    app.add_handler(CommandHandler("random", random))

    # Set latest available comic.
    setLatestComic()

    # Create scheduled job for notifying people about new comics (checks every 30 min).
    # notifierJob = updater.job_queue.run_repeating(comicNotify, interval=1800, first=0)
    # notifierJob.enabled = True

    # Create scheduled job for saving the subscriber list to disk every minute.
    # subscriberSavingJob = updater.job_queue.run_repeating(saveSubscribers, interval=60, first=60)
    # subscriberSavingJob.enabled = True

    # Start the bot.
    app.run_polling()

    # Note it does not save the subscribers one last time before exiting.


if __name__ == "__main__":
    main()
