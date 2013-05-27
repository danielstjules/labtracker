from django.contrib import admin
from labtracker.models import Item, Download, Request


class DownloadInline(admin.StackedInline):
    model = Download
    extra = 1


class DownloadAdmin(admin.ModelAdmin):
    list_display = ('name', 'item', 'dtype')
    list_filter = ['dtype']


class ItemAdmin(admin.ModelAdmin):
    list_display = ('description', 'location', 'local_num')
    inlines = [DownloadInline]


class RequestAdmin(admin.ModelAdmin):
    list_display = ('item', 'status', 'user', 'date_submitted')
    list_filter = ['date_submitted']

admin.site.register(Download, DownloadAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Request, RequestAdmin)
