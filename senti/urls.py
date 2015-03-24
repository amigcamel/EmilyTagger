from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url('^$', 'senti.views.main', name='index'),
    url('^senti/$', 'senti.views.main', name='senti_main'),
    url('^api$', 'senti.views.api', name='api'),
    url('^api_remove_cue$', 'senti.views.api_remove_cue', name='api_remove_cue'),
    url('^get_cand_text$', 'senti.views.get_cand_text', name='get_cand_text'),
    url('^get_ref$', 'senti.views.get_ref', name='get_ref'),
)
