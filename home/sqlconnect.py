# -*-coding: utf-8 -*-
from django.conf import settings
from datetime import datetime
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
        # logger.debug('Connection closed')

    def exec(self, cmd, *args):
        self._c.execute(cmd, *args)

    def fetch(self, cmd, *args):
        self.exec(cmd, *args)
        return self._c.fetchall()

    def create_tables(self):
        self.exec('''CREATE TABLE posts (post_id TEXT PRIMARY KEY, page INTEGER, title TEXT, source TEXT, category TEXT, post TEXT, upload_time DATE)''')
        self.exec('''CREATE TABLE tags (id INTEGER PRIMARY KEY, schema TEXT)''')

    def create_sample_tags(self):
        with open(settings.TAG_PATH) as f:
            ref = f.read()
        self.exec('''INSERT INTO tags VALUES (1, '%s')''' % ref)

    def insert_post(self, title, source, category, post, post_id):
        if len(post.strip()) == 0:
            logger.warning('empty input!')
        else:
            page = self.fetch('''SELECT MAX(page) FROM posts''')[0][0]
            if page is None:
                page = 1
            else:
                page += 1
            now = datetime.now().replace(microsecond=0)
            self.exec('''INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?, ?)''', (post_id, page, title, source, category, post, str(now)))

    def hide_post(self, post_id):
        self.exec('''UPDATE posts SET page=-1 WHERE (post_id=?)''', (post_id, ))
        logger.debug('Post hid: %s' % post_id)
        self.reorder()

    def delete_all_posts(self):
        self.exec('''DELETE FROM posts''')

    def reorder(self):
        pages = self.fetch('''SELECT page FROM posts WHERE (page!=-1)''')
        pages = sorted(i[0] for i in pages)
        for num, page in enumerate(pages, 1):
            self.exec('''UPDATE posts SET page=? WHERE (page=?)''', (num, page))
        logger.debug('Done reordering')

    @classmethod
    def pack_source_text(cls, username):
        client = cls(username)
        res = client.fetch(''' SELECT post FROM posts ''')
        posts = []
        for i in res:
            post = i[0]
            # the following part is only a workaround
            # need more debugging!
            try:
                post = post.decode('utf-8')
            except:
                pass
            posts.append(post)
        return posts
