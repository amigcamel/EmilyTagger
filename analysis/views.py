from django.shortcuts import render_to_response
from django.template import RequestContext


def tagdist(request):
    return render_to_response(
        'tagdist.html',
        context_instance=RequestContext(request)
    )


def tagstat(request):
    return render_to_response(
        'tagstat.html',
        context_instance=RequestContext(request)
    )


def worddist(request):
    return render_to_response(
        'worddist.html',
        context_instance=RequestContext(request)
    )
