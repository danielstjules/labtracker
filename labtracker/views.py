from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
from labtracker.models import Request, Item, Download
from django.contrib.auth import authenticate, login, logout

def index(request):
    """View a list of all items"""
    logged_user = ""
    item_list = Item.objects.all()   
    return render_to_response('labtracker/item_list.html', {'item_list': item_list},
                               context_instance=RequestContext(request))

def requests_viewer(request):
    """View a list of all requests"""
    request_list = Request.objects.filter(user = request.user.id)
    return render_to_response('labtracker/request_list.html', {'request_list': request_list},
                               context_instance=RequestContext(request))


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

def login_user(request):
    """Log in using custom login page"""
    message = "Please log in using the form below."
    username = ''
    password = ''
    template = 'auth.html'

    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username = username, password = password)
        if user is not None:
            if user.is_active:
                login(request, user)
                message = "You've successfully logged in!"
                template = 'auth_forward.html'
            else:
                message = "Your account is not active, please contact Support."
        else:
            message = "Your username and/or password were incorrect."

    return render_to_response(template,{'message' : message, 'title' : 'log in'},
                               context_instance = RequestContext(request))

def logout_user(request):
    """Log the user out and redirect them to the app root"""
    logout(request)
    message = "You've been logged out!"
    return render_to_response('auth_forward.html', {'message' : message, 'title' : 'log out'},
                               context_instance = RequestContext(request))  