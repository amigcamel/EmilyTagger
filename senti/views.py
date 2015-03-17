# -*-coding:utf-8-*-
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
# from .forms import SentiTagForm
from .mongo import *
from .ref import senti_ref
from urllib import unquote
import re
from misc.templatetags.senti_tag import txt_with_color
import json


def main(request, current_page=None):
    return render_to_response('senti_main.html', {'senti_ref': senti_ref}, context_instance=RequestContext(request))

    # if current_page is None:
    #     current_page = request.COOKIES.get('last_open_page', 1)

    # if int(current_page) < 1:
    #     return HttpResponseRedirect(reverse('index'))
    # elif int(current_page) >= 1 and int(current_page) <= 499:
    #     db_name = 'senti_news'
    # elif int(current_page) > 499 and int(current_page) <= 899:
    #     db_name = 'senti_ptt'
    # elif int(current_page) > 899:
    #     return HttpResponseRedirect(reverse('index'))

    # cat, url = find_next_id(int(current_page), db_name)
    # dic = dict()
    # dic['current_page'] = int(current_page) + 1

    # doc = c[db_name][cat].find({'_id': url}, {'content': 1}).next()
    # dic['text'] = doc['content']
    # text_id = dic['text_id'] = doc['_id']
    # dic['senti_ref'] = senti_ref
    # dic['pairs'] = read_pairs(text_id, request.user.username)
    # dic['pairs_by_cat'] = read_by_cat(text_id, request.user.username)
    # res = render_to_response('senti_main.html', dic, context_instance=RequestContext(request))
    # # res.set_cookie('last_open_page', current_page)
    # return res


def get_cand_text(request, page_num):
    if int(page_num) < 1:
        return HttpResponseRedirect(reverse('index'))
    elif int(page_num) >= 1 and int(page_num) <= 499:
        db_name = 'senti_news'
    elif int(page_num) > 499 and int(page_num) <= 899:
        db_name = 'senti_ptt'
    elif int(page_num) > 899:
        return HttpResponseRedirect(reverse('index'))

    cat, url = find_next_id(int(page_num), db_name)

    doc = c[db_name][cat].find({'_id': url}, {'content': 1}).next()
    cand_text = doc['content']
    text_id = doc['_id']
    pairs_by_cat = read_by_cat(text_id, request.user.username)
    pairs = read_pairs(text_id, request.user.username)
    cand_text = txt_with_color(cand_text, pairs)
    fin = {'pairs_by_cat': pairs_by_cat, 'cand_text': cand_text, 'text_id': text_id}
    return HttpResponse(json.dumps(fin))


def api_remove_cue(request):
    res = request_parser(request)
    text_id = res['text_id']
    cue = res['cue']
    username = request.user.username
    remove_cue(text_id, cue, username)
    return HttpResponse('ok')


def api(request):
    res = request_parser(request)
    cue = res['cue']
    val = int(res['value'])
    text_id = res['text_id']
    update(text_id=text_id, cue=cue, tag=val, user=request.user.username)
    return HttpResponse('ok')


def request_parser(request):
    req_dic = dict()
    req = request.read().split('&')
    for r in req:
        res = re.search('(.+)=(.*)', r)
        key, val = res.group(1), res.group(2)
        req_dic[key] = unquote(val)
    return req_dic
