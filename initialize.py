#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    from annotator.sqlconnect import SqlConnect

    os.mkdir('dbs')
    os.mkdir('user_dbs')

    sc = SqlConnect('guest@guest.com')
    sc.create_tables()
    sc.create_sample_tags()
    sc.insert_post('ann-title', 'ann-source', 'ann-cat', u'''
        Hi,
        歡迎使用 LOPE Annotator!
        註冊後，即可上傳自己的文章，已經編輯個人標記。
        目前此系統仍在開發階段,
        若有任何問題,
        請聯絡amigcamel@gmail.com (阿吉)
        ''')
