# coding=UTF-8

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, BaseFilter
import logging
import json
import urllib.request
import random


# Enables logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


'''TELEGRAM KAMAA'''


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Woof woof motherfucker")


def darkroom(bot, update):
    with urllib.request.urlopen("https://ttkamerat.fi/darkroom/api/v1/sensors/latest") as url:
        sensor_data = json.loads(url.read().decode())
        reply = "Valoa: " + str(sensor_data["entries"][0]["value"])\
                + " ja ovea: " + str(sensor_data["entries"][1]["value"])
        bot.send_message(chat_id=update.message.chat_id, text=reply)


def count_up(user, var):
    if user not in data:
        new_name(user)

    data[user][var] += 1

    file_write("data.json")


def msg_sticker(bot, update):
    # Kun uusi viesti on stickeri

    user = update.message.from_user.username

    print(user, "sticker", update.message.sticker.file_id)

    count_up(user, "count_sticker")


def msg_text(bot, update):
    # Kun uusi viesti on tekstiä

    user = update.message.from_user.username
    message = update.message.text.lower()

    print(user, "text", message)

    count_up(user, "count_messages")

    lotto = random.randint(1, 101)

    if "kiitos" in message:

        count_up(user, "count_kiitos")

        if 1 <= lotto <= 10:
            update.message.reply_text("Kiitos")
        elif 11 <= lotto <= 20:
            sticker_index = random.randint(0, len(sticker_list) + 1)

            bot.send_sticker(chat_id=update.message.chat_id, sticker=sticker_list[sticker_index])

    elif "markku" in message:
        if 1 <= lotto <= 50:
            bot.send_message(chat_id=update.message.chat_id, text="woof?")
    
    
def stats(bot, update):
    user = update.message.from_user.username

    print(user, "stats")

    if not user in data:
        new_name(user)
        file_write("data.json")

    perc = round((data[user]["count_sticker"]) / (data[user]["count_sticker"] + data[user]["count_messages"]), 2)
    
    msg = ""
    msg += str(user) + ": \nMessages: " + str(data[user]["count_messages"]) + " ({}%) \n".format(perc)
    msg += "Stickers: " + str(data[user]["count_stickers"]) + "\n"
    msg += "Kiitos: " + str(data[user]["count_kiitos"])

    bot.send_message(chat_id=update.message.chat_id, text=msg)

    
def handlers(updater):
    dp = updater.dispatcher

    # ok eli tässä alla oleville komennoille (esim darkroom) annetaan aina bot ja updater argumenteiksi
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('darkroom', darkroom))
    dp.add_handler(CommandHandler('stats', stats))
    dp.add_handler(MessageHandler(Filters.sticker, msg_sticker))
    dp.add_handler(MessageHandler(Filters.text, msg_text))
    

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
sticker_list = file_read("sticker_list_kiitos.json")
data = file_read("data.json")
main()
