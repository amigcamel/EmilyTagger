from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url('^$', 'home.views.home', name='home'),
    url('^lope.anno/', include('senti.urls')),
    url('^lope.anno/account/', include('account.urls')),
    url('^lope.anno/admin/', include(admin.site.urls)),
)
