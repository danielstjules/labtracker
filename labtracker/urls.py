from django.conf.urls import patterns, url
from django.views.generic import ListView
from labtracker.models import Request, Item

urlpatterns = patterns(
    'labtracker.views',
    url(r'^((?P<page>\d+)/)?$',
        ListView.as_view(
            queryset=Item.objects.all(),
            paginate_by=50,
            template_name='item_list.html')),
    url(r'^item/(?P<item_id>\d+)/$', 'item_detail'),
    url(r'^item/(?P<item_id>\d+)/request/$', 'submit_request'),
    url(r'^request/(?P<request_id>\d+)/$', 'request_detail'),
    url(r'^request/(?P<request_id>\d+)/modify/$', 'modify_request_status'),
    url(r'^request/(?P<request_id>\d+)/post_comment/$', 'post_comment'),
    url(r'^login/$', 'login_user'),
    url(r'^reports/$', 'reports'),
    url(r'^report/(?P<report_id>\d+)/delete/$', 'delete_report'),
    url(r'^requests/$', 'request_list'),
    url(r'^requests_admin/((?P<page>\d+)/)?$',
        ListView.as_view(
            queryset=Request.objects.all().order_by('-date_updated'),
            paginate_by=50,
            template_name='request_list_admin.html')),
    url(r'^logout/$', 'logout_user'),
)
