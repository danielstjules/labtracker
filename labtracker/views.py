from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from labtracker.models import Request, Item, Comment
from django.contrib.auth import authenticate, login, logout


def item_detail(request, item_id):
    """View details of an item"""
    i = get_object_or_404(Item, pk=item_id)
    req_list = Request.objects.filter(item=i, status='active')
    i.views += 1
    i.save()
    return render_to_response('item_detail.html', {'item': i, 'req_list': req_list},
                              context_instance=RequestContext(request))


def submit_request(request, item_id):
    """Submit a request for an item"""
    post = request.POST
    item = Item.objects.get(pk=item_id)
    template = 'forward.html'
    fwd_page = '/item/' + item_id
    Request.objects.create(item=item, status="pending", notes=post["notes"],
                           user=request.user)
    response = {
        'success_message': "You have successfully submitted a request for: " + item.description,
        'title': 'Successful',
        'fwd_page': fwd_page
    }
    return render_to_response(template, response,
                              context_instance=RequestContext(request))


def modify_request_status(request, request_id):
    """Change the status of an existing request"""
    post = request.POST
    req = Request.objects.get(pk=request_id)
    template = 'forward.html'
    fwd_page = '/requests_admin/'
    req.status = post.get('choice')
    req.save()
    response = {
        'success_message': "Request Status changed successfully to: " + post.get('choice'),
        'title': 'Successful',
        'fwd_page': fwd_page
    }
    return render_to_response(template, response,
                              context_instance=RequestContext(request))


def post_comment(request, request_id):
    """Post a user comment on request_details page"""
    post = request.POST
    req = Request.objects.get(pk=request_id)
    Comment.objects.create(user=request.user, request=req, content=post["comment"])
    template = 'forward.html'
    fwd_page = '/request/'+request_id+'/'
    if request.user != req.user:
        req.mark_unread()
    response = {
        'success_message': "Your comment has been successfully posted",
        'title': 'Successful',
        'fwd_page': fwd_page
    }
    return render_to_response(template, response,
                              context_instance=RequestContext(request))


def request_list(request):
    """View a list of requests for the current user"""
    request_list = Request.objects.filter(user=request.user.id)
    return render_to_response('request_list.html', {'request_list': request_list},
                              context_instance=RequestContext(request))


def request_detail(request, request_id):
    """View details of a request"""
    req = get_object_or_404(Request, pk=request_id)
    item = Item.objects.get(pk=req.item.id)
    req_list = Request.objects.filter(item=item, status='active')
    comment_list = Comment.objects.filter(request=req).order_by('-date_submitted')
    if request.user == req.user:
        req.mark_read()
    response = {'req': req, 'req_list': req_list, 'comment_list': comment_list}
    return render_to_response('request_detail.html', response,
                              context_instance=RequestContext(request))


def login_user(request):
    """Log in using custom login page"""
    username = password = ''

    msg_type = 'message'
    msg_text = "Please log in using the form below."
    template = 'auth.html'
    fwd_page = '/'

    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                msg_type = 'success_message'
                msg_text = "Login successful!"
                template = 'forward.html'
            else:
                msg_type = 'error_message'
                msg_text = "Your account is not active, please contact Support."
        else:
            msg_type = 'error_message'
            msg_text = "Your username and/or password were incorrect."

    response = {
        msg_type: msg_text,
        'title': 'log in',
        'fwd_page': fwd_page
    }

    return render_to_response(template, response,
                              context_instance=RequestContext(request))


def logout_user(request):
    """Log the user out and redirect them to the app root"""
    logout(request)
    template = 'forward.html'
    fwd_page = '/'
    response = {
        'success_message': "You've been successfully logged out!",
        'title': 'log out',
        'fwd_page': fwd_page
    }
    return render_to_response(template, response,
                              context_instance=RequestContext(request))
