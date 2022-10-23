from core.get_ids import get_ids
from collections import Counter
import re

# TODO collection


def parse_and_count(db, update):
    user_id, chat_id = get_ids(update)

    # Älä laske blacklistattuja
    if db.in_blacklist(user_id):
        return

    text = update.message.text.upper()

    # usernameksi laitetaan 'Not found' jos sitä ei ole
    username = "Not found"
    if update.message.from_user.username is not None:
        username = update.message.from_user.username

    # chat titleksi laitetaan 'Private' jos sitä ei ole (priva chätti)
    chat_title = "Private"
    if update.message.chat.title is not None:
        chat_title = update.message.chat.title

    # muuttaa kaikki paitsi kirjaimet ja numerot välilyönneiksi
    parsed_text = re.sub("[^a-zA-Z0-9 öÖäÄ\n]", " ", text)

    # splittaa välilyöntien kohdalta
    split_text = parsed_text.split(" ")

    # poistaa listasta yhden ja nollan pituiset alkiot
    split_text = [i for i in split_text if len(i) > 1]

    # laskee listasta sanat ja tallentaa sen muotoon {"sana1": sanaMäärä1, "sana2": sanaMäärä2 ... }
    wordCount = Counter(split_text)

    # lisätään sanat db:n sanacountteriin
    for word in wordCount:
        db.word_collection_add(user_id, chat_id, word, wordCount[word])
