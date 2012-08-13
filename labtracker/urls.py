from django.conf.urls import patterns, include, url

urlpatterns = patterns('labtracker.views',
    url(r'^$', 'item_list'),
    url(r'^(?P<page>\d+)/$', 'item_list'),
    url(r'^item/(?P<item_id>\d+)/$', 'item_detail'),
    url(r'^item/(?P<item_id>\d+)/request/$', 'submit_request'),
    url(r'^request/(?P<request_id>\d+)/$', 'request_detail'),
    url(r'^request/(?P<request_id>\d+)/request_modify/$', 'modify_request_status'),
    url(r'^request/(?P<request_id>\d+)/request/comment_submit/$', 'post_comment'),
    url(r'^login/$', 'login_user'),
    url(r'^requests/$', 'request_list'),
    url(r'^requests_admin/$', 'admin_request_list'),
    url(r'^logout/$', 'logout_user'),
)