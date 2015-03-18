from django import template
import json
register = template.Library()

from senti.ref import senti_ref
import re


@register.filter
def cue_with_color(item):
    cue, tag = item[0], item[1]
    output = '<span class="%s">%s</span>' % (senti_ref[tag][1], cue)
    return output


@register.filter
def txt_with_color(text, pairs):
    for k, v in pairs.iteritems():
        text = re.sub(k, '<span class="%s highlight">%s</span>' % (senti_ref[int(v)][1], k), text)
    return text


@register.filter
def to_json(dic):
    return json.dumps(dic)
