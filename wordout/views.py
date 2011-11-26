from django.shortcuts import render_to_response
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.template import RequestContext
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from wordout.forms import *
from wordout.models import *
from wordout.lib import force_subdomain


def main_page(request):
    return render_to_response(
            'main_page.html',
            dict(user=request.user)
        )


@login_required
def create_numeric_page(request):
    '''
    if the request is post, i go into form, validate it and the customer will save those identifiers and redirect into the main page
    if not, 
    we display the form. start should be a default
    '''
    if request.method == 'POST':
        form = NumericIdenForm(request.POST)
        if form.is_valid():
            start = form.cleaned_data['start']
            end = form.cleaned_data['end']
            redirect_link = form.cleaned_data['redirect_link']
            customer = Customer.objects.get(user = request.user) #this has to be changed in version 2 when we combine User and Customer
            customer.numeric_ident_save(start, end, redirect_link)
            return HttpResponseRedirect('/')
    
    try:
        last = Identifiers.objects.filter(customer = request.user, identifier_type = 1).order_by('-created')[0]
        last = int(last.identifier)
    except IndexError:
        last = 0

    form = NumericIdenForm(initial={'start':last+1})
    return render_to_response('create_numeric.html', dict(form=form), context_instance=RequestContext(request))



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

