#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to feed clock with emojis and messages.
TODO !!!
We need to add account limits here !!!!
Need to move Telegram Token to config file together with accounts

Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import json
import re
import redis

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

redis = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    emoji = str(update.message.text.encode("unicode_escape"))
    emoji = emoji.replace('\\\\', '+')
    message = emoji.replace('\\\\', '+')
    emoji = emoji.lower()
    emojis = re.findall(r'(?:\+u)[a-z0-9]{8}', emoji)
    message = re.sub(r'(?:\+U)[a-z0-9]{8}', r'', message)
    message = re.sub(r'\\', r'', message)
    message = re.sub(r'^b\'', r'', message)
    message = re.sub(r'\'$', r'', message)
    message = re.sub(r'^\s+', r'', message)
    message = re.sub(r'\s+$', r'', message)
    redis.set('message', message)
    redis.set('emoji', json.dumps(emojis))
    update.message.reply_text("ok")


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(
        "1470465087:AAFC_Z5Flxr6TjxIDgctOvkCF9UMd4T8cWc", use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
