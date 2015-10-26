from django.conf.urls import patterns, url
from . import views


urlpatterns = patterns(
    '',
    # url('^$', 'annotator.views.main', name='index'),
    url('^tagdist/$', views.tagdist, name='tagdist'),
    url('^tagstat/$', views.tagstat, name='tagstat'),
    url('^worddist/$', views.worddist, name='worddist'),
)
