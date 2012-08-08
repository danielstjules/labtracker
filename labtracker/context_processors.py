from labtracker.models import Request, Item, Download

def unread_processor(request):
    unread_number = Request.objects.filter(user = request.user.id, read = False).count()
    return {'unread_number': unread_number}