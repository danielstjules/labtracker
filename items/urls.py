from django.conf.urls import patterns, include, url

urlpatterns = patterns('items.views',
    url(r'^$', 'index'),
    url(r'^(?P<item_id>\d+)/$', 'detail'),
    url(r'^(?P<item_id>\d+)/request/$', 'request'),
)