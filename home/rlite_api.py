# -*-coding:utf8-*-
import hirlite
import simplejson as json
from django.conf import settings
from os.path import join
from itertools import chain
from .sqlconnect import SqlConnect
from itertools import groupby
import logging
logger = logging.getLogger(__name__)


class DB_Conn:

    def __init__(self, user):
        if not user:
            user = 'guest@guest.com'
        logger.info('%s connection to db' % user)
        db_path = join(settings.RLITE_DB_PATH, user)
        self.db = hirlite.Rlite(path=db_path)
        # logger.debug('rlite: Connection established')

    def command(self, *args):
        '''A wrapper for Rlite.db.command which also ensures the input strings are all utf-8'''
        args = [i.encode('utf-8') for i in args]
        return self.db.command(*args)

    def read(self, uid):
        '''read tagged words by uid'''

        res = self.command('get', uid)

        if res:
            res = json.loads(res)
        else:
            res = {}
        return res

    def save(self, uid, cue, value):
        dic = self.command('get', uid)
        if dic:
            dic = json.loads(dic)
        else:
            dic = {}

        dic[cue] = value
        obj = json.dumps(dic)
        logger.debug('obj: ' + str(obj))

        self.command('set', uid, obj)

        logger.debug('UID: %s, CUE: %s, VALUE: %s -- update successfully!' % (uid, cue, value))
        return True

    def remove(self, uid, cue):
        dic = self.read(uid)
        dic.pop(cue)
        obj = json.dumps(dic)
        self.command('set', uid, obj)
        logger.debug('UID: %s, CUE: %s deleted successfully!' % (uid, cue))
        return True

    def collect(self, subtag):
        all_keys = self.command('keys', '*')
        con = []
        for key in all_keys:
            key = key.decode('utf-8')
            if key.split('__')[-1] == subtag:
                value = self.read(key)
                con.append([key, value])
            logger.debug('cursor: ' + key)

        return con

    def collect_tagged_words(self, subtag, with_val=False):
        items = self.collect(subtag)
        wlst = (i[1] for i in items)
        if with_val:
            wlst = (i.items() for i in wlst)
        else:
            wlst = (i.keys() for i in wlst)
        wlst = chain.from_iterable(wlst)
        words = list(set(wlst))
        return words

    @classmethod
    def pack_tagged_words(cls, username):
        client = cls(username)
        keys = client.db.command('keys', '*')
        sql_client = SqlConnect(username)
        res = sql_client.fetch(''' SELECT * FROM tags ''')[0][1]
        ref = json.loads(res)
        ref_dic = {}
        for v in ref.values():
            ref_dic.update(v)
        pairs = [(key.decode('utf8').split('__')[-1], json.loads(client.db.command('get', key))) for key in keys]
        pairs.sort(key=lambda x: x[0])
        output = {}
        for k, g in groupby(pairs, lambda x: x[0]):
            dic = {}
            for gg in g:
                d = gg[1]
                for kk, vv in d.items():
                    dic[kk] = ref_dic[k][vv][0]
            output[k] = dic
        output = json.dumps(output)
        return output


def update(cue, value, text_id, tag, subtag, user):
    value = int(value)
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
