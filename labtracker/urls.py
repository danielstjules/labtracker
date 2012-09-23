from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView
from django.conf.urls.defaults import *
from labtracker.models import Request, Item, Download, Comment

urlpatterns = patterns('labtracker.views',
    url(r'^((?P<page>\d+)/)?$',
        ListView.as_view(
            queryset=Item.objects.all(),
            paginate_by=50,
            template_name='item_list.html')),
    url(r'^item/(?P<item_id>\d+)/$', 'item_detail'),
    url(r'^item/(?P<item_id>\d+)/request/$', 'submit_request'),
    url(r'^request/(?P<request_id>\d+)/$', 'request_detail'),
    url(r'^request/(?P<request_id>\d+)/request_modify/$', 'modify_request_status'),
    url(r'^request/(?P<request_id>\d+)/request/comment_submit/$', 'post_comment'),
    url(r'^login/$', 'login_user'),
    url(r'^requests/$', 'request_list'),
    url(r'^requests_admin/((?P<page>\d+)/)?$',
        ListView.as_view(
            queryset=Request.objects.all().order_by('-date_updated'),
            paginate_by=50,
            template_name='request_list_admin.html')),
    url(r'^logout/$', 'logout_user'),
)
