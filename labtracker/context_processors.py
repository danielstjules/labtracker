from labtracker.models import Request, Item, Download
from django.db.models import Q

def unread_processor(request):
    unread_number = Request.objects.filter(
		Q(status = 'pending') | Q(status = 'approved') | Q(status = 'active'),
		user = request.user.id, 
		read = False, 
	).count()
    return {'unread_number': unread_number}

def username_processor(request):
    user_name = request.user.username
    return {'user_name': user_name}    

def pending_requests_nr_processor(request):
    pending_requests_nr = Request.objects.filter(status = 'pending').count()
    return {'pending_requests_nr': pending_requests_nr}        