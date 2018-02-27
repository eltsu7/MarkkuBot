# coding=UTF-8

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, BaseFilter
import logging
import json
import urllib.request


# Enables logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


'''TELEGRAM KAMAA'''

viestit = []


class FilterKiitos(BaseFilter):
    def filter(self, message):
        return "kiitos" in message.text.lower()


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Woof woof motherfucker")


def darkroom(bot, update):

    with urllib.request.urlopen("https://ttkamerat.fi/darkroom/api/v1/sensors/latest") as url:
        sensor_data = json.loads(url.read().decode())
        print(sensor_data)
        reply = "Valoa: " + str(sensor_data["entries"][0]["value"]) + " ja ovea: " + str(sensor_data["entries"][1]["value"])
        bot.send_message(chat_id=update.message.chat_id, text=reply)


def kiitos(bot, update):
    # Jos nimi löytyy datasta, lisätään sille yksi viesti ja yksi kiitos
    # Jos ei löydy niin luodaan tyhjä pohja ja ajetaan kiitos() uudelleen

    user = update.message.from_user.username



    if user in data:
        data[user]["count_kiitos"] += 1
        data[user]["count_messages"] += 1
    else:

        data[user] = {
            "count_kiitos": 0,
            "count_messages": 0,
            "count_stickers": 0
            }
        kiitos(bot, update)

    file_write("data.json")


def new_text_message(bot, update):


    user = update.message.from_user.username

    if user in data:
        data[user]["count_messages"] += 1
    else:
        data[user] = {
            "count_kiitos": 0,
            "count_messages": 1,
            "count_stickers": 0
            }

    file_write("data.json")

    
def handlers(updater):
    dp = updater.dispatcher

    filter_kiitos = FilterKiitos()

    # ok eli tässä alla oleville komennoille (esim darkroom) annetaan aina bot ja updater argumenteiksi
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('darkroom', darkroom))
    dp.add_handler(MessageHandler(filter_kiitos, kiitos))
    dp.add_handler(MessageHandler(Filters.text, new_text_message))
    

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
