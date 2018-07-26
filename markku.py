# coding: utf-8

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, BaseFilter
import logging
import json
from urllib.request import Request, urlopen
import random
from pymongo import MongoClient, ASCENDING

# Enables logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def start(bot, update):
    printlog(update, "start")
    count_and_write(update, "commands")

    bot.send_message(chat_id=update.message.chat_id, text="Woof woof")


def thiskillsthemarkku(bot, update):
    printlog(update, "kill")

    db_client.close()

    exit()


def darkroom(bot, update):
    printlog(update, "darkroom")
    count_and_write(update, "commands")
    
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
    printlog(update, "help")
    check_names(update)
    count_and_write(update, "commands")

    reply = "Komennot:\n" \
            "/darkroom - Kertoo onko joku pimiöllä\n" \
            "/stats - Chattikohtaiset statsit\n" \
            "/noutaja - Postaa satunnaisen noutajakuvan\n"\
            "\n" \
            "Botin koodit: @eltsu7 ja @kulmajaba\n" \
            "Valosensorit ja siihen koodit: @anttimoi"

    bot.send_message(chat_id=update.message.chat_id, text=reply)


# TODO: siirrä tänne chatin ja userin tsekkaus? Käytä updaten kenttiä user_id ja chat_id
# TODO: check_names ja count_and_write aina peräkkäin
# TODO: lisää kenttä jos ei löydy
def count_and_write(update, var):
    user_id, chat_id = check_names(update)

    chats_collection.update_one(
        { "chat_id": chat_id, "users.user_id": user_id },
        { "$inc": { "users.$.count." + var: 1 }}
    )


# TODO: tsekkaa onko nimi Not Found, tsekkaa onko käyttäjänimi joku järkevä, jos on niin päivitä
# TODO: nää haut menee osin päällekkäin monen funkkarin kanssa, jossa tarvitaan hetken kuluttua
# Usernamee tai chattia tai muuta.
def check_names(update):
    user_id = str(update.message.from_user.id)

    # priva-chateissa chat id == user id
    chat_id = str(update.message.chat.id)

    if chats_collection.find_one({ "chat_id": chat_id }) == None:
        new_chat = {
            "chat_id": chat_id,
            "title": update.message.chat.title
        }
        chats_collection.insert_one(new_chat)

        # Create unique index
        chats_collection.create_index([( "chat_id", ASCENDING )], unique=True)

    if chats_collection.find_one({ "chat_id": chat_id, "users.user_id": user_id }) == None:
        new_name(update, chat_id)

    return user_id, chat_id


def new_name(update, chat_id):
    user_id = str(update.message.from_user.id)

    if update.message.from_user.username is not None:
        username = update.message.from_user.username
    else:
        username = "Not found"

    new_user = {
        "user_id": user_id,
        "username": username,
        "count": {
            "messages": 0,
            "stickers": 0,
            "photos": 0,
            "gifs": 0,
            "commands": 0,
            "published": 0,
            "kiitos": 0
        }
    }

    chats_collection.update_one(
        { "chat_id": chat_id },
        { "$push": { "users": new_user }}
    )

    # Create unique index for user array elements
    # TODO: eihän se nyt noin toimi
    chats_collection.create_index([( "users", ASCENDING )], unique=True)


def toptenlist(chat_id, var):
    cursor = chats_collection.aggregate([
        {"$match": {"chat_id": chat_id}},
        {"$project": {"_id": 0, "chat_id": 1, "users": {"username": 1, "count": 1}}},
        {"$unwind": "$users"},
        {"$replaceRoot": {"newRoot": "$users"}},
        {"$project": {"_id": 0, "username": 1, "count": "$count." + var}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ])
    topten_sorted = list(cursor)

    text = ""
    number = 1

    for user in topten_sorted:
        text += str(number) + ". " + user["username"] + ": " + str(user["count"]) + "\n"
        number += 1

    return text, len(topten_sorted)


def topten_messages(bot, update):
    printlog(update, "toptenmessages")
    _, chat_id = check_names(update) # Ignoraa user_id
    count_and_write(update, "commands")

    list, number = toptenlist(chat_id, "messages")

    text = "Top " + str(number) + " viestittelijät:\n" + list

    bot.send_message(chat_id=update.message.chat_id, text=text)


def topten_kiitos(bot, update):
    printlog(update, "toptenkiitos")
    _, chat_id = check_names(update) # Ignoraa user_id
    count_and_write(update, "commands")

    list, number = toptenlist(chat_id, "kiitos")

    text = "Top " + str(number) + " kiitostelijat:\n" + list

    bot.send_message(chat_id=update.message.chat_id, text=text)


def noutaja(bot, update):
    printlog(update, "noutaja")
    _, chat_id = check_names(update) # Ignoraa user_id
    count_and_write(update, "commands")

    url = "https://dog.ceo/api/breed/retriever/golden/images/random"

    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

    with urlopen(req) as page:
        retriever_data = json.loads(page.read().decode())

        picture_link = retriever_data["message"]

        bot.sendPhoto(chat_id=chat_id, photo=picture_link)


def protip(bot, update):
    printlog(update, "protip")
    _, chat_id = check_names(update) # Ignoraa user_id
    count_and_write(update, "commands")

    protip_index = random.randint(0, len(protip_list) - 1)

    bot.send_message(chat_id=chat_id, text=protip_list[protip_index])


def msg_text(bot, update):
    printlog(update, "text")
    _, chat_id = check_names(update) # Ignoraa user_id
    count_and_write(update, "messages")

    message = update.message.text.lower()

    lotto = random.randint(1, 201)

    if "kiitos" in message:
        count_and_write(update, "kiitos")

        if lotto < 11:
            update.message.reply_text("Kiitos")
        elif lotto < 16:
            sticker_index = random.randint(0, len(sticker_list) - 1)
            bot.send_sticker(chat_id=chat_id, sticker=sticker_list[sticker_index])

        elif lotto < 17:
            update.message.reply_text("Ole hyvä")

    elif "markku" in message and "istu" in message:
        if lotto < 91:
            bot.send_message(chat_id=chat_id, text="*istuu*")
        else:
            bot.send_message(chat_id=chat_id, text="*paskoo lattialle*")

    elif "huono markku" in message:
        bot.send_message(chat_id=chat_id, text="w00F")

    elif "filmi" in message and lotto < 11:
        bot.send_message(chat_id=chat_id, text="Filmi best")


def msg_sticker(bot, update):
    printlog(update, "sticker")
    check_names(update)
    count_and_write(update, "stickers")


def msg_photo(bot, update):
    printlog(update, "photo")
    check_names(update)
    count_and_write(update, "photos")


def msg_gif(bot, update):
    printlog(update, "gif")
    check_names(update)
    count_and_write(update, "gifs")


def stats(bot, update):
    printlog(update, "stats")
    user_id, chat_id = check_names(update)
    count_and_write(update, "commands")

    cursor = chats_collection.aggregate([
        {"$match": {"chat_id": chat_id}},
        {"$project": {"_id": 0, "users": 1}},
        {"$unwind": "$users"},
        {"$replaceRoot": {"newRoot": "$users"}},
        {"$match": {"user_id": user_id}}
    ])
    user = cursor.next()

    user_data = user["count"]

    sticker_percent = "?"
    kiitos_percent = "?"

    if user_data["stickers"] + user_data["messages"] != 0:
        sticker_percent = round(((user_data["stickers"]) / (user_data["stickers"] + user_data["messages"]) * 100), 2)

    if user_data["messages"] != 0:
        kiitos_percent = round(((user_data["kiitos"]) / (user_data["messages"]) * 100), 2)

    msg = "@{}:\nMessages: {}".format(user["username"], user_data["messages"])
    msg += "\nStickers: {} ({}%)".format(user_data["stickers"], sticker_percent)
    msg += "\nKiitos: {} ({}%)".format(user_data["kiitos"], kiitos_percent)
    msg += "\nPhotos: {}".format(user_data["photos"])

    bot.send_message(chat_id=update.message.chat_id, text=msg)


def published(bot, update, text):
    user_id, chat_id = check_names(update)


    
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

    print()


# Lue JSON-tiedosto
def file_read(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            saved_data = json.load(file)
        file.close()
        return saved_data
    except FileNotFoundError:
        print("Oh dog file not found")
        exit(1)


def main():
    updater = Updater(token=settings["tg_token"])
    handlers(updater)

    updater.start_polling()

settings = file_read("settings.json")
sticker_list = file_read("sticker_list_kiitos.json")
protip_list = file_read("tips.json")

# TODO: failaa jos ei saada yhteyttä
db_client = MongoClient("localhost", 27017)
db = db_client[settings["db_name"]]
chats_collection = db[settings["collection_name"]]

main()
