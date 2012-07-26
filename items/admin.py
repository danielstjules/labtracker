from django.contrib import admin
from items.models import Item, Download, Request

class DownloadInline(admin.StackedInline):
    model = Download
    extra = 1

class ItemAdmin(admin.ModelAdmin):
    list_display = ('description', 'location', 'local_num')
    inlines = [DownloadInline]

class RequestAdmin(admin.ModelAdmin):
    list_display = ('status', 'item')
    list_filter = ['sub_date']

admin.site.register(Item, ItemAdmin)
admin.site.register(Request, RequestAdmin)