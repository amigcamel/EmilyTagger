# -*-coding:utf-8-*-
from itertools import chain
from config import POS_PATH, NEG_PATH, COMBINED_LEX, OUTPUT_LEX, POSTS_SEG_PATH, TARGET_USER, SUBTAG, LOG_PATH
from senti.rlite_api import DB_Conn
from collections import Counter
from itertools import groupby
from analysis import filter_tagged_words, load_val_ref
from converter import to_excel, to_csv
import csv
import hirlite
import simplejson as json
import multiprocessing
import numpy
import logging


# logging settings
logger_name = 'span_error'
logger2 = logging.getLogger(logger_name)
LOG_PATH = LOG_PATH % logger_name
fh = logging.FileHandler(LOG_PATH)
fh.setLevel(logging.ERROR)
logger2.addHandler(fh)


def _txt_to_list(path, spliter='\r\n'):
    with open(path) as f:
        raw = f.read()
        lst = raw.split(spliter)
        lst = filter(None, lst)
        lst = set(lst)
        lst = [i.decode('utf-8') for i in lst]
    return lst


def _csv_to_list(path):
    with open(path) as f:
        raw = csv.reader(f)
        lst = list(raw)
    return lst


def build_emolex_counter():
    '''讀取正/負情緒詞表'''
    pos, neg = [_txt_to_list(f) for f in (POS_PATH, NEG_PATH)]
    return Counter(pos), Counter(neg)


def load_senti_wordlist():
    '''讀取基本情緒詞表'''
    combined_lex = _csv_to_list(COMBINED_LEX)
    combined_lex.pop(0)
    output_lex = _csv_to_list(OUTPUT_LEX)
    output_lex = zip(*output_lex)
    merged_lst = combined_lex + output_lex
    merged_list = chain.from_iterable(merged_lst)
    merged_list = filter(None, merged_list)
    merged_list = set(merged_list)
    merged_list = [i.decode('utf-8') for i in merged_list]
    return merged_list


def load_posts_seg():
    '''讀取已分詞的posts'''
    rlite = hirlite.Rlite(POSTS_SEG_PATH)
    keys = rlite.command('keys', '*')
    keys.insert(0, 'mget')
    posts_seg = rlite.command(*keys)
    posts_seg = [json.loads(i) for i in posts_seg]
    posts_seg = reduce(lambda x, y: x+y, posts_seg)
    return posts_seg


def build_target_emolex():
    dbconn = DB_Conn(TARGET_USER)
    words = dbconn.collect_tagged_words(SUBTAG)
    senti_wordlis = load_senti_wordlist()
    target = set(words) - set(senti_wordlis)
    return list(target)


def extract_sentence(post, span=10):
    global target_emolex
    global pos
    global neg
    pid = multiprocessing.current_process().pid
    logger2.debug(pid)
    ovl = set(target_emolex) & set(post)
    post = numpy.array(post)
    post_len = len(post)

    con = []

    for o in ovl:
        idxs = numpy.where(post == o)[0]
        for idx in idxs:
            tar_word = post[idx]
            right_bound = idx + span
            if right_bound >= post_len:
                logger2.warning('right_bound smaller than %d' % span)
                logger2.error('%s' % tar_word)
                break
            pos_cnt, neg_cnt = 0, 0
            while True:
                if idx <= right_bound:
                    pos_count = pos.get(post[idx])
                    if pos_count is None:
                        neg_count = neg.get(post[idx])
                        if neg_count is None:
                            pass
                        else:
                            neg_cnt += 1
                    else:
                        pos_cnt += 1
                    idx += 1
                else:
                    break
            logger2.debug('%s -- %d -- %d' % (tar_word, pos_cnt, neg_cnt))
            if pos_cnt > neg_cnt:
                res = 'pos'
            elif pos_cnt < neg_cnt:
                res = 'neg'
            elif pos_cnt == neg_cnt:
                res = 'neu'
            con.append((tar_word, res))
    return con


def calc_polarity(lsts):
    lsts.sort(key=lambda x: x[0])
    dic = dict()
    for k, g in groupby(lsts, lambda x: x[0]):
        g = [i[1] for i in g]
        freq = len(g) * 1.0
        pos = g.count('pos')
        neg = g.count('neg')
        val = (pos*1.0 + neg*-1.0) / freq
        # dic[k] = val
        dic[k] = '%.5f' % val
        logger2.debug('%s | %f - %f - %f - %f' % (k, pos, neg, freq, val))
    return dic


if __name__ == '__main__':
    pos, neg = build_emolex_counter()
    target_emolex = build_target_emolex()
    posts_seg = load_posts_seg()
    pool = multiprocessing.Pool(processes=12)
    result = []
    for p in posts_seg:
        result.append(pool.apply_async(extract_sentence, (p, )))
    pool.close()
    pool.join()
    result = [i.get() for i in result]
    result = list(chain.from_iterable(result))
    dic = calc_polarity(result)

    u, d = filter_tagged_words()
    val_ref = load_val_ref()
    rows = []
    for k, v in dic.iteritems():
        if k in u:
            vals = u[k]
        elif k in d:
            vals = d[k]
        else:
            raise
        val_names = ', '.join([val_ref[i] for i in vals])
        fin = [k, v, val_names]
        rows.append(fin)
    fname = 'emo_val'
    rows.sort(key=lambda x: x[1], reverse=True)
    to_csv(rows, fname)
    rows.insert(0, [u'標記詞', u'情緒值', u'原始分類'])
    rows = zip(*rows)
    to_excel(rows, fname, 'senti')
