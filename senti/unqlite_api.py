# -*-coding:utf8-*-
from unqlite import UnQLite
import json
import logging
from django.conf import settings
from os.path import join
import traceback

logger = logging.getLogger(__name__)


class DB_Conn:

    def __init__(self, user):
        if not user:
            user = 'guest@guest.com'
        logger.info(user)
        user = user.encode('utf8')
        db_path = join(settings.UNQLITE_DB_PATH, user)
        self.db = UnQLite(db_path)
        logger.debug('UnQLite: Connection established')

    def __del__(self):
        self.db.close()
        logger.debug('UnQLite: Connection closed')

    def read(self, uid):
        uid = ensure_utf8(uid)
        # uid = uid.encode('utf8')
        if self.db.exists(uid):
            res = self.db[uid]
            res = json.loads(res)
        else:
            res = {}
        return res

    def save(self, uid, cue, value):
        has_key = self.db.exists(uid)
        if has_key:
            dic = json.loads(self.db[uid])
        else:
            dic = {}
        logger.debug('has_key: ' + str(has_key))

        dic[cue] = value
        obj = json.dumps(dic)
        logger.debug('obj: ' + str(obj))

        retry_time = 0
        while True:
            if retry_time == 50:
                raise Exception('Aji: Unknown error!!!!!!')
            else:
                try:
                    res = self.db.store(uid, obj)
                    if not res:
                        logger.error('Cannot store VALUE "%s" with KEY "%s"' % (obj, uid))
                    logger.debug('UID: %s, CUE: %s, VALUE: %s -- update successfully!' % (uid, cue, value))
                    return res
                except:
                    logger.critical(traceback.format_exc())
                    logger.critical('retry times: %d' % retry_time)
                    retry_time += 1

    def remove(self, uid, cue):
        dic = self.read(uid)
        cue = ensure_unicode(cue)
        dic.pop(cue)
        obj = json.dumps(dic)
        res = self.db.store(uid, obj)
        if not res:
            logger.error('Cannot store VALUE "%s" with KEY "%s"' % (obj, uid))
        logger.debug('UID: %s, CUE: %s deleted successfully!' % (uid, cue.encode('utf8')))
        return res

    def collect(self, subtag):
        cursor = self.db.cursor()
        cursor.reset()

        con = []

        key = cursor.key()
        if key.split('__')[-1] == subtag:
            con.append([key, cursor.value()])

        while True:
            try:
                cursor.next()
                key = cursor.key()
                if key.split('__')[-1] == subtag:
                    con.append([key, cursor.value()])
                logger.debug('cursor: ' + cursor.key())
            except StopIteration:
                break
        return con


def update(cue, value, text_id, tag, subtag, user):
    uid = '%s__%s' % (text_id, subtag)
    conn = DB_Conn(user)
    res = conn.save(uid, cue, value)
    return res


def read_pairs(text_id, tag, subtag, user):
    uid = '%s__%s' % (text_id, subtag)
    conn = DB_Conn(user)
    res = conn.read(uid)
    return res


def remove_cue(text_id, tag, subtag, cue, user):
    uid = '%s__%s' % (text_id, subtag)
    conn = DB_Conn(user)
    res = conn.remove(uid, cue)
    return res


def ensure_utf8(string):
    try:
        string.decode('utf8')
    except:
        if isinstance(string, unicode):
            string = string.encode('utf8')
        else:
            raise ValueError('string cannot be converted to utf8')
    finally:
        return string


def ensure_unicode(string):
    if not isinstance(string, unicode):
        try:
            string = string.decode('utf8')
        except:
            raise ValueError('string cannot be converted to unicode')
    return string

# UnQLite
# DB will be locked when in used
# use read in save
