# -*- coding: utf-8 -*-
import json
from urllib.request import urlopen, Request
from urllib.error import URLError
import random
from os import environ
import time
from datetime import datetime

from core.printlog import printlog
from core.count_and_write import count_and_write
from core.get_ids import get_ids
from core.toptenlist import toptenlist
from core.camera_versus_text import camera_versus_text

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import masterlist

class CommandRouter():
    def __init__(self, db):
        self.db = db
        self.last_command = {}

        self.commands = {
            "/start": self.start,
            "/stats": self.stats,
            "/darkroom": self.darkroom,
            "/korona": self.korona,
            "/help": self.help,
            "/noutaja": self.noutaja,
            "/topten": self.topten,
            "/protip": self.protip,
            "/blacklist": self.add_blacklist,
            "/unblacklist": self.remove_blacklist
        }

    def get_commands(self):
        # yllä olevat komennot
        coms = self.commands.keys()

        # poistetaan '/' edestä 
        return [x[1:] for x in coms]

    def route_command(self, bot, update, args=[]):
        message = update.message.text.split(" ")[0]

        #poistetaan '@<BotUsername>' komennosta jos löytyy
        print(message)
        if "@" in message:
            message = message.split("@", 1)[0]

        print(message)

        printlog(update, message)
        count_and_write(self.db, update, "commands")

        if message in self.commands:
            self.commands[message](bot, update, args)


    def on_timeout(self, user_id, chat_id):
        current_time = time.time()

        # privassa saa spämmii
        if user_id == chat_id:
            return False

        if (user_id, chat_id) in self.last_command and self.last_command[(user_id, chat_id)] + 60 > current_time:
            return True
        else:
            self.last_command[(user_id, chat_id)] = current_time
            return False

    def start(self, bot, update, args):
        _, chat_id = get_ids(update) # Ignoraa user_id, tätä käytetään paljon

        bot.send_message(chat_id=chat_id, text="Woof woof")

    def stats(self, bot, update, args):
        user_id, chat_id = get_ids(update)

        if self.on_timeout(user_id, chat_id):
            return

        if self.db.in_blacklist(user_id):
            update.message.reply_text("Markku ei seuraa sinua. Käytä komentoa /unblacklist , jos haluat seurannan käyttöön.\n" \
                                    "Markku does not track you. Use the command /unblacklist to enable tracking.")
            return

        counters = self.db.get_counters()

        user_counters = {}
        counter_sum = 0

        # Haetaan käyttäjän laskurien arvot databaseltä
        for i in counters:
            user_counters[i] = self.db.get_counter_user(user_id, chat_id, i)
            if i != "kiitos":
                counter_sum += user_counters[i]

        # Muodostetaan lähetettävä viesti
        msg = "@{}<code>:".format(update.message.from_user.username)
        msg += "\n{:<10}{:>5}".format("Total:", counter_sum)

        for counter in user_counters:
            if counter == "kiitos":
                if user_counters["messages"] != 0:
                    msg += "\n└ {}% Kiitosta".format(round(user_counters[counter] / user_counters["messages"] * 100, 1) )
                else:
                    msg += "\n└ ??% Kiitosta"


            else:
                msg += "\n{:<10}{:>5} ({:>4}%)".format(counter.capitalize() + ":",
                    user_counters[counter], round(user_counters[counter] / counter_sum * 100, 1) )

        msg += "</code>"
     
        # Lähetetään viesti. parse_mode mahdollistaa html-muotoilun viestissä
        bot.send_message(chat_id=chat_id, text=msg, parse_mode='HTML')

    # Lukee netistä valosensorin datan ja kertoo onko kerhohuoneella valot päällä
    def darkroom(self, bot, update, args):
        user_id, chat_id = get_ids(update)

        if self.on_timeout(user_id, chat_id):
            return
        
        try:
            with urlopen(environ["SENSOR_API_ADDRESS"]) as url:
                sensor_data = json.loads(url.read().decode())

                value_light = 0
                insert_time = ""

                # JSON härössä muodossa, sen takia teemme näin. Esimerkki:
                #   {"entries": [{"value": 191, "sensor": "light1", "inserted": "2018-07-27T16:18:43.589Z"}]}

                if len(sensor_data["entries"]) != 0:
                    for sensor in sensor_data["entries"]:
                        if sensor["sensor"] == "light1":
                            value_light = sensor["value"]
                            insert_time = sensor["inserted"]

                    if value_light > 100:
                        reply = "Joku on pimiöllä :O"
                    else:
                        reply = "Pimiö tyhjä :("

                    # Selvitetään kuinka vanhaa uusin tieto on. Palvelimen data UTC:na, verrataan lokaaliin aikaan.
                    # Tällä toteutuksella lokaalin aikavyöhykkeen ei pitäisi haitata.
                    current_datetime = datetime.now()
                    now_timestamp = time.time()

                    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)

                    inserted_datetime = datetime.strptime(insert_time, "%Y-%m-%dT%H:%M:%S.%fZ") + offset

                    date_diff = current_datetime - inserted_datetime

                    if date_diff.seconds > 3600 and date_diff.days == 0:
                        reply += " ({} tuntia sitten)".format(date_diff.seconds//3600)
                    elif date_diff.days != 0:
                        reply += " ({} päivää ja {} tuntia sitten)".format(date_diff.days, date_diff.seconds//3600)

                else:
                    reply = "Ei tietoa :/"

                bot.send_message(chat_id=chat_id, text=reply)
        except URLError as e:
            print(e.reason)
            bot.send_message(chat_id=chat_id, text="Ei ny onnistunu (%s)" % e.reason)

    def korona(self, bot, update, args):
        user_id, chat_id = get_ids(update)
        try:

            url = "https://w3qa5ydb4l.execute-api.eu-west-1.amazonaws.com/prod/finnishCoronaData"

            with urlopen(url) as response:
                data = json.loads(response.read().decode())

                confirmedCount = len(data["confirmed"])
                deathCount = len(data["deaths"])

                msg = "Tartuntoja Suomessa: {}\n Kuolemia: {}".format(confirmedCount, deathCount)

                bot.send_message(chat_id=chat_id, text=msg)

        except URLError as e:
            print(e.reason)
            bot.send_message(chat_id=chat_id, text="Ei ny onnistunu (%s)" % e.reason)

    def help(self, bot, update, args):
        user_id, chat_id = get_ids(update)

        if self.on_timeout(user_id, chat_id):
            return

        reply = "Komennot:\n" \
                "/darkroom - Kertoo onko joku pimiöllä.\n" \
                "/stats - Chattikohtaiset statsit.\n" \
                "/topten <i>laskuri</i> - Paljastaa chatin spämmibotit.\n"\
                "/noutaja - Postaa satunnaisen noutajakuvan.\n"\
                "/protip - Antaa ammatti valo kuvaus vinkin!\n"\
                "/blacklist - Poistaa lähettäjän datat tietokannasta ja estää uusien tallentamisen.\n"\
                "/unblacklist - Sallii omien tietojen tallentamisen blacklist-komennon jälkeen.\n"\
                "\n" \
                "Botin koodit: @eltsu7, @kulmajaba ja @anttimoi\n" \
                "https://github.com/eltsu7/MarkkuBot\n" \
                "Valosensorit ja siihen koodit: @anttimoi"

        bot.send_message(chat_id=chat_id, text=reply, parse_mode='HTML')            

    def noutaja(self, bot, update, args):
        user_id, chat_id = get_ids(update)

        if self.on_timeout(user_id, chat_id):
            return

        url = "https://dog.ceo/api/breed/retriever/golden/images/random"

        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

        with urlopen(req) as page:
            retriever_data = json.loads(page.read().decode())

            picture_link = retriever_data["message"]

            bot.sendPhoto(chat_id=chat_id, photo=picture_link)

    def topten(self, bot, update, args):
        user_id, chat_id = get_ids(update)

        if self.on_timeout(user_id, chat_id):
            return

        # argumenttejä pitää olla vain yksi. ei errorviestiä koska tätä varmaan painetaan vahingossa usein
        if len(args) != 1:
            return

        # db:ltä käytössä olevat laskurit
        valid_counters = self.db.get_counters()

        # errorviesti jos argumentti ei vastaa laskuria
        if args[0] not in valid_counters:
            counters = ", ".join(valid_counters)
            reply = "Väärä laskurin nimi. Käytettävät laskurit: " + counters + "."
            bot.send_message(chat_id=chat_id, text=reply)

            return

        text = toptenlist(self.db, chat_id, args[0])

        bot.send_message(chat_id=chat_id, text=text)

    def protip(self, bot, update, args):
        user_id, chat_id = get_ids(update)

        if self.on_timeout(user_id, chat_id):
            return

        protip_list = masterlist.tips

        protip_index = random.randint(0, len(protip_list) - 1)

        bot.send_message(chat_id=chat_id, text=protip_list[protip_index])

    def camera_versus(self, bot, update, args):
        _, chat_id = get_ids(update)

        msg = camera_versus_text()
        bot.send_message(chat_id=chat_id, text=msg)

    def add_blacklist(self, bot, update, args):
        user_id, _ = get_ids(update)

        if (update.message.chat.type != "private"):
            update.message.reply_text("Ole hyvä ja lähetä tämä pyyntö yksityisviestillä.\n" \
                                    "Please send this request via private message.")
            return

        
        if self.db.in_blacklist(user_id):
            update.message.reply_text("Tietosi on jo poistettu, eikä sinua seurata.\n" \
                                    "Your information is already deleted and you are not tracked.")
            return

        keyboard = [[InlineKeyboardButton("Ei (No)", callback_data="false"),
                    InlineKeyboardButton("Kyllä (Yes)", callback_data="true")]]

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text("Haluatko, että kaikki henkilöivät tietosi poistetaan Markun tietokannasta," \
                                "ja käyttäjäsi lisätään \"älä seuraa\"-listalle?\n\n" \
                                "Do you want to delete all of your personifiable information from Markku's database" \
                                "and add your user to the \"do not track\" list?",
                                reply_markup=reply_markup)

    def remove_blacklist(self, bot, update, args):
        user_id, _ = get_ids(update)

        if (update.message.chat.type != "private"):
            update.message.reply_text("Ole hyvä ja lähetä tämä pyyntö yksityisviestillä\n" \
                                    "Please send this request via private message")
            return

        if self.db.in_blacklist(user_id):
            
            self.db.remove_blacklist(user_id)
            update.message.reply_text("Markku seuraa sinua taas.\n" \
                                    "Markku is tracking you again.\n\n" \
                                    "*sniff sniff* Woof!")
        else:
            update.message.reply_text("Et ole Markun \"älä seuraa\"-listalla.\n" \
                                    "You are not on Markku's \"do not track\" list.")

    def blacklist_confirm(self, bot, update):
        query = update.callback_query

        username = query.from_user.username
        user_id = query.from_user.id

        print("Type: blacklist_confirm", "\nUsername: ", username)

        if (query.data == "false"):
            bot.edit_message_text(text="Käyttäjätietojen poistaminen peruttu.\n" \
                                    "The deletion of user information has been cancelled.",
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)
            return
        
        bot.edit_message_text(text="Käyttäjätiedot poistettu, ja käyttäjää ei seurata jatkossa.\n" \
                                    "User information deleted, and the user will not be tracked.",
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)

        # Poista kaikki käyttäjän dokumentit
        self.db.add_blacklist(user_id)
