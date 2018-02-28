# coding=UTF-8

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, BaseFilter
import logging
import json
import urllib.request
import random


# Enables logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


'''TELEGRAM KAMAA'''


class FilterKiitos(BaseFilter):
    def filter(self, message):
        return "kiitos" in message.text.lower()


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Woof woof motherfucker")


def darkroom(bot, update):
    with urllib.request.urlopen("https://ttkamerat.fi/darkroom/api/v1/sensors/latest") as url:
        sensor_data = json.loads(url.read().decode())
        reply = "Valoa: " + str(sensor_data["entries"][0]["value"]) + " ja ovea: " + str(sensor_data["entries"][1]["value"])
        bot.send_message(chat_id=update.message.chat_id, text=reply)


def kiitos(bot, update):
    # Jos nimi löytyy datasta, lisätään sille yksi viesti ja yksi kiitos
    # Jos ei löydy niin luodaan tyhjä pohja ja ajetaan kiitos() uudelleen

    user = update.message.from_user.username

    lottokuponki = random.randint(0, 10)
    #print(lottokuponki)

    if lottokuponki == 3:
        bot.send_message(chat_id=update.message.chat_id, text="Kiitos")
    elif lottokuponki == 4:
        bot.send_sticker(chat_id=update.message.chat_id, sticker="CAADAgADIQEAAiHfMQEwSd7-kQ3ZzwI")

    if user in data:
        data[user]["count_kiitos"] += 1
        data[user]["count_messages"] += 1

    else:
        new_name(user)
        kiitos(bot, update)

    file_write("data.json")


def add_count_text(bot, update):
    # Laskee yhden tekstiviestin lisää

    user = update.message.from_user.username

    print(user, " text")

    if user in data:
        data[user]["count_messages"] += 1
    else:
        new_name(user)
        add_count_text(bot, update)

    file_write("data.json")


def add_count_sticker(bot, update):
    # Laskee yhden stickerin lisää
    
    # print(update.message.sticker.file_id)

    user = update.message.from_user.username

    # print(user, " sticker")

    if user in data:
        data[user]["count_stickers"] += 1
    else:
        new_name(user)
        add_count_sticker(bot, update)

    file_write("data.json")
    
    
def stats(bot, update):
    msg = ""
    
    for name in data:
        
        namestats = str(name) + ": \n" + "Messages: " + str(data[name]["count_messages"]) + "\n\n"
        
        msg += namestats
        
    update.message.reply_text(msg)

    
def handlers(updater):
    dp = updater.dispatcher

    filter_kiitos = FilterKiitos()

    # ok eli tässä alla oleville komennoille (esim darkroom) annetaan aina bot ja updater argumenteiksi
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('darkroom', darkroom))
    dp.add_handler(CommandHandler('stats', stats))
    dp.add_handler(MessageHandler(Filters.sticker, add_count_sticker))
    dp.add_handler(MessageHandler(filter_kiitos, kiitos))
    dp.add_handler(MessageHandler(Filters.text, add_count_text))
    

''' MUUTA KAMAA '''


def new_name(username):
    data[username] = {
            "count_kiitos": 0,
            "count_messages": 0,
            "count_stickers": 0
            }


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
