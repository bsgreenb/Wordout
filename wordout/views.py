from django.shortcuts import render_to_response
from django.contrib.auth import logout
from django.contrib.auth.models import User
from wordout.forms import *
from django.template import RequestContext
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.auth import authenticate, login as auth_login

def main_page(request):
    return render_to_response(
            'main_page.html',
            dict(user=request.user)
        )

def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')

def register_page(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password1'],
                    email=form.cleaned_data['email']
                     )
            new_user = authenticate(username=request.POST['username'], password=request.POST['password1'])
            auth_login(request, new_user)
            return HttpResponseRedirect('/')
    
    form = RegistrationForm()
    return render_to_response('registration/register.html', dict(form = form), context_instance=RequestContext(request))
