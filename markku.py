# coding=UTF-8

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, BaseFilter
import logging, json

# Enables logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


'''TELEGRAM KAMAA'''


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Woof woof motherfucker")
	
	
def darkroom(bot, update):
	# Pimiöjutut
	
    
def handlers(updater):
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('pimiö', darkroom))
    

'''MUUTA KAMAA'''


def file_read(filename):
    # Reads a json file

    try:
        with open(filename, 'r') as file:
            data = json.load(file)
        file.close()
        return data
    except FileNotFoundError:
        print("Oh dog file not found")
        exit(1)


def file_write(filename):
    # Writes a json file

    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)
    file.close()


def main():
    updater = Updater(token='527366541:AAG3x6KeR4KDhvEa6zlO8Cszia5cMfwMXiI')
    handlers(updater)

    updater.start_polling()

data = file_read("data.json")
main()


