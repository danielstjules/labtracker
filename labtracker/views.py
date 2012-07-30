from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login

def user_login(request):
	username = request.POST['username']
	password = request.POST['password']
	user = authenticate(username = username, password = password)
	if user is not None:
		if user.is_active:
			login(request, user)
			# redirect to some legit website here. don't know how to do this yet - vlad
		else:
			# let the user know his account was disabled, don't know how to do this yet - vlad
	else:
		# display an error message for an invalid username or password. 