import sys
from os import environ
from collections import Counter
import psycopg2


class DatabasePsql:
    def __init__(self):
        self.counters = [
            "messages",
            "kiitos",
            "stickers",
            "photos",
            "gifs",
            "commands",
        ]

    def open_connection(self):
        db_name = environ["POSTGRES_DB"]
        db_user = environ["POSTGRES_USER"]
        db_pass = environ["POSTGRES_PASSWORD"]
        db_host = environ["POSTGRES_HOST"]
        db_port = environ["POSTGRES_PORT"]

        self.table_name = environ["POSTGRES_TABLE_NAME"]
        self.table_counter = environ["POSTGRES_TABLE_COUNTER"]
        self.table_word = environ["POSTGRES_TABLE_WORD"]
        self.table_blacklist = environ["POSTGRES_TABLE_BLACKLIST"]

        try:
            conn = psycopg2.connect(
                dbname=db_name,
                user=db_user,
                password=db_pass,
                host=db_host,
                port=db_port,
            )
        except psycopg2.Error as e:
            print("DB error: " + str(e))
            return False

        return conn

    def get_counters(self):
        return self.counters

    def in_blacklist(self, user_id):
        conn = self.open_connection()
        if conn == False:
            return False

        cursor = conn.cursor()

        sql = "SELECT 1 " "FROM {} " "WHERE user_id = {};"

        cursor.execute(sql.format(self.table_blacklist, user_id))

        blacklisted = cursor.fetchone() is not None

        conn.close()

        return blacklisted

    def update_name(self, id, name):
        conn = self.open_connection()
        if conn == False:
            return

        cursor = conn.cursor()

        sql = (
            "INSERT INTO {0} (id, name) "
            "VALUES ({1}, '{2}') "
            "ON CONFLICT (id) DO UPDATE "
            "SET name = '{2}';"
        )

        cursor.execute(sql.format(self.table_name, id, name))

        print(self.table_name, id, name)
        conn.commit()

    def add_blacklist(self, user_id):
        conn = self.open_connection()
        if conn == False:
            return

        cursor = conn.cursor()

        sql = (
            "INSERT INTO {0} "
            "VALUES ({4});"
            " "
            "DELETE FROM {1} "
            "WHERE id={4}; "
            "DELETE FROM {2} "
            "WHERE user_id={4}; "
            "DELETE FROM {3} "
            "WHERE user_id={4}; "
        )
        cursor.execute(
            sql.format(
                self.table_blacklist,
                self.table_name,
                self.table_counter,
                self.table_word,
                user_id,
            )
        )

        conn.commit()
        conn.close()

    def remove_blacklist(self, user_id):
        conn = self.open_connection()
        if conn == False:
            return

        cursor = conn.cursor()

        sql = "DELETE from {} " "WHERE user_id = {};"

        cursor.execute(sql.format(self.table_blacklist, user_id))
        conn.commit()
        conn.close()

    # inkrementoidaan. Jossei riviä ole, lisätään se
    def increment_counter(self, user_id, chat_id, counter, amount):
        conn = self.open_connection()
        if conn == False:
            return

        cursor = conn.cursor()

        sql = (
            "INSERT INTO {0} (user_id, chat_id, {1}) "
            "VALUES ({2}, {3}, {4}) "
            "ON CONFLICT (user_id, chat_id) DO UPDATE "
            "SET {1} = {0}.{1} + {4};"
        )

        cursor.execute(
            sql.format(self.table_counter, counter, user_id, chat_id, amount)
        )
        conn.commit()
        conn.close()

    # palauttaa käyttäjä, chätti parin laskurin
    def get_counter_user(self, user_id, chat_id, counter):
        conn = self.open_connection()
        if conn == False:
            return

        cursor = conn.cursor()

        sql = "SELECT {} " "FROM {} " "WHERE user_id = {} AND chat_id = {};"

        cursor.execute(sql.format(counter, self.table_counter, user_id, chat_id))

        pari = cursor.fetchone()[0]

        conn.close()

        return pari

    # nimitaulusta nimet, countterista laskurin arvo
    # kursori antaa ne tupleina -> muutetaan dictiin ja palautetaan
    def get_counter_top(self, chat_id, counter, top_amount):
        conn = self.open_connection()
        if conn == False:
            return

        cursor = conn.cursor()

        sql = (
            "SELECT {0}.{2}, {1}.name "
            "FROM {0} "
            "INNER JOIN {1} "
            "ON {0}.user_id = {1}.id "
            "WHERE {0}.chat_id={3} "
            "AND {0}.{2}!=0 "
            "ORDER BY {0}.{2} DESC "
            "LIMIT {4};"
        )

        cursor.execute(
            sql.format(
                self.table_counter, self.table_name, counter, chat_id, top_amount
            )
        )

        res = cursor.fetchall()

        conn.close()

        return dict((y, x) for x, y in res)

    # user, chat, sana yhdistelmät uniikkeja
    # jos ei löydy -> lisätään, jos löytyy, lisätään amount counttiin
    def word_collection_add(self, user_id, chat_id, word, amount):
        conn = self.open_connection()
        if conn == False:
            return

        cursor = conn.cursor()

        sql = (
            "INSERT INTO {0} (user_id, chat_id, word, count) "
            "VALUES ({1}, {2}, '{3}', {4}) "
            "ON CONFLICT (user_id, chat_id, word) DO UPDATE "
            "SET count = {0}.count + {4}; "
        )

        cursor.execute(sql.format(self.table_word, user_id, chat_id, word, amount))
        conn.commit()
        conn.close()


if __name__ == "__main__":
    asd = DatabasePsql()
