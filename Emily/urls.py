from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url('^emilytagger/', include('senti.urls')),
    url('^account/', include('account.urls')),
    url('^admin/', include(admin.site.urls)),
)
