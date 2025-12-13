from telegram.ext import Updater, CommandHandler, ApplicationBuilder
from telegram.error import TimedOut
import requests
from xkcd import *
import logging
import re
import os.path
import json
import time
from functools import wraps

subscriberChats = []
latestComic = 0
subscribersFile = "subscribers.json"


def load_env(path=".env"):
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, value = line.split("=", 1)
            os.environ[key] = value


async def start(update, context) -> None:
    await update.message.reply_text(
        "Hey! I'm xkcd bot. "
        "Here is my list of commands:\n"
        "/subscribe - I'll notify you whenever a new xkcd is released.\n"
        "/unsubscribe - I'll stop notifying you when new xkcd comics are released.\n"
        "/xkcd - Type in the comic number and I'll find it for you! Type nothing and I'll send you the latest xkcd.\n"
        "/random - I'll send you a random xkcd."
    )


def subscribe(bot, update):
    global subscriberChats
    if update.message.chat_id not in subscriberChats:
        subscriberChats.append(update.message.chat_id)
        update.message.reply_text(
            "You are now subscribed.\n"
            "From now on I will send you new xkcd comics when they are released.\n"
            "If you wish to unsubscribe, send me a /unsubscribe command."
        )
    else:
        update.message.reply_text(
            "Hey you're already subscribed!\nDid you mean /unsubscribe?"
        )


def unsubscribe(bot, update):
    global subscriberChats
    if update.message.chat_id in subscriberChats:
        subscriberChats.remove(update.message.chat_id)
        update.message.reply_text("You have been unsubscribed.")
    else:
        update.message.reply_text("Hey you're not even subscribed to begin with!")


async def xkcd(update, context):
    print(update.message.text)
    if update.message.text == "/xkcd" or update.message.text == "/xkcd latest":
        comic = getLatestComic()
        print(comic)
        await send_comic(update, comic)

    elif update.message.text == "/xkcd random" or update.message.text == "/random":
        print(latestComic)
        comic = getComic(221)
        print(comic)
        await send_comic(update, comic)

    else:
        xkcdNumber = int(re.search(r"\d+", update.message.text).group())
        comic = getComic(xkcdNumber)
        print(comic)
        await send_comic(update, comic)


async def send_comic(update, comic):
    await update.message.reply_photo(photo=comic["img"])
    await update.message.reply_text(
        "xkcd " + str(comic["num"]) + "\nAlt-text: " + comic["alt"]
    )


def comicNotify(bot, job):
    comic = getLatestComic()
    if comic["num"] > latestComic:
        setLatestComic()
        for chat_id in subscriberChats:
            send_message_retry(bot, chat_id, "A new xkcd is out!")
            send_photo_retry(bot, chat_id, comic["img"])
            send_message_retry(
                bot,
                chat_id,
                "xkcd " + str(comic["num"]) + "\nAlt-text: " + comic["alt"],
            )


def setLatestComic():
    global latestComic
    comic = getLatestComic()
    latestComic = comic["num"]


def readSubscribers():
    global subscriberChats
    with open(subscribersFile, "r") as infile:
        subscriberJson = json.load(infile)
        subscriberChats = subscriberJson["subscribers"]


def saveSubscribers(bot, job):
    with open(subscribersFile, "w") as outfile:
        finalJson = {}
        finalJson["subscribers"] = subscriberChats
        json.dump(finalJson, outfile)


def main():
    # First load our subscriber list if it exists:
    if os.path.isfile(subscribersFile):
        readSubscribers()

    # Set up logging to stdout. Todo: Actually make a log file.
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Configure updater with our API token.
    try:
        load_env()
    except FileNotFoundError:
        print("No environment file found. Proceeding.")

    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("Not Telegram token provided. Add one to the `.env` file")
    # updater = Updater(token)
    app = ApplicationBuilder().token(token).build()

    # Create dispatcher and register commands.

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("commands", start))
    # app.add_handler(CommandHandler("subscribe", subscribe))
    # app.add_handler(CommandHandler("unsubscribe", unsubscribe))
    app.add_handler(CommandHandler("xkcd", xkcd))
    app.add_handler(CommandHandler("random", xkcd))

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
