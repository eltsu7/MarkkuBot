def toptenlist(db, chat_id, var):
    toptenlist_sorted = db.get_counter_top(chat_id, var, 10)

    text = ""
    lista = ""
    number = 1

    # Dicti järjestyksessä joten jos eka on 0 --> kaikki on 0.

    for user, value in toptenlist_sorted.items():
        if number == 1 and value == 0:
            return "'{}'-laskuri on kaikilla tyhjä.".format(var)

        lista += str(number) + ". " + user + ": " + str(value) + "\n"
        number += 1

    text = "Top {} laskurissa {}:\n{}".format(len(toptenlist_sorted), var, lista)

    return text
