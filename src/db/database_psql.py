import sys
from os import environ  
from collections import Counter
import psycopg2

class DatabasePsql:
    def __init__(self):
        db_name = environ["PSQL_DBNAME"]
        db_user = environ["PSQL_USER"]
        db_pass = environ["PSQL_PASS"]
        db_host = environ["PSQL_HOST"]
        db_port = environ["PSQL_PORT"]
        self.table_name =       environ["PSQL_TABLE_NAME"]
        self.table_counter =    environ["PSQL_TABLE_COUNTER"]
        self.table_word =       environ["PSQL_TABLE_WORD"]
        self.table_blacklist =  environ["PSQL_TABLE_BLACKLIST"]

        self.conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_pass,
            host=db_host,
            port=db_port
        )

        self.cursor = self.conn.cursor()

        # luodaan tarvittavat taulut jos niitä ei ole
        markkuschema = open("markku.sql", "r")
        self.cursor.execute(markkuschema.read())

        self.counters = [
            "messages",
            "kiitos",
            "stickers",
            "photos",
            "gifs",
            "commands",
        ]

    def get_counters(self):
        return self.counters


    def in_blacklist(self, user_id):
        sql =   "SELECT 1 " \
                "FROM {} " \
                "WHERE user_id = {};"

        self.cursor.execute(sql.format(self.table_blacklist, user_id))

        return self.cursor.fetchone() is not None


    def update_name(self, id, name):
        sql =   "INSERT INTO {0} (id, name) " \
                "VALUES ({1}, '{2}') " \
                "ON CONFLICT (id) DO UPDATE " \
                "SET name = '{2}';"        

        self.cursor.execute(sql.format(self.table_name, id, name))

        self.conn.commit()


    def add_blacklist(self, user_id):
        sql =   "INSERT INTO {0} " \
                "VALUES ({4});" \
                " " \
                "DELETE FROM {1} " \
                "WHERE id={4}; " \
                "DELETE FROM {2} " \
                "WHERE user_id={4}; " \
                "DELETE FROM {3} " \
                "WHERE user_id={4}; " \
        
        self.cursor.execute(sql.format(self.table_blacklist, self.table_name, self.table_counter, self.table_word, user_id))

        self.conn.commit()


    def remove_blacklist(self, user_id):
        sql =   "DELETE from {} " \
                "WHERE user_id = {};"

        self.cursor.execute(sql.format(self.table_blacklist, user_id))
        self.conn.commit()


    def increment_counter(self, user_id, chat_id, counter, amount):
        # inkrementoidaan, jossei riviä ole, lisätään se

        sql =   "INSERT INTO {0} (user_id, chat_id, {1}) " \
                "VALUES ({2}, {3}, {4}) " \
                "ON CONFLICT (user_id, chat_id) DO UPDATE " \
                "SET {1} = {0}.{1} + {4};"

        self.cursor.execute(sql.format(self.table_counter, counter, user_id, chat_id, amount))
        self.conn.commit()


    def get_counter_user(self, user_id, chat_id, counter):
        # palauttaa käyttäjä, chätti parin laskurin

        sql =   "SELECT {} " \
                "FROM {} " \
                "WHERE user_id = {} AND chat_id = {};"

        self.cursor.execute(sql.format(counter, self.table_counter, user_id, chat_id))
        
        return self.cursor.fetchone()[0]


    def get_counter_top(self, chat_id, counter, top_amount):
        # nimitaulusta nimet, countterista laskurin arvo
        # kursori antaa ne tupleina -> muutetaan dictiin ja palautetaan

        sql =   "SELECT {0}.{2}, {1}.name " \
                "FROM {0} " \
                "INNER JOIN {1} " \
                "ON {0}.user_id = {1}.id " \
                "WHERE {0}.chat_id={3} " \
                "AND {0}.{2}!=0 " \
                "ORDER BY {0}.{2} DESC " \
                "LIMIT {4};"

        self.cursor.execute(sql.format(self.table_counter, self.table_name, counter, chat_id, top_amount))

        res = self.cursor.fetchall()

        return dict((y, x) for x, y in res)

        
    def word_collection_add(self, user_id, chat_id, word, amount):
        # user, chat, sana yhdistelmät uniikkeja
        # jos ei löydy -> lisätään, jos löytyy, lisätään amount counttiin

        sql =   "INSERT INTO {0} (user_id, chat_id, word, count) " \
                "VALUES ({1}, {2}, '{3}', {4}) " \
                "ON CONFLICT (user_id, chat_id, word) DO UPDATE " \
                "SET count = {0}.count + {4}; "

        self.cursor.execute(sql.format(self.table_word, user_id, chat_id, word, amount))
        self.conn.commit()


    def word_collection_get_chat(self, chat_id):
        # TODO tätä ei käytetä vielä missään, en tiedä miten pitäisi tehdä

        sql = "select * from word where chat_id = {};"
        self.cursor.execute(sql.format(chat_id))

        return self.cursor.fetchall()


    def word_collection_get_chat_user(self, chat_id, user_id):
        pass

if __name__ == "__main__":
    asd = DatabasePsql()
