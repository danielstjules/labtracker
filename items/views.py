from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
from items.models import Request, Item, Download
from django.contrib.auth import authenticate, login

def index(request):
    latest_item_list = Item.objects.all()[:5]
    return render_to_response('items/index.html', {'latest_item_list': latest_item_list})

def detail(request, item_id):
    i = get_object_or_404(Item, pk=item_id)
    return render_to_response('items/detail.html', {'item': i},
                               context_instance=RequestContext(request))

def request(request, item_id):
    return HttpResponse("You're submitting a request for item %s." % item_id)

