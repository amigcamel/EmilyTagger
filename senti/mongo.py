# -*-coding:utf8-*-
from pymongo import Connection
from ref import senti_ref


c = Connection(host='localhost', port=27017)
db = c['senti_user']


def create(text_id, user):
    db[user].insert({'_id': text_id, 'tags': {}})


def remove_cue(text_id, cue, user):
    if not user:
        user = 'guest'
    # When passing indecies of senti_news (which all start with '/') by using
    # Django URL dispatcher, '/' will lost... maybe there is something wrong
    # with the url patterns that I wrote...
    if not text_id.startswith('/'):
        if '/M.' not in text_id:  # DIRTY!!!!!!!!!!!!!!!!!!!!!
            text_id = '/' + text_id
    db[user].update({'_id': text_id}, {'$unset': {'tags.%s' % cue: 1}})


# def update(text_id, cue, tag, user):
#     if not user:
#         user = 'guest'
#     db[user].update({'_id': text_id}, {'$set': {'tags.%s' % cue: tag}})


# def read_pairs(text_id, user):
#     if not user:
#         user = 'guest'
#     while True:
#         try:
#             res = db[user].find({'_id': text_id}, {'tags': 1}).next()['tags']
#             break
#         except StopIteration:
#             create(text_id, user)
#             continue
#     return res


def read_by_cat(text_id, user):
    res = read_pairs(text_id, user)
    dic = dict()
    for i in senti_ref.keys():
        dic[i] = list()
    for k, v in res.iteritems():
        dic[v].append(k)
    return dic


def mk_content_lst(db_name):
    if db_name == 'senti_news':
        col_name = 'yahoo'
    elif db_name == 'senti_ptt':
        col_name = 'ptt'

    res = c[db_name].collection_names()

    res.remove('system.indexes')
    con = []
    for cat in res:
        cat_lst = c[db_name][cat].find({}, {'_id': 1})
        cat_lst = list(cat_lst)
        cat_lst = [(cat, i['_id']) for i in cat_lst]
        con += cat_lst
    con = [(idx, i[0], i[1]) for idx, i in enumerate(con, 1)]
    for idx, cat, url in con:
        print idx, cat, url
        c[db_name + '_cache'][col_name].insert(
            {'_id': idx, 'cat': cat, 'url': url})


def find_next_id(current_idx, db_name):
    if db_name == 'senti_news':
        col_name = 'yahoo'
    elif db_name == 'senti_ptt':
        col_name = 'ptt'
        current_idx -= 499

    res = c[db_name + '_cache'][col_name].find(
        {'_id': current_idx}, {'cat': 1, 'url': 1}).next()
    cat, url = res['cat'], res['url']
    return cat, url

# def delete(text_id, user):
#    db[user].remove({'_id':text_id})
