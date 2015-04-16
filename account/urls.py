from django.conf.urls import patterns, url
from . import views


urlpatterns = patterns('',
    url('^signin/$', views.signin, name='signin'),
    url('^signout/$', views.signout, name='signout'),
    url('^register/$', views.register, name='register'),
)
