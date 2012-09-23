from labtracker.models import Request, Item, Download
from django.db.models import Q

def unread_processor(request):
    unread_number = Request.objects.filter(
		Q(status = 'pending') | Q(status = 'approved') | Q(status = 'active'),
		user = request.user.id, 
		read = False, 
	).count()
    return {'unread_number': unread_number} 

def open_requests_processor(request):
    open_requests_number = Request.objects.filter(
		Q(status = 'pending') | Q(status = 'approved') | Q(status = 'active'),
	).count()
    return {'open_requests_number': open_requests_number}