from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url('^$', 'senti.views.main'),
    url('^download/$', 'home.views.download', name='download'),
    url('^upload_text/$', 'home.views.upload_text', name='upload_text'),
    url('^paste_text/$', 'home.views.paste_text', name='paste_text'),
    url('^lope.anno/', include('senti.urls')),
    url('^lope.anno/account/', include('account.urls')),
    url('^lope.anno/admin/', include(admin.site.urls)),
)
