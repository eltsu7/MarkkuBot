# coding=UTF-8

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, BaseFilter
import logging
import json

# Enables logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


'''TELEGRAM KAMAA'''


class FilterKiitos(BaseFilter):
    def filter(self, message):
        return "kiitos" in message.text.lower()


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Woof woof motherfucker")


def darkroom(bot, update):
    reply = "Ei toimi vielä"
    bot.send_message(chat_id=update.message.chat_id, text=reply)


def kiitos(bot, update):
    if update.message.from_user.username in data:
        data[update.message.from_user.username] += 1
    else:
        data[update.message.from_user.username] = 1

    file_write("data.json")

    
def handlers(updater):
    dp = updater.dispatcher

    filter_kiitos = FilterKiitos()

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('pimiö', darkroom))
    dp.add_handler(MessageHandler(filter_kiitos, kiitos))
    

''' MUUTA KAMAA '''


def file_read(filename):
    # Reads a json file

    try:
        with open(filename, 'r') as file:
            saved_data = json.load(file)
        file.close()
        return saved_data
    except FileNotFoundError:
        print("Oh dog file not found")
        exit(1)


def file_write(filename):
    # Writes a json file

    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)
    file.close()


def main():
    updater = Updater(token=settings["tg_token"])
    handlers(updater)

    updater.start_polling()

settings = file_read("settings.json")
data = file_read("data.json")
main()


