# -*- coding: utf-8 -*-


# Palauta updatesta user_id ja chat_id
def get_ids(update):
    # priva-chateissa chat id == user id
    # TG API dokkareissa ei mainita kenttää from_user, mut se toimii joten ¯\_(ツ)_/¯
    # oikee kenttä olis message.from.id mutta python vetää herneen nenään
    return update.message.from_user.id, update.message.chat.id
