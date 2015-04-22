# -*-coding:utf-8 -*-
import sqlite3
from senti.rlite_api import DB_Conn
# from Jseg import jieba
from Jseg.Jieba import Jieba
from django.conf import settings
from os.path import isfile
from itertools import chain
from collections import Counter, OrderedDict, defaultdict
import cPickle
import logging
import json

TAG_PATH = settings.TAG_PATH
DB_PATH = settings.DATABASES['default']['NAME']
SEG_CACHE_NAME = 'seg_res.cpkl'
TARGET_USER = 'emily.lulala@gmail.com'
SUBTAG = 'Emotion'


def add_cues():
    '''add tagged words to jieba's dictionary'''
    logging.debug("add tagged words to jieba's custom dictionary")
    jieba = Jieba()
    dbconn = DB_Conn(TARGET_USER)
    words = dbconn.collect_tagged_words(SUBTAG)
    jieba.add_custom_dic(words)
    return jieba


def seg_posts():
    jieba = add_cues()
    db = sqlite3.connect(DB_PATH)
    c = db.cursor()
    c.execute('SELECT post FROM emilytagger_posts')
    res = c.fetchall()
    posts = (i[0] for i in res)
    seg_res = (jieba.seg(post).raw for post in posts)
    logging.debug('segmenting... this might take a while...')
    seg_res = [[i[0] for i in j] for j in seg_res]
    logging.debug('dumping segmented results...')
    with open(SEG_CACHE_NAME, 'wb') as f:
        cPickle.dump(seg_res, f)


def check_cache():
    if isfile(SEG_CACHE_NAME) is False:
        logging.debug('caching segmented post results...')
        seg_posts()


def read_seg_res():
    check_cache()
    with open(SEG_CACHE_NAME, 'rb') as f:
        return cPickle.load(f)


def get_fdist_all():
    res = read_seg_res()
    return Counter(chain.from_iterable(res))


def calc_freq():
    fdist_all = get_fdist_all()
    uniq, dup = filter_tagged_words()
    lst = []
    for k, v in uniq.iteritems():
        word = k
        cls = v[0]
        freq = fdist_all[k]
        tar = (word, cls, freq)
        lst.append(tar)
        logging.debug(json.dumps(tar, ensure_ascii=False))
    return lst


def build_group_ref():
    db = sqlite3.connect(DB_PATH)
    c = db.cursor()
    c.execute('SELECT source, senti, url FROM emilytagger_posts')
    res = c.fetchall()
    ref = OrderedDict()
    for source, senti, url in res:
        group_name = '%s-%s' % (source, senti)
        if group_name in ref:
            ref[group_name].append(url)
        else:
            ref[group_name] = list()
    return ref


def load_ref(tag='EMOTION', subtag='Emotion'):
    with open(TAG_PATH) as f:
        ref = json.load(f)[tag][subtag]
    fin = dict()
    for num, p in enumerate(ref):
        cls = p[0]
        fin[str(num)] = cls
    return fin


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


if __name__ == '__main__':
    check_cache()
