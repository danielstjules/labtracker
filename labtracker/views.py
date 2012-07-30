from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
from labtracker.models import Request, Item, Download
from django.contrib.auth import authenticate, login

def index(request):
    """View a list of all items"""
    latest_item_list = Item.objects.all()[:5]
    return render_to_response('labtracker/item_list.html', {'latest_item_list': latest_item_list})

def detail(request, item_id):
    """View details of an item"""
    i = get_object_or_404(Item, pk = item_id)
    return render_to_response('labtracker/item_detail.html', {'item': i},
                               context_instance=RequestContext(request))

def request(request, item_id):
    """Submit a request for an item"""
    p = request.POST
    item = Item.objects.get(pk = item_id)
    request = Request.objects.create(item = item, status = "pending", notes = p["notes"], user = request.user)
    return HttpResponse("You've submitted a request for item %s." % item_id)