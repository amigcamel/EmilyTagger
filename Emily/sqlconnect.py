from django.conf import settings
import sqlite3
import logging
logger = logging.getLogger(__name__)


class SqlConnect:

    def __init__(self):
        dbpath = settings.DATABASES['default']['NAME']
        self._conn = sqlite3.connect(dbpath)
        self._con.isolation_level = None  # allow autocommit
        self._c = self._conn.cursor()

    def __del__(self):
        self._conn.close()
        logger.debug('Connection closed')

    def close(self):
        self._conn.close()
        logger.debug('Connection closed')

    def commit(self):
        self._conn.commit()
        logger.debug('data committd')


def creaet_tag_columns():
    from senti.ref import senti_ref, senti_ref2
    sc = SqlConnect()
    sc.execute('''CREATE TABLE emilytagger_tags (id integer primary key autoincrement, ch_name text, en_name text, color_code text''')
    tags = [senti_ref, senti_ref2]
    for t in tags:
        for k, v in t.iteritems():
            print k, v


# def create_source():
#     c.execute('''CREATE TABLE emilytagger_posts (id integer primary key autoincrement, source text, senti text, url text, post text)''')


# def make_entry_list():
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     # check if table exists
#     c.execute('''SELECT name FROM sqlite_master WHERE (type='table' AND name='entry_list')''')
#     c.execute('''DROP TABLE IF EXISTS entry_list''')
#     c.execute('''CREATE TABLE entry_list (url, text)''')


# for col in cols:
#     source, senti = col
#     if source == 'yahoo':
#         dbname = 'senti_news'
#     elif source == 'ptt':
#         dbname = 'senti_ptt'
#     posts = list(c[dbname]['%s_%s' % (source, senti)].find())
#     for p in posts:
#         url = p['_id']
#         if url.startswith('/'):
#             url = url[1:]
#         post = p['content']
#         print source, senti, url
#         sc.execute('''INSERT INTO emilytagger_posts VALUES (NULL, ?, ?, ?, ?)''', (source, senti, url, post))

# sc.commit()