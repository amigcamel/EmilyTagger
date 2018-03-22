# -*-coding:utf-8-*-
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.conf import settings
from .rlite_api import update, read_pairs, remove_cue
from .func import gen_tag_dist
from .sqlconnect import SqlConnect
import simplejson as json


import logging
logger = logging.getLogger(__name__)


DB_PATH = settings.DATABASES['default']['NAME']


def main(request):
    logger.info(request.user.username)
    return render_to_response(
        'senti_main.html',
        context_instance=RequestContext(request)
    )


def get_cand_text(request):
    req = request_parser(request)
    page_num = req.get('last_open_page')
    logger.debug('page_num: %s' % str(page_num))
    tag, subtag = req.get('tag'), req.get('subtag')

    sc = SqlConnect(request.user.username)
    res = sc.fetch(
        '''SELECT post_id, post FROM posts WHERE page=?''', (page_num, ))
    text_id, cand_text = res[0]

    pairs = read_pairs(text_id, tag, subtag, request.user.username)
    fin = {'pairs': pairs, 'cand_text': cand_text, 'text_id': text_id}
    resp = json.dumps(fin)

    return HttpResponse(resp)


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
    logger.info(res['value'])
    res = update(**res)
    if res:
        return HttpResponse('ok')
    else:
        raise


def request_parser(request):
    if request.method == 'POST':
        req = request.POST
    elif request.method == 'GET':
        req = request.GET

    req = req.copy().dict()
    req.pop('csrfmiddlewaretoken')
    return req


def get_total_page(request):
    sc = SqlConnect(request.user.username)
    res = sc.fetch('''SELECT max(page) FROM posts''')
    num = res[0][0]
    return HttpResponse(num)


def load_ref(request):
    sc = SqlConnect(request.user.username)
    res = sc.fetch('''SELECT schema FROM tags''')
    ref = res[0][0]
    return HttpResponse(ref)


def hide_post(request):
    if request.method == 'POST':
        r = request_parser(request)
        post_id = r['post_id']
        sc = SqlConnect(request.user.username)
        sc.hide_post(post_id)
        return HttpResponse('ok')


def mod_ref(request, jdata):
    try:
        json.loads(jdata)
        sc = SqlConnect(request.user.username)
        sc.exec_('''UPDATE tags SET schema=?''', (jdata, ))
    except BaseException:
        logger.warning('invalid json format')


def show_post_list(request):
    sc = SqlConnect(request.user.username)
    res = sc.fetch(
        '''SELECT page, title, upload_time FROM posts WHERE (page!=-1)''')
    return HttpResponse(json.dumps(res, ensure_ascii=False))


def draw_dist_pie(request, subtag):
    res = gen_tag_dist(request.user.username, subtag)
    logger.debug(res)
    return HttpResponse(json.dumps(res, ensure_ascii=False))


def get_post_dist(request, subtag):
    from .rlite_api import DB_Conn
    from itertools import groupby, chain
    sc = SqlConnect(request.user.username)
    res = sc.fetch('select post_id, source, category, upload_time from posts')
    res = [list(i) for i in res]

    dbconn = DB_Conn(request.user.username)

    con = []
    tag_res_con = []
    for id, source, category, upload_time in res:
        uid = '%s__%s' % (upload_time, subtag)
        tag_res = dbconn.read(uid)
        if tag_res:
            con.append(1)
        else:
            con.append(0)
        tag_res_con.append(tag_res)

    tmp = list(zip(*res))
    tmp.append(con)
    tmp.append(tag_res_con)
    res = map(list, zip(*tmp))

    groups = []
    uniquekeys = []
    for k, g in groupby(res, lambda x: x[2]):
        groups.append(list(g))
        uniquekeys.append(k)
    print(groups)
    raise
    dist = [
        (
            '%d~%d' % (i[0][0], i[-1][0]),
            i[0][1], i[0][2], sum(ii[4] for ii in i),
            len(dict(chain.from_iterable(ii[5].items() for ii in i)))
        )
        for i
        in groups
    ]
    return HttpResponse(json.dumps(dist))


def get_freq_dist(request, subtag='Emotion'):
    from .rlite_api import DB_Conn
    # from nltk import FreqDist
    from collections import Counter

    dist = json.loads(get_post_dist(request, subtag).content)

    post_range_con = []
    for post_range, source, senti, tagged_num, type_num in dist:
        post_start, post_end = post_range.split('~')
        post_range = range(int(post_start), int(post_end) + 1)
        post_range_con.append(post_range)

    sc = SqlConnect(request.user.username)
    res = sc.fetch('select id, source, senti, url from posts')
    res = [list(i) for i in res]

    dbconn = DB_Conn(request.user.username)
    fdist_lst = []
    words_con = []
    for post_range in post_range_con:
        words = []
        for p in post_range:
            uid = '%s__%s' % (res[p - 1][3], subtag)
            kv = dbconn.read(uid)
            words += kv.keys()
            words_con += kv.keys()
        words = Counter(words)
        words = words.items()
        words = sorted(words, key=lambda x: x[1], reverse=True)
        words = [(i[0], i[1]) for i in words if i[1] > 1]
        fdist_lst.append(words)

    all_words = Counter(words_con)
    all_words = all_words.items()
    all_words = sorted(all_words, key=lambda x: x[1], reverse=True)
    all_words = [(i[0], i[1]) for i in all_words if i[1] > 1]
    fdist_lst.append(all_words)

    tar = ['%s-%s' % (i[1], i[2]) for i in dist]
    tar.append('all')

    return HttpResponse(json.dumps(
        list(zip(tar, fdist_lst)), ensure_ascii=False))


if __name__ == '__main__':
    from test import FakeRequest
    request = FakeRequest()
