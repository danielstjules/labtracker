from django.conf.urls import patterns, include, url

urlpatterns = patterns('labtracker.views',
    url(r'^$', 'index'),
    url(r'^(?P<page>\d+)/$', 'index'),
    url(r'^item/(?P<item_id>\d+)/$', 'detail'),
    url(r'^item/(?P<item_id>\d+)/request/$', 'request'),
	#url(r'^request/(?P<request_id>\d+)$', 'request_detail'),
    url(r'^login/$', 'login_user'),
    url(r'^request_list/$', 'requests_viewer'),
    url(r'^logout/$', 'logout_user'),
)