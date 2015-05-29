# -*-coding:utf-8-*-
from django.shortcuts import render_to_response, resolve_url
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.conf import settings
from .rlite_api import update, read_pairs, remove_cue
from .func import gen_tag_dist
from .forms import UploadTextForm, ModifyTagForm, PasteTextForm
from .sqlconnect import SqlConnect
import simplejson as json


import logging
logger = logging.getLogger(__name__)


DB_PATH = settings.DATABASES['default']['NAME']


def main(request):
    if request.method == 'POST':
        upload_text_form = UploadTextForm(request.POST, request.FILES)
        modify_tag_form = ModifyTagForm(request.POST)
        paste_text_form = PasteTextForm(request.POST)
        # if request.FILES:
        query_dict = request.POST
        if 'uploadFile' in query_dict:
            # logger.info(request.FILES['upload_file'].name)
            files = request.FILES.getlist('upload_file')
            for f in files:
                logger.debug(f.name)
                text = f.read()
                logger.debug(text)
                sc = SqlConnect(request.user.username)
                sc.insert_post(text)
            return HttpResponseRedirect(resolve_url('index'))

        elif 'pasteText' in query_dict:
            res = query_dict.get('text')
            logger.info(res)
            if len(res.strip()) != 0:
                logger.debug(res)
                sc = SqlConnect(request.user.username)
                sc.insert_post(res)
                return HttpResponseRedirect(resolve_url('index'))

        elif 'modifyTag' in query_dict:
            res = query_dict.get('tag_schema')
            logger.info(res)
            if len(res.strip()) != 0:
                mod_ref(request, res)
                return HttpResponseRedirect(resolve_url('index'))

    else:
        upload_text_form = UploadTextForm()
        logger.info(request.user.username)
        sc = SqlConnect(request.user.username)
        sc._c.execute('''SELECT schema FROM tags WHERE (id=1)''')
        ref = sc._c.fetchall()[0][0]
        modify_tag_form = ModifyTagForm(initial={'tag_schema': ref})
        paste_text_form = PasteTextForm()
    return render_to_response(
            'senti_main.html',
            {
                'upload_text_form': upload_text_form,
                'modify_tag_form': modify_tag_form,
                'paste_text_form': paste_text_form
            },
            context_instance=RequestContext(request)
        )


def get_cand_text(request):
    req = request_parser(request)
    page_num = req.get('last_open_page')
    logger.debug('page_num: %s' % str(page_num))
    tag, subtag = req.get('tag'), req.get('subtag')

    sc = SqlConnect(request.user.username)
    sc._c.execute('''SELECT url, post FROM posts WHERE id=?''', (page_num, ))

    text_id, cand_text = sc._c.fetchall()[0]

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
    sc._c.execute('''SELECT count(*) FROM posts''')
    num = sc._c.fetchall()[0][0]
    return HttpResponse(num)


def load_ref(request):
    sc = SqlConnect(request.user.username)
    sc._c.execute('''SELECT schema FROM tags''')
    ref = sc._c.fetchall()[0][0]
    return HttpResponse(ref)


def mod_ref(request, jdata):
    try:
        json.loads(jdata)
        sc = SqlConnect(request.user.username)
        sc._c.execute('''UPDATE tags SET schema=?''', (jdata, ))
    except:
        logger.warning('invalid json format')


def draw_dist_pie(request, subtag):
    res = gen_tag_dist(request.user.username, subtag)
    logger.debug(res)
    return HttpResponse(json.dumps(res, ensure_ascii=False))


def get_post_dist(request, subtag):
    from .rlite_api import DB_Conn
    from itertools import groupby, chain
    sc = SqlConnect(request.user.username)
    sc._c.execute('select id, source, senti, url from posts')
    res = sc._c.fetchall()
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

    tmp = list(zip(*res))
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

    sc = SqlConnect(request.user.username)
    sc._c.execute('select id, source, senti, url from posts')
    res = sc._c.fetchall()
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

    return HttpResponse(json.dumps(list(zip(tar, fdist_lst)), ensure_ascii=False))


if __name__ == '__main__':
    from test import FakeRequest
    request = FakeRequest()
