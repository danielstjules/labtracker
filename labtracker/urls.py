from django.conf.urls import patterns, include, url

urlpatterns = patterns('labtracker.views',
    url(r'^$', 'index'),
    url(r'^(?P<item_id>\d+)/$', 'detail'),
    url(r'^(?P<item_id>\d+)/request/$', 'request'),
    url(r'^login/$', 'login_user'),
    url(r'^logout/$', 'logout_user'),
)