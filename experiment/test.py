# -*-coding:utf-8-*-
# from __future__ import unicode_literals
import sys
# import simplejson as json


def force_encoding_output(func):

    if sys.version_info.major < 3:

        def _func(*args, **kwargs):
            return func(*args, **kwargs)

        return _func

    else:
        return func


class Foo(object):

    def __init__(self, text):
        self.text = text

    # @force_encoding_output
    def __repr__(self):
        return self.text
        # return json.dumps(self.text, ensure_ascii=False)


class Func:

    def concat(self, w1, w2):
        res = w1 + w2
        return C(res)


class C:

    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return self.text


if __name__ == '__main__':
    func = Func()
