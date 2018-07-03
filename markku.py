# coding: UTF-8

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, BaseFilter
import logging
import json
from urllib.request import Request, urlopen
import random


# Enables logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

message_counter = 0


def start(bot, update):
    count_and_write(update, "count_commands")
    bot.send_message(chat_id=update.message.chat_id, text="Woof woof")


def thiskillsthemarkku(bot, update):
    file_write("data.json")

    printlog(update, "kill")

    exit()


def darkroom(bot, update):
    print("darkroom")
    count_and_write(update, "count_commands")
    
    with urlopen("https://ttkamerat.fi/darkroom/api/v1/sensors/latest") as url:
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

        bot.send_message(chat_id=update.message.chat_id, text=reply)


def help(bot, update):
    count_and_write(update, "count_commands")

    reply = "Komennot:\n" \
            "/darkroom - Kertoo onko joku pimiöllä\n" \
            "/stats - Chattikohtaiset statsit\n" \
            "/noutaja - Postaa satunnaisen noutajakuvan\n"\
            "\n" \
            "Botin koodit: @eltsu7\n" \
            "Valosensorit ja siihen koodit: @anttimoi"

    bot.send_message(chat_id=update.message.chat_id, text=reply)


def count_and_write(update, var):
    user, chat = check_names(update)

    if var in data[chat][user]:
        data[chat][user][var] += 1
    else:
        data[chat][user][var] = 1

    global message_counter

    if message_counter % 10 == 0:
        print("writing data\n")
        file_write("data.json")

    message_counter += 1


def toptenlist(chat, var):

    topten = {}

    for user in data[chat]:

        if len(topten) < 10:

            topten[user] = data[chat][user][var]

        else:

            few_name = min(topten, key=topten.get)

            if data[chat][user][var] > topten[few_name]:

                topten.pop(few_name)
                topten[user] = data[chat][user][var]

    text = ""
    number = 1

    topten_sorted = sorted(topten, key=topten.get, reverse=True)

    for i in topten_sorted:
        text += str(number) + ". " + i + ": " + str(topten[i]) + "\n"
        number += 1

    return text, len(topten_sorted)


def topten_messages(bot, update):
    user, chat = check_names(update)

    printlog(update, "toptenmessages")

    list, number = toptenlist(chat, "count_messages")

    text = "Top " + str(number) + " viestittelijät:\n" + list

    bot.send_message(chat_id=update.message.chat_id, text=text)

    count_and_write(update, "count_commands")


def topten_kiitos(bot, update):
    user, chat = check_names(update)

    printlog(update, "toptenkiitos")

    list, number = toptenlist(chat, "count_kiitos")

    text = "Top " + str(number) + " kiitostelijat:\n" + list

    bot.send_message(chat_id=update.message.chat_id, text=text)

    count_and_write(update, "count_commands")


def noutaja(bot, update):
    user, chat = check_names(update)

    printlog(update, "noutaja")

    url = "https://dog.ceo/api/breed/retriever/golden/images/random"

    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

    with urlopen(req) as page:
        retriever_data = json.loads(page.read().decode())

        picture_link = retriever_data["message"]

        bot.sendPhoto(chat_id=update.message.chat_id, photo=picture_link)

    count_and_write(update, "count_commands")


def protip(bot, update):
    printlog(update, "protip")

    count_and_write(update, "count_commands")
    protip_index = random.randint(0, len(protip_list) - 1)

    bot.send_message(chat_id=update.message.chat_id, text=protip_list[protip_index])


def msg_text(bot, update):
    # Kun uusi viesti on tekstiä

    message = update.message.text.lower()
    user, chat = check_names(update)

    printlog(update, "text")

    count_and_write(update, "count_messages")

    lotto = random.randint(1, 201)

    if "kiitos" in message:

        count_and_write(update, "count_kiitos")

        if lotto < 11:
            update.message.reply_text("Kiitos")
        elif lotto < 16:
            sticker_index = random.randint(0, len(sticker_list) - 1)
            bot.send_sticker(chat_id=update.message.chat_id, sticker=sticker_list[sticker_index])

        elif lotto < 17:
            update.message.reply_text("Ole hyvä")

    elif "markku" in message and "istu" in message:
        if lotto < 91:
            bot.send_message(chat_id=update.message.chat_id, text="*istuu*")
        else:
            bot.send_message(chat_id=update.message.chat_id, text="*paskoo lattialle*")

    elif "huono markku" in message:
        bot.send_message(chat_id=update.message.chat_id, text="w00F")

    elif "filmi" in message and lotto < 11:
        bot.send_message(chat_id=update.message.chat_id, text="Filmi best")


def msg_sticker(bot, update):
    # Kun uusi viesti on stickeri

    printlog(update, "sticker")

    count_and_write(update, "count_stickers")


def msg_photo(bot, update):
    printlog(update, "photo")

    count_and_write(update, "count_photos")


def msg_gif(bot, update):
    printlog(update, "gif")

    count_and_write(update, "count_gifs")


def stats(bot, update):
    user, chat = check_names(update)

    printlog(update, "stats")

    user_data = data[chat][user]

    for var in ["count_messages", "count_stickers", "count_kiitos", "count_photos", "count_commands"]:
        if var not in user_data:
            user_data[var] = 0

    count_and_write(update, "count_commands")

    sticker_percent = "?"
    kiitos_percent = "?"

    if user_data["count_stickers"] + user_data["count_messages"] != 0:
        sticker_percent = round(((user_data["count_stickers"]) / (user_data["count_stickers"] + user_data["count_messages"]) * 100), 2)

    if user_data["count_messages"] != 0:
        kiitos_percent = round(((user_data["count_kiitos"]) / (user_data["count_messages"]) * 100), 2)

    msg = "@{}:\nMessages: {}".format(user, user_data["count_messages"])
    msg += "\nStickers: {} ({}%)".format(user_data["count_stickers"], sticker_percent)
    msg += "\nKiitos: {} ({}%)".format(user_data["count_kiitos"], kiitos_percent)
    msg += "\nPhotos: {}".format(user_data["count_photos"])

    # msg += "\nPublished photos: {}".format(user_data["count_published"])

    bot.send_message(chat_id=update.message.chat_id, text=msg)


def published(bot, update, text):
    user, chat = check_names(update)

    print(user, chat, "published")

    print(text)

    
def handlers(updater):
    dp = updater.dispatcher

    # ok eli tässä alla oleville komennoille (esim darkroom) annetaan aina bot ja updater argumenteiksi
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('darkroom', darkroom))
    dp.add_handler(CommandHandler('stats', stats))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('noutaja', noutaja))
    dp.add_handler(CommandHandler('toptenmsg', topten_messages))
    dp.add_handler(CommandHandler('toptenkiitos', topten_kiitos))
    dp.add_handler(CommandHandler('protip', protip))
    dp.add_handler(CommandHandler('published', published, pass_args=True))
    dp.add_handler(CommandHandler('thiskillsthemarkku', thiskillsthemarkku))
    dp.add_handler(MessageHandler(Filters.sticker, msg_sticker))
    dp.add_handler(MessageHandler(Filters.text, msg_text))
    dp.add_handler(MessageHandler(Filters.photo, msg_photo))
    dp.add_handler(MessageHandler(Filters.document, msg_gif))



def printlog(update, msg_type):
    username = update.message.from_user.username
    content = ""

    print("Type: ", msg_type, "\nUsername: ", username)

    if msg_type == "sticker":
        content = update.message.sticker.file_id
    elif msg_type == "text":
        content = update.message.text

    if content != "":
        print("Content: ", content)

    print("\n")


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
        with open(filename, 'r', encoding='utf-8') as file:
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
protip_list = file_read("tips.json")
data = file_read("data.json")
main()
