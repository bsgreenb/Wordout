from django.shortcuts import render_to_response
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.template import RequestContext
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.auth import authenticate, login as auth_login
from wordout.forms import *
from wordout.models import *
from wordout.lib import force_subdomain


def main_page(request):
    return render_to_response(
            'main_page.html',
            dict(user=request.user)
        )

def direct_page(request, code):
    '''
    referrer = request.META['HTTP_REFERER']
    result = urlparse(referrer)
    path = result.path
    netloc = result.netloc
    m = re.compile(r'^[a-zA-Z0-9\-\.]+\.[a-zA-Z0-9\-\.]+\.(com|org|net|mil|edu|COM|ORG|NET|MIL|EDU)$')
    search = m.search(html)
    if not search:
        netloc = 'www.' + netloc
    
    user_agent = request.META['HTTP_USER_AGENT']
    ip = request.META['REMOTE_ADDR']
    '''

    try:
        identifier = Identifiers.objects.get(code = code)
        redirect_link = identifier.redirect_link
    except Identifiers.DoesNotExist:
        return HttpResponseRedirect('/')


    if not request.META.get('HTTP_REFERER', ''):
        referrer = None
    else:
        referrer = request.META['HTTP_REFERER']
        referrer, created = get_or_create_link(referrer)

    if not request.META.get('HTTP_USER_AGENT', ''):
        user_agent = None
    else:
        user_agent = request.META['HTTP_USER_AGENT']
        user_agent, created = User_Agent.objects.get_or_create(agent = user_agent)

    if not request.META.get('REMOTE_ADDR', ''):
        ip = None
    else:
        ip = request.META['REMOTE_ADDR']
        ip, created = IP.objects.get_or_create(address = ip)

    Request.objects.create(referral_code = identifier, redirect_link = redirect_link, referrer = referrer, IP = ip, Agent = user_agent)
    
    return HttpResponseRedirect(redirect_link)

    
    
    
    
    
    
def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')

def register_page(request):

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
    else:
        form = RegistrationForm()
    return render_to_response('registration/register.html', dict(form = form), context_instance=RequestContext(request))

