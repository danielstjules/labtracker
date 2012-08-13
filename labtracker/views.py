from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
from labtracker.models import Request, Item, Download, Comment
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
    req_list = Request.objects.filter(item = i, status = 'active')
    i.views += 1
    i.save()
    return render_to_response('labtracker/item_detail.html', {'item': i, 'req_list': req_list}, 
                               context_instance=RequestContext(request))

def submit_request(request, item_id):
    """Submit a request for an item"""
    p = request.POST
    item = Item.objects.get(pk = item_id)
    message = {'type': 'success_message', 'text': "You have successfully submitted a request for item: " + item.name}
    template = 'forward.html'
    fwd_page = '/labtracker/item/' + item_id
    req = Request.objects.create(item = item, status = "pending", notes = p["notes"], user = request.user)
    return render_to_response(template, {message['type'] : message['text'], 'title' : 'Sucessful', 'fwd_page' : fwd_page},
                               context_instance = RequestContext(request))    

def modify_request_status(request, request_id):
    p = request.POST
    req = Request.objects.get(pk = request_id)
    message = {'type': 'success_message', 'text': "Request Status changed sucessfully to: "+p.get('choice')}
    template = 'forward.html'
    fwd_page = '/labtracker/requests_admin/'
    req.status = p.get('choice')
    req.save()
    return render_to_response(template, {message['type'] : message['text'], 'title' : 'Sucessful', 'fwd_page' : fwd_page},
                               context_instance = RequestContext(request))

def post_comment(request, request_id):
    p = request.POST
    req = Request.objects.get(pk = request_id)
    comment = Comment.objects.create(user = request.user, request= req, content = p["comment"])
    message = {'type': 'success_message', 'text': "Your comment has been posted sucessfully "}
    template = 'forward.html'
    fwd_page = '/labtracker/request/'+request_id+'/'
    return render_to_response(template, {message['type'] : message['text'], 'title' : 'Sucessful', 'fwd_page' : fwd_page},
                               context_instance = RequestContext(request))    

def request_list(request):
    """View a list of requests for the current user"""
    request_list = Request.objects.filter(user = request.user.id)
    return render_to_response('labtracker/request_list.html', {'request_list': request_list},
                               context_instance=RequestContext(request))

def admin_request_list(request):
    """View a list of all requests (admin view) """
    request_list = Request.objects.all()
    return render_to_response('labtracker/request_list_admin.html', {'request_list': request_list},
                               context_instance=RequestContext(request))    


def request_detail(request, request_id):
    """View details of a request"""
    req = get_object_or_404(Request, pk = request_id)
    item = Item.objects.get(pk = req.item.id)
    req_list = Request.objects.filter(item = item, status = 'active')
    comment_list = Comment.objects.filter(request = req)
    if request.user == req.user:
        req.mark_read()
    return render_to_response('labtracker/request_detail.html', {'req': req, 'req_list' : req_list, 'comment_list' : comment_list},
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