# -*-coding:utf-8 -*-
import sys
sys.path.append('..')

import sqlite3
from senti.rlite_api import DB_Conn
from itertools import chain, groupby
from collections import Counter, OrderedDict, defaultdict
from converter import to_csv, to_excel
from config import LOG_PATH, GFDIST_PATH, POSTS_SEG_PATH, TAG_PATH, DB_PATH, TARGET_USER, TAG, SUBTAG, OUTPUT_PATH
import simplejson as json
import hirlite
import logging


# logging settings
logger_name = 'segmetation_error'
logger = logging.getLogger(logger_name)
LOG_PATH = LOG_PATH % logger_name
fh = logging.FileHandler(LOG_PATH)
fh.setLevel(logging.ERROR)
logger.addHandler(fh)


def filter_tagged_words():
    '''回傳非重複及重複的標記詞'''
    dbconn = DB_Conn(TARGET_USER)
    words = dbconn.collect_tagged_words(SUBTAG, with_val=True)
    dic = defaultdict(list)
    for k, v in words:
        dic[k].append(v)

    uniq, dup = {}, {}

    for k, v in dic.iteritems():
        if len(v) > 1:
            dup[k] = v
        elif len(v) == 1:
            uniq[k] = v

    return uniq, dup


def load_val_ref(tag=TAG, subtag=SUBTAG):
    '''讀取分類名稱與值的對應'''
    with open(TAG_PATH) as f:
        ref = json.load(f)[tag][subtag]
    fin = dict()
    for num, p in enumerate(ref):
        cls = p[0]
        fin[str(num)] = cls
    return fin


def build_cache():
    '''
    1. 將所有文件斷詞並依groupname分類 (gfdist.rld)
    2. 產生所有斷詞結果 (posts_seg.rld)
    '''
    from jseg import multi

    # 收集所有標記詞
    dbconn = DB_Conn(TARGET_USER)
    words = dbconn.collect_tagged_words(SUBTAG)

    # 將標記詞加入guranteed wordlist
    multi.j.add_guaranteed_wordlist(words)

    db = sqlite3.connect(DB_PATH)
    c = db.cursor()
    c.execute('SELECT source, senti, post FROM emilytagger_posts')
    res = c.fetchall()
    res.sort(key=lambda x: (x[0], x[1]))
    rlite = hirlite.Rlite(GFDIST_PATH)
    rlite2 = hirlite.Rlite(POSTS_SEG_PATH)
    for k, g in groupby(res, lambda x: (x[0], x[1])):
        groupname = '%s-%s' % k
        posts = [post for source, senti, post in g]
        posts_seg = multi.seg(posts)

        rlite2.command('set', '%s-%s' % (source, senti), json.dumps([[j[0] for j in i] for i in posts_seg]))

        raws = list(chain.from_iterable(posts_seg))
        toks = [word for word, pos in raws]
        fdist = Counter(toks)
        rlite.command('set', groupname, json.dumps(fdist))


def read_group_fdist(groupname):
    '''依groupname讀取fdist'''
    rlite = hirlite.Rlite(GFDIST_PATH)
    if groupname == 'all':
        keys = rlite.command('keys', '*')
        fdist = Counter({})
        for key in keys:
            sub_fdist = json.loads(rlite.command('get', key))
            fdist += Counter(sub_fdist)
    else:
        fdist = rlite.command('get', groupname)
        fdist = json.loads(fdist)
    return fdist


def calc(groupname):
    '''
    計算詞頻
    '''
    val_ref = load_val_ref()
    fdist = read_group_fdist(groupname)
    tagged_words = collect_tagged_word(groupname)
    con = []
    for word, val in tagged_words:
        freq = fdist.get(word)
        if freq is None or freq == 0:
            logger.error('%s: %s' % (groupname, word))
        else:
            con.append((word, val, freq))
    con.sort(key=lambda x: x[1])

    dic = OrderedDict()
    for k, g in groupby(con, lambda x: x[1]):
        val_name = val_ref[k]
        tar = [(word, freq) for word, val, freq in g]
        tar.sort(key=lambda x: x[1], reverse=True)
        dic[val_name] = tar

    return dic


def build_index_ref_by_group():
    '''
    建立每一個groupname下的index list
    Example -- {'ptt-happy': [...], 'ptt-odd': [...]}
    '''
    db = sqlite3.connect(DB_PATH)
    c = db.cursor()
    c.execute('SELECT source, senti, url FROM emilytagger_posts')
    res = c.fetchall()
    res.sort(key=lambda x: (x[0], x[1]))
    group_ref = OrderedDict()
    for k, g in groupby(res, lambda x: (x[0], x[1])):
        groupname = '%s-%s' % (k[0], k[1])
        group_ref[groupname] = [url for source, senti, url in g]
    return group_ref

    ref = OrderedDict()
    for source, senti, url in res:
        group_name = '%s-%s' % (source, senti)
        if group_name in ref:
            ref[group_name].append(url)
        else:
            ref[group_name] = list()
            ref[group_name].append(url)
    return ref


def collect_tagged_word(groupname, subtag=SUBTAG):
    '''依groupname收集所有標記詞'''
    index_ref = build_index_ref_by_group()
    if groupname == 'all':
        indexes = chain.from_iterable(index_ref.values())
    else:
        indexes = index_ref[groupname]
    dbconn = DB_Conn(TARGET_USER)
    con = []
    for index in indexes:
        uid = '%s__%s' % (index, subtag)
        tagged_words = dbconn.read(uid)
        con.append(tagged_words.items())
    con = list(set(chain.from_iterable(con)))
    return con


def wrapper():
    groupnames = build_index_ref_by_group().keys()  # This function is used for borrowing purpose to get group names
    groupnames.insert(0, 'all')
    for groupname in groupnames:
        logger.debug('processing %s' % groupname)
        dic = calc(groupname)
        rows = []
        for title, body in dic.iteritems():
            body = [u'"%s"-%d次' % (word, freq) for word, freq in body]
            rows.append([title] + body)

        to_excel(rows, groupname, 'senti')
        to_csv(rows, groupname)


if __name__ == '__main__':
    from os.path import join, isfile
    import os
    afs = os.listdir(OUTPUT_PATH)
    for f in afs:
        logger.debug("deleting %s" % f)
        f = join(OUTPUT_PATH, f)
        if isfile(f):
            os.remove(f)
    wrapper()

    # output lexicons with and without duplicates
    logger.debug('generating lex_dup and lex_uniq')
    u, d = filter_tagged_words()
    tmp = [('lex_uniq', u), ('lex_dup', d)]
    val_ref = load_val_ref()
    for name, rows in tmp:
        con = []
        for word, vals in rows.items():
            vals = ', '.join([val_ref[val] for val in vals])
            con.append((word, vals))
        to_csv(con, name)
        to_excel(zip(*con), name, 'senti')
