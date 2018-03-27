# coding=UTF-8

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, BaseFilter
import logging
import json
import urllib.request
import random


# Enables logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

message_counter = 0


'''TELEGRAM KAMAA'''


def start(bot, update):
    count_up(update, "count_commands")
    bot.send_message(chat_id=update.message.chat_id, text="Woof woof")


def darkroom(bot, update):
    print("darkroom")
    count_up(update, "count_commands")
    
    with urllib.request.urlopen("https://ttkamerat.fi/darkroom/api/v1/sensors/latest") as url:
        sensor_data = json.loads(url.read().decode())

        value_light = 0
        value_door = 0
        isDarkroomPopulated = False

        for sensor in sensor_data["entries"]:
            if sensor["sensor"] == "light1":
                value_light = sensor["value"]

            elif sensor["sensor"] == "door1":
                value_door = sensor["value"]

        if value_light > 100:
            isDarkroomPopulated = True
        else:
            isDarkroomPopulated = False

        if isDarkroomPopulated:
            reply = "Joku on pimiöllä :O\n"
        else:
            reply = "Pimiö tyhjä :(\n"

        '''
                
        reply = reply + "(Valoa: " + str(value_light)\
                + " ja ovea: " + str(value_door) + ")"

        '''

        bot.send_message(chat_id=update.message.chat_id, text=reply)


def help(bot, update):
    count_up(update, "count_commands")

    reply = "Komennot:\n" \
            "/darkroom - Kertoo onko joku pimiöllä\n" \
            "/stats - Chattikohtaiset statsit\n" \
            "\n" \
            "Kiitokset, ylistykset sekä ehdotukset -> @eltsu7"

    bot.send_message(chat_id=update.message.chat_id, text=reply)


def count_up(update, var):
    user, chat = check_names(update)

    data[chat][user][var] += 1

    message_counter += 1

    if message_counter % 10 == 0:
        file_write("data.json")



def msg_sticker(bot, update):
    # Kun uusi viesti on stickeri

    print(update.message.from_user.username, "sticker", update.message.sticker.file_id)

    count_up(update, "count_stickers")


def msg_text(bot, update):
    # Kun uusi viesti on tekstiä

    message = update.message.text.lower()
    user, chat = check_names(update)

    print(user, "text", chat, message)

    count_up(update, "count_messages")

    lotto = random.randint(1, 101)

    if "kiitos" in message:

        count_up(update, "count_kiitos")

        if 1 <= lotto <= 10:
            update.message.reply_text("Kiitos")
        elif 11 <= lotto <= 20:
            sticker_index = random.randint(0, len(sticker_list) + 1)

            bot.send_sticker(chat_id=update.message.chat_id, sticker=sticker_list[sticker_index])

    elif "markku" in message and "istu" in message:
        if 1 <= lotto <= 80:
            bot.send_message(chat_id=update.message.chat_id, text="*istuu*")
        else:
            bot.send_message(chat_id=update.message.chat_id, text="*paskoo lattialle*")

    elif "markku" in message and 1 <= lotto <= 10:
        bot.send_message(chat_id=update.message.chat_id, text="woof?")

    elif "filmi" in message and 1 <= lotto <= 5:
        bot.send_message(chat_id=update.message.chat_id, text="Filmi best")


def stats(bot, update):
    user, chat = check_names(update)

    print(user, chat, "stats")

    user_data = data[chat][user]

    count_up(update, "count_commands")

    percent = "?"
    if user_data["count_stickers"] + user_data["count_messages"] != 0:
        percent = round(((user_data["count_stickers"]) / (user_data["count_stickers"] + user_data["count_messages"]) * 100), 2)

    msg = "@{}:\nMessages: {}".format(user, user_data["count_messages"])
    msg += "\nStickers: {} ({}%)".format(user_data["count_stickers"], percent)
    msg += "\nKiitos: {}".format(user_data["count_kiitos"])
    # msg += "\nPublished photos: {}".format(user_data["count_published"])

    bot.send_message(chat_id=update.message.chat_id, text=msg)

    
def handlers(updater):
    dp = updater.dispatcher

    # ok eli tässä alla oleville komennoille (esim darkroom) annetaan aina bot ja updater argumenteiksi
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('darkroom', darkroom))
    dp.add_handler(CommandHandler('stats', stats))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(MessageHandler(Filters.sticker, msg_sticker))
    dp.add_handler(MessageHandler(Filters.text, msg_text))
    

''' MUUTA KAMAA '''


def check_names(update):
    user = update.message.from_user.username
    chat = update.message.chat.title
    chat_type = update.message.chat.type

    if chat_type == "private":
        chat = "Private"

    if chat not in data:
        data[chat] = {}

    if user not in data[chat]:
        new_name(chat, user)

    file_write("data.json")

    return user, chat


def new_name(chat, username):
    data[chat][username] = {
            "count_kiitos": 0,
            "count_messages": 0,
            "count_stickers": 0,
            "count_published": 0,
            "count_commands": 0
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
