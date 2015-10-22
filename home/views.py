from django.shortcuts import render_to_response, resolve_url
from django.http import HttpResponseRedirect
from django.template import RequestContext
from .forms import PasteTextForm, UploadTextForm
from .sqlconnect import SqlConnect
import logging
logger = logging.getLogger(__name__)


# def home(request):
#     return render_to_response(
#         'home.html',
#         context_instance=RequestContext(request)
#     )


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
