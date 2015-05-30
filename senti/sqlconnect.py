# -*-coding: utf-8 -*-
from django.conf import settings
import sqlite3
import logging
logger = logging.getLogger(__name__)


class SqlConnect:

    def __init__(self, db_name):
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

    def exec(self, cmd, *args):
        self._c.execute(cmd, *args)

    def fetch(self, cmd, *args):
        self.exec(cmd, *args)
        return self._c.fetchall()

    def create_tables(self):
        self.exec('''CREATE TABLE posts (post_id text primary key, page integer, source text, category text, post text)''')
        self.exec('''CREATE TABLE tags (id integer primary key, schema text)''')

    def create_sample_tags(self):
        with open(settings.TAG_PATH) as f:
            ref = f.read()
        self.exec('''INSERT INTO tags VALUES (1, '%s')''' % ref)

    def insert_post(self, post_id, page, source, category, post):
        if len(post.strip()) == 0:
            logger.warning('empty input!')
        else:
            self.exec('''INSERT INTO posts VALUES (?, ?, ?, ?, ?)''', (post_id, page, source, category, post))
