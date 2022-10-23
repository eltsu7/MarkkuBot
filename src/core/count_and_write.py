# -*- coding: utf-8 -*-

from core.get_ids import get_ids

# TODO collection


def count_and_write(db, update, var):
    user_id, chat_id = get_ids(update)

    # TODO: tsekkaa onko nimi Not Found, tsekkaa onko käyttäjänimi muuttunu järkeväks, jos on niin päivitä
    username = "Not found"
    if update.message.from_user.username is not None:
        username = update.message.from_user.username

    # Älä laske blacklistattuja
    if db.in_blacklist(user_id):
        return

    db.increment_counter(user_id, chat_id, var, 1)
