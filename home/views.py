from django.shortcuts import render_to_response, resolve_url
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from .forms import PasteTextForm, UploadTextForm
from .sqlconnect import SqlConnect
from .rlite_api import DB_Conn
from datetime import datetime
import os
from zipfile import ZipFile
import shutil
import logging
logger = logging.getLogger(__name__)


# def home(request):
#     return render_to_response(
#         'home.html',
#         context_instance=RequestContext(request)
#     )

def download_source_text(request):

    def add_zip_flat(zip, filename):
        # avoid including absolute path; ref: http://stackoverflow.com/a/16104667/1105489
        dir, base_filename = os.path.split(filename)
        os.chdir(dir)
        zip.write(base_filename)

    user = request.user.username
    tmp_path = '/tmp/' + user
    if not os.path.isdir(tmp_path):
        os.mkdir(tmp_path)
    posts = SqlConnect.pack_source_text(user)
    text_paths = []
    zip_path = '/tmp/%s.zip' % user
    for num, post in enumerate(posts, 1):
        text_path = tmp_path + '/%d.txt' % num
        text_paths.append(text_path)
        with open(text_path, 'w') as f:
            f.write(post)
    with ZipFile(zip_path, 'w') as z:
        for p in text_paths:
            add_zip_flat(z, p)
    shutil.rmtree(tmp_path)

    # django download file
    # ref: http://stackoverflow.com/a/909088/1105489
    f = open(zip_path, 'rb')  # must set mode to "rb"; "r" won't work
    resp = HttpResponse(f, content_type='application/zip')
    resp['Content-Disposition'] = 'attachment; filename=source.zip'
    f.close()
    os.remove(zip_path)
    return resp


def download_tagged_words(request):
    res = DB_Conn.pack_tagged_words(request.user.username)
    resp = HttpResponse(res, content_type='application.json')
    resp['Content-Disposition'] = 'attachment; filename=tagged_words.json'
    return resp


def download(request):
    return render_to_response(
        "download.html",
        context_instance=RequestContext(request)
    )


def upload_text(request):
    if request.method == 'POST':
        upload_text_form = UploadTextForm(request.POST, request.FILES)
        # if request.FILES:
        query_dict = request.POST
        if 'uploadFile' in query_dict:
            logger.info(request.FILES['upload_file'].name)
            r = request_parser(request)
            r.pop('uploadFile')
            files = request.FILES.getlist('upload_file')
            for f in files:
                logger.debug(f.name)
                text = f.read()
                logger.debug(text)
                r['post'] = text
                r['post_id'] = str(datetime.now())
                sc = SqlConnect(request.user.username)
                sc.insert_post(**r)
            return HttpResponseRedirect(resolve_url('index'))
    else:
        upload_text_form = UploadTextForm()

    return render_to_response(
        'upload_text.html',
        {
            'upload_text_form': upload_text_form,
        },
        context_instance=RequestContext(request)
    )


def paste_text(request):
    if request.method == 'POST':
        paste_text_form = PasteTextForm(request.POST)
        r = request_parser(request)
        r.pop('pasteText')
        logger.info(r)
        if len(r.get('post').strip()) != 0:
            r['post_id'] = str(datetime.now())
            sc = SqlConnect(request.user.username)
            sc.insert_post(**r)
            return HttpResponseRedirect(resolve_url('index'))

    else:
        paste_text_form = PasteTextForm()

    return render_to_response(
        'paste_text.html',
        {
            'paste_text_form': paste_text_form,
        },
        context_instance=RequestContext(request)
    )


def request_parser(request):
    if request.method == 'POST':
        req = request.POST
    elif request.method == 'GET':
        req = request.GET

    req = req.copy().dict()
    req.pop('csrfmiddlewaretoken')
    return req
