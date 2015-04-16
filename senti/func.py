# -*-coding:utf8-*-
from .rlite_api import DB_Conn
from itertools import groupby, chain
from collections import OrderedDict
from django.conf import settings
import json
import sqlite3

DB_PATH = settings.DATABASES['default']['NAME']
TAG_PATH = settings.TAG_PATH


def gen_tag_dist(user, subtag):
    with open(TAG_PATH) as f:
        _ref = json.load(f)
        _ref = dict(chain.from_iterable([i.items() for i in _ref.values()]))

    ref, seriesColors = zip(*_ref[subtag])

    dbconn = DB_Conn(user)
    res = dbconn.collect(subtag)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('select id, source, senti, url from emilytagger_posts')
    res = c.fetchall()
    res = [list(i) for i in res]

    con = []

    for id, source, senti, url in res:
        uid = '%s__%s' % (url, subtag)
        tag_res = dbconn.read(uid)
        output = (id, '%s-%s' % (source, senti), tag_res)
        con.append(output)

    groups = []
    uniqk = []
    for k, g in groupby(con, lambda x: x[1]):
        groups.append(list(g))
        uniqk.append(k)

    tags_con = []
    for k, g in zip(uniqk, groups):
        tags = list(chain.from_iterable([i[-1].items() for i in g]))
        tags_con.append((k, tags))

    tags_con.append(('all', list(chain.from_iterable([i[1] for i in tags_con]))))

    output = OrderedDict()
    for t in tags_con:
        group_name = t[0]
        percentage, totalnum = _dist_pie(ref, t[1])
        output[group_name] = {'percentage': percentage, 'totalnum': totalnum}

    tar = {'groups': output, 'seriesColors': seriesColors}

    return tar


def _dist_pie(ref, tags):
    tags.sort(key=lambda x: x[1])
    groups = []
    uniqk = []
    for k, g in groupby(tags, lambda x: x[1]):
        groups.append(list(g))
        uniqk.append(k)
    vals = []
    for num, g in enumerate(groups):
        partnum = len(set([j[0] for j in g]))
        vals.append(partnum)
    totalnum = sum(vals) * 1.0
    percentage = [v/totalnum*100 for v in vals]
    lst = zip(ref, percentage)
    return lst, vals
