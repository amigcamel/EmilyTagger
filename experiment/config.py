# -*-coding:utf-8-*-
from os.path import abspath, dirname, join
from django.conf import settings

CUR_PATH = dirname(abspath(__name__))
GFDIST_PATH = join(CUR_PATH, 'gfdist.rld')
POSTS_SEG_PATH = join(CUR_PATH, 'posts_seg.rld')
OUTPUT_PATH = join(CUR_PATH, 'output')
LOG_PATH = join(OUTPUT_PATH, 'logs', '%s.log')
TAG_PATH = settings.TAG_PATH
DB_PATH = settings.DATABASES['default']['NAME']
TARGET_USER = 'emily.lulala@gmail.com'
TAG = 'EMOTION'
SUBTAG = 'Emotion'

POS_PATH = join(CUR_PATH, 'src', 'postivewordsall.txt')
NEG_PATH = join(CUR_PATH, 'src', 'negativewordsall.txt')
COMBINED_LEX = join(CUR_PATH, 'src', u'整合詞表.csv')
OUTPUT_LEX = join(CUR_PATH, 'src', 'output.csv')
SAMP_PATH = join(CUR_PATH, 'src', 'Sample_experiment.xlsx')
SAMPLE_CHUNK_POLARITY = join(CUR_PATH, 'src', 'SAMPLE_CHUNK_POLARITY.csv')
