from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.db import transaction #commit_on_success to create sharer view so it runs query only once.
from django.utils import simplejson

from wordout.forms import *
from wordout.models import *
from wordout.lib import get_ip, code_generator
from wordout.lib import check_session_form  #I store form error in session['form'] this function is to return the form that includes error


##### SYSTEM RELATED #####

@login_required
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
            #this is not the best practice. I forced extra query here.  change on version 2
            #I need create/check both client_id and api_key
            while True:
                client_key = code_generator(9)
                api_key = code_generator(30)
                try:
                    Customer.objects.get(client_key = client_key)
                except Customer.DoesNotExist:
                    try:
                        Customer.objects.get(api_key = api_key)
                    except Customer.DoesNotExist:
                        break
            free_group = Customergroup.objects.get(id=1)
            Customer.objects.create(user=user, client_key = client_key, api_key = api_key, customergroup=free_group )
            new_user = authenticate(username=request.POST['username'], password=request.POST['password1'])
            auth_login(request, new_user)
            return HttpResponseRedirect('/')
    else:
        form = RegistrationForm()
    return render_to_response('registration/register.html', dict(form = form), context_instance=RequestContext(request))

##### SHARER #####

RESULTS_PER_PAGE = 20

def main_page(request):
    if request.user.is_authenticated():
        form = DisplaySharerForm(request.GET)  # validation is in the form
        if form.is_valid():
            order_by = form.cleaned_data['order_by']
            desc = form.cleaned_data['desc']
            action_type_id = form.cleaned_data['action_type_id']
            page_number = form.cleaned_data['page_number']
            customer_sharer_identifier = forms.cleaned_data['customer_sharer_identifier']

            customer = Customer.objects.get(user = request.user)
            ls = customer.display_sharers(
                customer_sharer_identifier = customer_sharer_identifier,
                order_by = order_by,
                desc = desc,
                action_type_id = action_type_id,
                page_number = page_number,
                results_per_page = RESULTS_PER_PAGE
            )

            # next is to have a list of dicts that I can loop through to give the sorting url and header
            sort_links = [
                {'order_by':'customer_sharer_identifier','display_name':'Sharer_ID'},
                {'order_by':'redirect_link', 'display_name':'link'},
                {'order_by':'enabled', 'display_name':'Enable'},
                {'order_by':'click_total', 'display_name':'Clicks'}
            ]

        for action_type in ls[0]['action_type_set']: # complete the sort links
            sort_links.append({
                'order_by':'action_count',
                'display_name':action_type['action_name'],
                'action_type_id': action_type['action_type_id'],
            })

        # NOW, I set urls
        for item in sort_links:
            url = '/?order_by=%s&desc=%s'

            toggle_desc = 'true'
            if desc == 'true':  # switch desc, asc
                toggle_desc = 'false'

            if item['order_by'] == order_by: # test whether I need switch desc, asc
                url = url % (order_by, toggle_desc)
            else:
                url = url % (item['order_by'], 'true')

            if item['action_type_id']:
                url = url + '&action_type_id=' + item['action_type_id']

            item['sort_url'] = url

        #get default start value for create numeric identifiers
        try:
            last = Sharer.objects.filter(customer = customer).order_by('-created')[0]
            last = last.customer_sharer_identifier
        except IndexError:
            last = 0

        default_start = last + 1

        form = check_session_form(request) # this is used to display form errors. the function will take the form and remove it from the session.
        return render_to_response('sharer.html', dict(ls=ls, sort_links=sort_links, default_start = default_start, form = form), context_instance=RequestContext(request))

    else:
        form = RegistrationForm()
    return render_to_response(
                'main_page.html', dict(form=form),
                context_instance=RequestContext(request))

@login_required
def show_referrer_by_sharer(request, customer_sharer_identifier): #show where the clicks come from by each sharer. we display this in a modal when the client clicks "detail"
    customer = Customer.objects.get(user = request.user)
    data = customer.display_referrer_by_sharer(customer_sharer_identifier)
    results = {}
    if data:
        results['success'] = True
        results['response'] = data 
    else:
        results['success'] = False
    return HttpResponse(simplejson.dumps(results), 'application/javascript')
    
@login_required
@transaction.commit_on_success
def create_sharer_page(request):
    if request.method == 'POST':
        form = CreateSharerForm(user=request.user, data=request.POST)
        if form.is_valid():
            start = form.cleaned_data['start']
            end = form.cleaned_data['end']
            redirect_link = form.cleaned_data['redirect_link']
            customer = Customer.objects.get(user = request.user) #this has to be changed in version 2 when we combine User and Customer
            data = customer.create_sharer(start, end, redirect_link)
        else:
            request.session['form'] = form
    return HttpResponseRedirect('/')

@login_required
def change_redirect_link_page(request):
    if request.is_ajax():
        form = ChangeLinkForm(user = request.user, data = request.POST)
        if form.is_valid():
            sharer_ls = request.POST['sharer_ls']
            if sharer_ls != 'ALL':
                sharer_ls = sharer_ls[:-1].split(',') # create a list
            redirect_link = form.cleaned_data['redirect_link']
            customer = Customer.objects.get(user=request.user)
            try:
                customer.change_redirect_link(redirect_link, sharer_ls)
            except AttributeError: #invalid sharer ls
                error = 'invalid sharer list'
                return HttpResponse(simplejson.dumps({
                    'status':'fail',
                    'error':error
                }))
            results = {
                'status':'OK',
                'redirect_link':redirect_link
            }
            return HttpResponse(simplejson.dumps(results))
        else:
            error = 'invalid redirect link'
    else:
        error = 'invalid request'
    return HttpResponse(simplejson.dumps({
        'status':'fail',
        'error':error
    }))

@login_required
def disable_or_enable_sharer_page(request, action):
    if request.is_ajax():
        sharer_ls = request.POST['sharer_ls']
        if sharer_ls != 'ALL':
            sharer_ls = sharer_ls[:-1].split(',')
        customer = Customer.objects.get(user=request.user)
        if action == 'disabled':
            try:
                customer.disable_or_enable_sharer(sharer_ls, False)
            except AttributeError:
                return HttpResponse(simplejson.dumps({
                    'status':'fail'
                }))
        if action ==  'enabled':
            try:
                customer.disable_or_enable_sharer(sharer_ls, True)
            except AttributeError:
                return HttpResponse(simplejson.dumps({
                    'status':'fail'
                    }))
        return HttpResponse(simplejson.dumps({
            'status':'OK',
            'enable_text': action
        }))
    return HttpResponse(simplejson.dumps({
        'status':'fail'
    }))


##### PLUGIN PAGE #####
@login_required
def sharer_plugin_page(request):
    # this is the config page.

    customer = Customer.objects.select_related().get(user=request.user)
    customer_sharer_ls = customer.sharer_set.all()
    client_key = customer.client_key
    message_title = customer.message_title
    message_body = customer.message_body
    form = check_session_form(request)
    return render_to_response('plugin_page.html', dict(customer_sharer_ls=customer_sharer_ls, client_key=client_key, message_title=message_title, message_body=message_body, form=form), context_instance=RequestContext(request))

@login_required
def edit_msg_page(request):
    if request.method == 'POST':
        customer = Customer.objects.get(user=request.user)
        form = MessageForm(request.POST)
        if form.is_valid():
            customer.update_title_and_body(form.cleaned_data['message_title'], form.cleaned_data['message_body'])
        else:
            request.session['form'] = form

    return HttpResponseRedirect('/pluginpage/')

def display_sharer_plugin_page(request, client_key, sharer_identifier):
    # this is the actual promote page the customers link on their websites

    try:
        customer = Customer.objects.get(client_key = client_key, sharer__customer_sharer_identifier = sharer_identifier)
    except Customer.DoesNotExist:
        return Http404

    sharer_detail = customer.display_sharers(sharer_identifier = sharer_identifier)
    message_title = customer.message_title
    message_body = customer.message_body
    return render_to_response('display_plugin_page.html', dict(sharer_detail = sharer_detail, message_title = message_title, message_body = message_body), context_instance = RequestContext(request))


##### ACTION #####
@login_required
def action_type_page(request):
    customer = Customer.objects.get(user=request.user)
    action_type_ls = customer.action_type_set.all()
    api_key = customer.api_key

    current_number_actions = customer.action_type_set.all().count()
    if current_number_actions == 0:
        new_action_type_identifier = 1
    else:
        new_action_type_identifier = customer.action_type_set.aggregate(last_customer_action_type_identifier=Max('customer_action_type_identifier'))['last_customer_action_type_identifier'] + 1

    form = check_session_form(request)
    return render_to_response('action_type_page.html', dict(action_type_ls=action_type_ls, api_key=api_key, new_action_type_identifier = new_action_type_identifier, form=form), context_instance=RequestContext(request))

@login_required
def create_action_type_page(request):
    if request.method == 'POST':
        customer = Customer.objects.get(user=request.user)
        form  = ActionTypeForm(user=customer, data=request.POST)
        if form.is_valid():
            customer.create_actiontype(form.cleaned_data['customer_action_type_identifier'], form.cleaned_data['action_name'], form.cleaned_data['action_description'])
        else:
            request.session['form'] = form
    return HttpResponseRedirect('/actiontype')

@login_required
def edit_action_type_page(request):
    if request.method == 'POST':
        customer = Customer.objects.get(user=request.user)
        form = ActionTypeForm(user=customer, data=request.POST)
        if form.is_valid():
            customer.edit_actiontype(form.cleaned_data['customer_action_type_identifier'], form.cleaned_data['action_name'], form.cleaned_data['action_description'])
        else:
            request.session['form'] = form
    return HttpResponseRedirect('/actiontype')

@login_required
def disable_or_enable_action_page(request, action):
    if request.method == 'POST':
        action_type_ls = request.POST['action_type_ls'][:-1].split(',')
        customer = Customer.objects.get(user=request.user)
        if action == 'disable':
            customer.disable_or_enable_action(action_type_ls, False)
        if action == 'enable':
            customer.disable_or_enable_action(action_type_ls, True)
    return HttpResponseRedirect('/actiontype')

@login_required
def referrer_page(request):
    customer = Customer.objects.get(user=request.user)
    #figure out the best way to add start and end variables
    ls = customer.display_referrer()
    return render_to_response('referrer.html', dict(ls=ls), context_instance=RequestContext(request))

@login_required
def path_page(request, host_id):
    customer = Customer.objects.get(user=request.user)
    ls = customer.display_path(host_id)
    results = {}
    if ls:
        results['success'] = True
        results['data'] = ls
    else:
        results['success'] = False
    return HttpResponse(simplejson.dumps(results), 'application/javascript')

def share_page(request, client_key, sharer_identifier):
    #need completely construct this page.
    try:
        customer = Customer.objects.get(client_key = client_key, sharer__customer_sharer_identifier = sharer_identifier)
    except Customer.DoesNotExist:
        return HttpResponseRedirect('/')

    ls = customer.display_sharers(sharer_identifier = sharer_identifier)

    message_title = customer.message_title
    message_body = customer.message_body

    return render_to_response('plugin_page.html', dict(ls= ls, message_title = message_title, message_body = message_body), context_instance = RequestContext(request))

def direct_page(request, code):
    try:
        sharer = Sharer.objects.get(code = code)
        redirect_link = sharer.redirect_link
    except Sharer.DoesNotExist:
        return HttpResponseRedirect('/')

    if request.META.get('HTTP_REFERER', ''):
        referrer_form = ValidateReferrer({'referrer':request.META['HTTP_Referrer']})
        if referrer_form.is_valid():
            referrer, created = get_or_create_link(referrer_form.cleaned_data['referrer'])
        else:
            referrer = None
    else:
        referrer = None

    if not request.META.get('HTTP_USER_AGENT', ''):
        user_agent = None
    else:
        user_agent = request.META['HTTP_USER_AGENT']
        user_agent, created = User_Agent.objects.get_or_create(agent = user_agent)
    
    ip = get_ip(request)
    if ip:
        ip_form = ValidateIP({'ip':ip})
        if ip_form.is_valid():
            ip, created = IP.objects.get_or_create(address = ip)

    click = Click.objects.create(sharer = sharer, redirect_link = redirect_link, referrer = referrer, IP = ip, Agent = user_agent)
    url = '%s?wdcid=%s' % (redirect_link, click.id)
    return HttpResponseRedirect(url)
