# -*-coding:utf-8-*-
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.conf import settings
from rlite_api import update, read_pairs, remove_cue
from urllib import unquote
import re
import json
import sqlite3
from .func import gen_tag_dist


import logging
logger = logging.getLogger(__name__)


DB_PATH = settings.DATABASES['default']['NAME']


def main(request):
    return render_to_response('senti_main.html', context_instance=RequestContext(request))


def get_cand_text(request):
    res = request_parser(request)
    page_num = res['last_open_page']
    logger.debug('page_num: %s' % str(page_num))
    tag = res['tag']
    subtag = res['subtag']

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT url, post FROM emilytagger_posts WHERE id=?", (page_num, ))
    text_id, cand_text = c.fetchall()[0]
    conn.close()

    pairs = read_pairs(text_id, tag, subtag, request.user.username)

    fin = {'pairs': pairs, 'cand_text': cand_text, 'text_id': text_id}
    return HttpResponse(json.dumps(fin))


def api_remove_cue(request):
    res = request_parser(request)
    user = request.user.username
    res['user'] = user
    res = remove_cue(**res)
    return HttpResponse('ok')


def api(request):
    res = request_parser(request)
    user = request.user.username
    res['user'] = user
    res = update(**res)
    if res:
        return HttpResponse('ok')
    else:
        raise


def request_parser(request):
    req_dic = dict()
    req = request.read().split('&')
    for r in req:
        res = re.search('(.+)=(.*)', r)
        key, val = res.group(1), res.group(2)
        req_dic[key] = unquote(val)
    if 'csrfmiddlewaretoken' in req_dic:
        req_dic.pop('csrfmiddlewaretoken')
    return req_dic


def load_ref(request):
    with open(settings.TAG_PATH) as f:
        ref = f.read()
    return HttpResponse(ref)


def draw_dist_pie(request, subtag):
    res = gen_tag_dist(request.user.username, subtag)
    return HttpResponse(json.dumps(res, ensure_ascii=False))


def get_post_dist(request, subtag):
    from .rlite_api import DB_Conn
    from itertools import groupby, chain
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('select id, source, senti, url from emilytagger_posts')
    res = c.fetchall()
    res = [list(i) for i in res]

    dbconn = DB_Conn(request.user.username)

    con = []
    tag_res_con = []
    for id, source, senti, url in res:
        uid = '%s__%s' % (url, subtag)
        tag_res = dbconn.read(uid)
        if tag_res:
            con.append(1)
        else:
            con.append(0)
        tag_res_con.append(tag_res)

    tmp = zip(*res)
    tmp.append(con)
    tmp.append(tag_res_con)
    res = map(list, zip(*tmp))

    groups = []
    uniquekeys = []
    for k, g in groupby(res, lambda x: x[2]):
        groups.append(list(g))
        uniquekeys.append(k)
    dist = [('%d~%d' % (i[0][0], i[-1][0]), i[0][1], i[0][2], sum(ii[4] for ii in i), len(dict(chain.from_iterable(ii[5].items() for ii in i)))) for i in groups]
    return HttpResponse(json.dumps(dist))


def get_freq_dist(request, subtag='Emotion'):
    from .rlite_api import DB_Conn
    # from nltk import FreqDist
    from collections import Counter

    dist = json.loads(get_post_dist(request, subtag).content)

    post_range_con = []
    for post_range, source, senti, tagged_num, type_num in dist:
        post_start, post_end = post_range.split('~')
        post_range = range(int(post_start), int(post_end)+1)
        post_range_con.append(post_range)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('select id, source, senti, url from emilytagger_posts')
    res = c.fetchall()
    res = [list(i) for i in res]

    dbconn = DB_Conn(request.user.username)
    fdist_lst = []
    words_con = []
    for post_range in post_range_con:
        words = []
        for p in post_range:
            uid = '%s__%s' % (res[p-1][3], subtag)
            kv = dbconn.read(uid)
            words += kv.keys()
            words_con += kv.keys()
        words = Counter(words)
        words = words.items()
        words.sort(key=lambda x: x[1], reverse=True)
        words = [(i[0], i[1]) for i in words if i[1] > 1]
        fdist_lst.append(words)

    all_words = Counter(words_con)
    all_words = all_words.items()
    all_words.sort(key=lambda x: x[1], reverse=True)
    all_words = [(i[0], i[1]) for i in all_words if i[1] > 1]
    fdist_lst.append(all_words)

    tar = ['%s-%s' % (i[1], i[2]) for i in dist]
    tar.append('all')

    return HttpResponse(json.dumps(zip(tar, fdist_lst), ensure_ascii=False))


if __name__ == '__main__':
    from test import FakeRequest
    request = FakeRequest()
