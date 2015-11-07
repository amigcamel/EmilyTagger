from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    # url('^$', 'senti.views.main'),
    url('^lope.anno/download/$', 'utility.views.download', name='download'),
    url('^lope.anno/download_source_text/$', 'utility.views.download_source_text', name='download_source_text'),
    url('^lope.anno/download_tagged_words/$', 'utility.views.download_tagged_words', name='download_tagged_words'),
    # url('^lope.anno/upload_text/$', 'utility.views.upload_text', name='upload_text'),
    # url('^lope.anno/paste_text/$', 'utility.views.paste_text', name='paste_text'),
    url('^lope.anno/post_uploader/$', 'utility.views.post_uploader', name='post_uploader'),
    url('^lope.anno/paste_post/$', TemplateView.as_view(template_name='paste_post.html'), name='paste_post'),
    url('^lope.anno/upload_posts/$', TemplateView.as_view(template_name='upload_posts.html'), name='upload_posts'),
    url('^lope.anno/personal_settings/$', 'utility.views.personal_settings', name='personal_settings'),
    url('^lope.anno/controls/$', 'utility.views.controls', name='controls'),

    url('^lope.anno/', include('annotator.urls')),
    url('^lope.anno/analysis/', include('analysis.urls')),
    url('^lope.anno/account/', include('account.urls')),
    url('^lope.anno/admin/', include(admin.site.urls)),
)
