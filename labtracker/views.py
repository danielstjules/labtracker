from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
from labtracker.models import Request, Item, Download
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def item_list(request, page = 1):
    """View a paginated list of items"""
    items = Item.objects.all() 
    paginator = Paginator(items, 50)

    try:
        item_list = paginator.page(page)
    except PageNotAnInteger:
        item_list = paginator.page(1)
    except EmptyPage:
        item_list = paginator.page(paginator.num_pages)

    return render_to_response('labtracker/item_list.html', {'item_list': item_list},
                               context_instance=RequestContext(request))

def item_detail(request, item_id):
    """View details of an item"""
    i = get_object_or_404(Item, pk = item_id)
    return render_to_response('labtracker/item_detail.html', {'item': i},
                               context_instance=RequestContext(request))

def submit_request(request, item_id):
    """Submit a request for an item"""
    p = request.POST
    item = Item.objects.get(pk = item_id)
    message = {'type': 'success_message', 'text': "You have successfully submitted a request for item: " + item.name}
    template = 'forward.html'
    fwd_page = '/labtracker/request_list/'
    req = Request.objects.create(item = item, status = "pending", notes = p["notes"], user = request.user)
    return render_to_response(template, {message['type'] : message['text'], 'title' : 'Sucessful', 'fwd_page' : fwd_page},
                               context_instance = RequestContext(request))

def request_list(request):
    """View a list of requests"""
    request_list = Request.objects.filter(user = request.user.id)
    return render_to_response('labtracker/request_list.html', {'request_list': request_list},
                               context_instance=RequestContext(request))

def request_detail(request, request_id):
    """View details of a request"""
    i = get_object_or_404(Request, pk = request_id)
    return render_to_response('labtracker/request_detail.html', {'request': i},
                               context_instance=RequestContext(request))

def login_user(request):
    """Log in using custom login page"""
    message = {'type': 'message', 'text': "Please log in using the form below."}
    username = password = ''
    template = 'auth.html'
    fwd_page = '/labtracker/'
    
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username = username, password = password)
        if user is not None:
            if user.is_active:
                login(request, user)
                message = {'type': 'success_message', 'text': "Login successful!"}
                template = 'forward.html'
            else:
                message = {'type': 'error_message', 'text': "Your account is not active, please contact Support."}
        else:
            message = {'type': 'error_message', 'text': "Your username and/or password were incorrect."}

    return render_to_response(template,{message['type'] : message['text'], 'title' : 'log in', 'fwd_page' : fwd_page}, 
                                context_instance = RequestContext(request))

def logout_user(request):
    """Log the user out and redirect them to the app root"""
    logout(request)
    message = {'type': 'success_message', 'text': "You've been successfully logged out!"}
    template = 'forward.html'
    fwd_page = '/labtracker/'
    return render_to_response(template, {message['type'] : message['text'], 'title' : 'log out', 'fwd_page' : fwd_page},
                               context_instance = RequestContext(request))  