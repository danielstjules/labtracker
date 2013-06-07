from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from labtracker.models import Request, Item, Comment, Report
from datetime import timedelta, date
from django.utils import timezone


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
    # Display login page and error if the user isn't logged in
    if not request.user.is_authenticated():
        error_response = {'error_message': 'You must login to submit a request.'}
        return render_to_response('auth.html', error_response,
                                  context_instance=RequestContext(request))

    post = request.POST
    item = Item.objects.get(pk=item_id)
    template = 'forward.html'
    Request.objects.create(item=item, status=Request.PENDING, notes=post["notes"],
                           user=request.user)
    response = {
        'success_message': "You have successfully submitted a request for: " + item.description,
        'title': 'Successful',
        'fwd_page': item.get_absolute_url
    }
    return render_to_response(template, response,
                              context_instance=RequestContext(request))


def modify_request_status(request, request_id):
    """Change the status of an existing request"""
    # Display login page and error if not logged in as staff
    if not request.user.is_authenticated() or not request.user.is_staff:
        error_response = {'error_message': 'Only Admins can modify a request status.'}
        return render_to_response('auth.html', error_response,
                                  context_instance=RequestContext(request))

    post = request.POST
    req = Request.objects.get(pk=request_id)
    template = 'forward.html'
    req.status = post.get('choice')
    req.save()
    response = {
        'success_message': "Request Status changed successfully to: " + post.get('choice'),
        'title': 'Successful',
        'fwd_page': req.get_absolute_url
    }
    return render_to_response(template, response,
                              context_instance=RequestContext(request))


def post_comment(request, request_id):
    """Post a user comment on request_details page"""
    # Display login page and error if the user isn't logged in
    if not request.user.is_authenticated():
        error_response = {'error_message': 'You must login to comment on a request.'}
        return render_to_response('auth.html', error_response,
                                  context_instance=RequestContext(request))

    post = request.POST
    req = Request.objects.get(pk=request_id)
    Comment.objects.create(user=request.user, request=req, content=post["comment"])
    template = 'forward.html'
    if request.user != req.user:
        req.mark_unread()
    response = {
        'success_message': "Your comment has been successfully posted",
        'title': 'Successful',
        'fwd_page': req.get_absolute_url
    }
    return render_to_response(template, response,
                              context_instance=RequestContext(request))


def request_list(request):
    """View a list of requests for the current user"""
    # Display login page and error if the user isn't logged in
    if not request.user.is_authenticated():
        error_response = {'error_message': 'You must login to view this page.'}
        return render_to_response('auth.html', error_response,
                                  context_instance=RequestContext(request))

    request_list = Request.objects.filter(user=request.user.id)
    return render_to_response('request_list.html', {'request_list': request_list},
                              context_instance=RequestContext(request))


def request_detail(request, request_id):
    """View details of a request"""
    # Display login page and error if the user isn't logged in
    if not request.user.is_authenticated():
        error_response = {'error_message': 'You must login to view this page.'}
        return render_to_response('auth.html', error_response,
                                  context_instance=RequestContext(request))

    req = get_object_or_404(Request, pk=request_id)
    item = Item.objects.get(pk=req.item.id)
    req_list = Request.objects.filter(item=item, status='active')
    comment_list = Comment.objects.filter(request=req).order_by('-date_submitted')
    if request.user == req.user:
        req.mark_read()
    response = {'req': req, 'req_list': req_list, 'comment_list': comment_list}
    return render_to_response('request_detail.html', response,
                              context_instance=RequestContext(request))


def reports(request):
    """Generate excel reports regarding requests and item use"""
    # Display login page and error if not logged in as staff
    if not request.user.is_authenticated() or not request.user.is_staff:
        error_response = {'error_message': 'Only admins can view this page.'}
        return render_to_response('auth.html', error_response,
                                  context_instance=RequestContext(request))

    # On POST, generate the report
    if request.POST:
        post = request.POST

        # Define some default values
        today = date.today()
        start_date = None
        end_date = timezone.now()

        title = post.get('title') if post.get('title') else None
        company = post.get('company') if post.get('company') else None
        item_id = post.get('item') if post.get('item') else None

        # Check if start and end dates are set
        if post.get('startdate') and post.get('enddate'):
            start_date = post.get('startdate')
            end_date = post.get('enddate')
        elif post.get('startdate') and not post.get('enddate'):
            start_date = post.get('startdate')
        elif not post.get('startdate') and post.get('enddate'):
            end_date = post.get('enddate')

        # Check if a preset range was chosen
        elif post.get('timelength') == 'past7days':
            start_date = today - timedelta(days=7)
        elif post.get('timelength') == 'past30days':
            start_date = today - timedelta(days=30)
        elif post.get('timelength') == 'past60days':
            start_date = today - timedelta(days=60)
        elif post.get('timelength') == 'past90days':
            start_date = today - timedelta(days=90)
        elif post.get('timelength') == 'past365days':
            start_date = today - timedelta(days=365)
        elif post.get('timelength') == 'thisweek':
            start_date = today - timedelta(days=today.weekday())
        elif post.get('timelength') == 'thismonth':
            start_date = date(today.year, today.month, 1)
        elif post.get('timelength') == 'thisyear':
            start_date = date(today.year, 1, 1)

        # Generate the report
        new_report = Report.objects.create(user=request.user,
                                           description=post.get('description'))
        new_report.createExcelFile(start_date, end_date, company, item_id, title)
        new_report.save()

        template = 'forward.html'
        response = {
            'success_message': "Report successfully generated",
            'title': 'Successful',
            'fwd_page': '/reports/'
        }

        # Render error and delete report if the file wasn't created
        if not new_report.rfile:
            new_report.delete()
            response = {
                'error_message': "No requests matched your criteria for the Report",
                'title': 'Error: Could not generate report',
                'fwd_page': '/reports/'
            }

        return render_to_response(template, response,
                                  context_instance=RequestContext(request))

    response = {
        'report_list': Report.objects.all().order_by('id').reverse(),
        'company_list': Item.objects.values_list('company', flat=True).distinct(),
        'item_list': Item.objects.all()
    }
    return render_to_response('reports.html', response,
                              context_instance=RequestContext(request))


def delete_report(request, report_id):
    """Delete an Excel report"""
    # Display login page and error if not logged in as staff
    if not request.user.is_authenticated() or not request.user.is_staff:
        error_response = {'error_message': 'Only Admins can delete reports.'}
        return render_to_response('auth.html', error_response,
                                  context_instance=RequestContext(request))

    report = Report.objects.get(pk=report_id)
    report.delete()

    template = 'forward.html'
    response = {
        'success_message': "Report successfully deleted",
        'title': 'Successful',
        'fwd_page': '/reports/'
    }
    return render_to_response(template, response,
                              context_instance=RequestContext(request))


def login_user(request):
    """Log in using custom login page"""
    username = password = ''

    msg_type = 'message'
    msg_text = "Please log in using the form below."
    template = 'auth.html'

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
        'fwd_page': '/'
    }

    return render_to_response(template, response,
                              context_instance=RequestContext(request))


def logout_user(request):
    """Log the user out and redirect them to the app root"""
    logout(request)
    template = 'forward.html'
    response = {
        'success_message': "You've been successfully logged out!",
        'title': 'log out',
        'fwd_page': '/'
    }
    return render_to_response(template, response,
                              context_instance=RequestContext(request))
