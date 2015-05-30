from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url('^$', 'senti.views.main', name='index'),
    url('^senti/$', 'senti.views.main', name='senti_main'),
    url('^api$', 'senti.views.api', name='api'),
    url('^api_remove_cue$', 'senti.views.api_remove_cue', name='api_remove_cue'),
    url('^get_total_page$', 'senti.views.get_total_page', name='get_total_page'),
    url('^get_cand_text$', 'senti.views.get_cand_text', name='get_cand_text'),
    url('^draw_dist_pie/(?P<subtag>\w+)$', 'senti.views.draw_dist_pie', name='draw_dist_pie'),
    url('^delete_post$', 'senti.views.delete_post', name='delete_post'),
    url('^load_ref$', 'senti.views.load_ref', name='load_ref'),
    url('^get_post_dist/(?P<subtag>\w+)$', 'senti.views.get_post_dist', name='get_post_dist'),
    url('^get_freq_dist/(?P<subtag>\w+)$', 'senti.views.get_freq_dist', name='get_freq_dist'),
)
