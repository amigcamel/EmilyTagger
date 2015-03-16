# -*-coding:utf-8-*-
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm


def signin(request):
    if request.method == 'POST':
        auth_form = AuthenticationForm(data=request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if auth_form.is_valid():
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect(reverse('index'))
                else:
                    pass
                    # Return a 'inactive user' error message
            else:
                pass
                # Return a 'disabled account' error message
    else:
        auth_form = AuthenticationForm()
    return render_to_response('signin.html', {'auth_form': auth_form}, context_instance=RequestContext(request))


def signout(request):
    logout(request)
    return redirect(reverse('index'))
