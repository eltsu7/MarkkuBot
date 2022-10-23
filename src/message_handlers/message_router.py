import random

from src.core.printlog import printlog
from src.core.get_ids import get_ids
from src.core.count_and_write import count_and_write
from src.core.parse_and_count import parse_and_count
import src.masterlist as masterlist


class MessageRouter:
    def __init__(self, db):
        self.db = db

        self.commands = {
            "msg_sticker": self.msg_sticker,
            "msg_text": self.msg_text,
            "msg_photo": self.msg_photo,
            "msg_gif": self.msg_gif,
        }

    def route_command(self, bot, update, command, args):
        printlog(update, command)

        username = update.message.from_user.username
        chat_title = update.message.chat.title
        user_id, chat_id = get_ids(update)

        if username is not None:
            self.db.update_name(user_id, username)

        if chat_title is not None:
            self.db.update_name(chat_id, chat_title)

        if command in self.commands:
            self.commands[command](bot, update)

    def msg_text(self, bot, update):
        _, chat_id = get_ids(update)
        count_and_write(self.db, update, "messages")

        sticker_list = masterlist.stickers
        message = update.message.text.lower()

        parse_and_count(self.db, update)

        lotto = random.random()

        if "kiitos" in message:
            count_and_write(self.db, update, "kiitos")

            if lotto < 0.05:  # 5%
                update.message.reply_text("Kiitos")
            elif lotto < 0.06:  # 1%
                sticker_index = random.randint(0, len(sticker_list) - 1)
                bot.send_sticker(chat_id=chat_id, sticker=sticker_list[sticker_index])

            elif lotto < 0.07:  # 1%
                update.message.reply_text("Ole hyvä")

        elif "markku" in message and "istu" in message:
            if lotto < 0.05:  # 5%
                bot.send_message(chat_id=chat_id, text="*paskoo lattialle*")
            else:
                bot.send_message(chat_id=chat_id, text="*istuu*")

        elif "huono markku" in message:
            bot.send_message(chat_id=chat_id, text="w00F")

        elif "markku perkele" in message:
            bot.send_message(chat_id=chat_id, text="woof?")

        elif "filmi" in message and lotto < 0.05:  # 5%
            bot.send_message(chat_id=chat_id, text="Filmi best")

    def msg_gif(self, bot, update):
        count_and_write(self.db, update, "gifs")

    def msg_photo(self, bot, update):
        count_and_write(self.db, update, "photos")

    def msg_sticker(self, bot, update):
        count_and_write(self.db, update, "stickers")
