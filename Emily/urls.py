from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url('^emilytagger/', include('senti.urls')),
    url('^emilytagger/account/', include('account.urls')),
    url('^emilytagger/admin/', include(admin.site.urls)),
)
