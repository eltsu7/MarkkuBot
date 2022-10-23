# coding: utf-8

from os import environ
from environs import Env

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    BaseFilter,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
    CallbackQueryHandler,
)

from db.database_psql import DatabasePsql

from command_handlers.command_router import CommandRouter
from message_handlers.message_router import MessageRouter


def handlers(updater):
    dp = updater.dispatcher

    # Avataan tietokanta
    db = DatabasePsql()

    # Alustetaan routerit
    cr = CommandRouter(db)
    mr = MessageRouter(db)

    # Komennot
    dp.add_handler(CommandHandler(cr.get_commands(), cr.route_command, pass_args=True))

    dp.add_handler(CallbackQueryHandler(cr.blacklist_confirm))

    # Suoraa viestiä urkkivat kilkkeet
    dp.add_handler(
        MessageHandler(Filters.sticker, add_parameter(mr.route_command, "msg_sticker"))
    )
    dp.add_handler(
        MessageHandler(Filters.text, add_parameter(mr.route_command, "msg_text"))
    )
    dp.add_handler(
        MessageHandler(Filters.photo, add_parameter(mr.route_command, "msg_photo"))
    )
    dp.add_handler(
        MessageHandler(Filters.document, add_parameter(mr.route_command, "msg_gif"))
    )
    dp.add_handler(
        MessageHandler(
            Filters.status_update.new_chat_members,
            add_parameter(mr.route_command, "status_new_members"),
        )
    )


def add_parameter(function, parameter):
    def new_function(bot, update, args=[]):
        function(bot, update, parameter, args)

    return new_function


def main():
    env = Env()
    env.read_env()

    updater = Updater(token=environ["TG_TOKEN"])
    handlers(updater)

    updater.start_polling()


main()
