from django.contrib import admin
from items.models import Item, Download, Request

class DownloadInline(admin.StackedInline):
    model = Download
    extra = 1

class ItemAdmin(admin.ModelAdmin):
    inlines = [DownloadInline]

admin.site.register(Item, ItemAdmin)
admin.site.register(Request)