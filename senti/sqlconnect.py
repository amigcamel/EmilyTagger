# -*-coding: utf-8 -*-
from django.conf import settings
import sqlite3
import time
import logging
logger = logging.getLogger(__name__)


class SqlConnect:

    def __init__(self, db_name):
        # if db_name is None:
        #     dbpath = settings.DATABASES['default']['NAME']
        if not db_name:
            db_name = 'guest@guest.com'

        dbpath = settings.USER_DB_PATH % db_name
        logger.info('dbpath: %s' % dbpath)
        self._conn = sqlite3.connect(dbpath)
        self._conn.isolation_level = None  # allow autocommit
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

    def create_tables(self):
        self._c.execute('''CREATE TABLE posts (id integer primary key autoincrement, source text, senti text, url text, post text)''')
        self._c.execute('''CREATE TABLE tags (id integer primary key, schema text)''')

    def create_sample_tags(self):
        with open(settings.TAG_PATH) as f:
            ref = f.read()
        self._c.execute('''INSERT INTO tags VALUES (1, '%s')''' % ref)

    def insert_post(self, text):
        if len(text.strip()) == 0:
            logger.warning('empty input!')
        else:
            self._c.execute('''INSERT INTO posts VALUES (null, 'test', 'test', ?, ?)''', (str(time.time()), text))


if __name__ == '__main__':
    sc = SqlConnect('amigcamel@gmail.com')
