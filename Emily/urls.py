from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url('^lopetagger/', include('senti.urls')),
    url('^lopetagger/account/', include('account.urls')),
    url('^lopetagger/admin/', include(admin.site.urls)),
)
