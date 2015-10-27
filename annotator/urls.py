from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url('^$', 'annotator.views.main', name='index'),
    url('^senti/$', 'annotator.views.main', name='senti_main'),
    url('^api$', 'annotator.views.api', name='api'),
    url('^api_remove_cue$', 'annotator.views.api_remove_cue', name='api_remove_cue'),
    url('^get_total_page$', 'annotator.views.get_total_page', name='get_total_page'),
    url('^get_cand_text$', 'annotator.views.get_cand_text', name='get_cand_text'),
    url('^show_post_list$', 'annotator.views.show_post_list', name='show_post_list'),
    url('^draw_dist_pie/(?P<subtag>\w+)$', 'annotator.views.draw_dist_pie', name='draw_dist_pie'),
    url('^hide_post$', 'annotator.views.hide_post', name='hide_post'),
    url('^load_ref$', 'annotator.views.load_ref', name='load_ref'),
    url('^get_post_dist/(?P<subtag>\w+)$', 'annotator.views.get_post_dist', name='get_post_dist'),
    url('^get_freq_dist/(?P<subtag>\w+)$', 'annotator.views.get_freq_dist', name='get_freq_dist'),
)
