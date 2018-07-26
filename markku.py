# coding: utf-8

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, BaseFilter
import logging
import json
from urllib.request import Request, urlopen
import random
from pymongo import ASCENDING, MongoClient

# Loggaus
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# TODO: var -> jotkut vakiomuuttujat tähän

def start(bot, update):
    printlog(update, "start")

    _, chat_id = get_ids(update) # Ignoraa user_id, tätä käytetään paljon
    count_and_write(update, "commands")

    bot.send_message(chat_id=chat_id, text="Woof woof")


def thiskillsthemarkku(bot, update):
    printlog(update, "kill")

    db_client.close()

    exit()


def darkroom(bot, update):
    printlog(update, "darkroom")

    _, chat_id = get_ids(update)
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

        bot.send_message(chat_id=chat_id, text=reply)


def help(bot, update):
    printlog(update, "help")

    _, chat_id = get_ids(update)
    count_and_write(update, "commands")

    reply = "Komennot:\n" \
            "/darkroom - Kertoo onko joku pimiöllä\n" \
            "/stats - Chattikohtaiset statsit\n" \
            "/toptenmsg - Chatin kovimmat viestittelijät\n"\
            "/toptenkiitos - Chatin kovimmat kiitostelijat\n"\
            "/noutaja - Postaa satunnaisen noutajakuvan\n"\
            "\n" \
            "Botin koodit: @eltsu7 ja @kulmajaba\n" \
            "Valosensorit ja siihen koodit: @anttimoi"

    bot.send_message(chat_id=chat_id, text=reply)


# Palauta updatesta user_id ja chat_id
def get_ids(update):
    # priva-chateissa chat id == user id
    # TG API dokkareissa ei mainita kenttää from_user, mut se toimii joten ¯\_(ツ)_/¯
    # oikee kenttä olis message.from.id mutta python vetää herneen nenään
    return update.message.from_user.id, update.message.chat.id


def count_and_write(update, var):
    user_id, chat_id = get_ids(update)

    # TODO: siirrä setOnInsertin sisälle
    # TODO: tsekkaa onko nimi Not Found, tsekkaa onko käyttäjänimi muuttunu järkeväks, jos on niin päivitä
    username = "Not found"
    if update.message.from_user.username is not None:
        username = update.message.from_user.username

    # countIncrementer kertoo $inc-operaattorille, mitä kasvatetaan ja kuinka paljon.
    # Jos kenttää ei löydy, $inc luo sen samalla numeroarvolla
    countIncrementer = {
        "count.messages": 0,
        "count.stickers": 0,
        "count.photos": 0,
        "count.gifs": 0,
        "count.commands": 0,
        "count.kiitos": 0
    }
    countIncrementer["count." + var] = 1
    
    # Update_one päivittää yhden dokumentin, eli yhden käyttäjän yhdessä chatissa.
    # Boolean lopussa on upsert-parametri, = jos queryn mätsäävää dokumenttia ei löydy, se luodaan.
    # SetOnInsert kertoo mitä muita kenttiä tehdään, jos luodaan uusi dokumentti
    chats_collection.update_one(
        { "chat_id": chat_id, "user_id": user_id },
        { 
            "$inc": countIncrementer,
            "$setOnInsert": {
                "chat_title": update.message.chat.title,
                "username": username,
            }
        },
        True
    )

    # Luo compound index (voidaan käyttää vain toisella tai molemmilla parametreilla)
    chats_collection.create_index([
        ("chat_id", ASCENDING),
        ("user_id", ASCENDING)
    ], unique=True)


def toptenlist(chat_id, var):
    cursor = chats_collection.aggregate([
        { "$match": { "chat_id": chat_id }},
        { "$project": { "_id": 0, "username": 1, "count": "$count." + var }},
        { "$sort": { "count": -1 }},
        { "$limit": 10 }
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

    _, chat_id = get_ids(update)
    count_and_write(update, "commands")

    list, number = toptenlist(chat_id, "messages")

    text = "Top " + str(number) + " viestittelijät:\n" + list

    bot.send_message(chat_id=chat_id, text=text)


def topten_kiitos(bot, update):
    printlog(update, "toptenkiitos")

    _, chat_id = get_ids(update)
    count_and_write(update, "commands")

    list, number = toptenlist(chat_id, "kiitos")

    text = "Top " + str(number) + " kiitostelijat:\n" + list

    bot.send_message(chat_id=chat_id, text=text)


def noutaja(bot, update):
    printlog(update, "noutaja")

    _, chat_id = get_ids(update)
    count_and_write(update, "commands")

    url = "https://dog.ceo/api/breed/retriever/golden/images/random"

    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

    with urlopen(req) as page:
        retriever_data = json.loads(page.read().decode())

        picture_link = retriever_data["message"]

        bot.sendPhoto(chat_id=chat_id, photo=picture_link)


def protip(bot, update):
    printlog(update, "protip")

    _, chat_id = get_ids(update)
    count_and_write(update, "commands")

    protip_index = random.randint(0, len(protip_list) - 1)

    bot.send_message(chat_id=chat_id, text=protip_list[protip_index])


def msg_text(bot, update):
    printlog(update, "text")

    _, chat_id = get_ids(update)
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

    count_and_write(update, "stickers")


def msg_photo(bot, update):
    printlog(update, "photo")

    count_and_write(update, "photos")


def msg_gif(bot, update):
    printlog(update, "gif")

    count_and_write(update, "gifs")


def stats(bot, update):
    printlog(update, "stats")

    user_id, chat_id = get_ids(update)
    count_and_write(update, "commands")

    user = chats_collection.find_one({ "chat_id": chat_id, "user_id": user_id })

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

    bot.send_message(chat_id=chat_id, text=msg)

    
def handlers(updater):
    dp = updater.dispatcher

    # Tässä alla oleville komennoille (esim darkroom) annetaan aina bot ja updater argumenteiksi
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('darkroom', darkroom))
    dp.add_handler(CommandHandler('stats', stats))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('noutaja', noutaja))
    dp.add_handler(CommandHandler('toptenmsg', topten_messages))
    dp.add_handler(CommandHandler('toptenkiitos', topten_kiitos))
    dp.add_handler(CommandHandler('protip', protip))
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
db_client = MongoClient("localhost", 27017, serverSelectionTimeoutMS=1000)
db = db_client[settings["db_name"]]
chats_collection = db[settings["collection_name"]]

main()
