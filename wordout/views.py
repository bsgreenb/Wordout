from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout  #We want to avoid overriding our own login function
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.db import transaction #commit_on_success to create sharer view so it runs query only once.
from django.utils import simplejson

from wordout.forms import *
from wordout.models import *
from wordout.lib import get_ip, code_generator
from wordout.lib import get_previous_form  #I store form error in session['form'] this function is to return the form that includes error


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

            # We make sure that the code hasn't been taken
            while True:
                client_key = code_generator(9)
                api_key = code_generator(30)
                try:
                    Customer.objects.get(client_key = client_key)
                    Customer.objects.get(api_key = api_key)
                except Customer.DoesNotExist:
                    break

            FREE_GROUP = 1 #ID of the Free Users group.  This is what everyone will be during private beta.
            Customer.objects.create(user=user, client_key = client_key, api_key = api_key, customer_group=FREE_GROUP)
            new_user = authenticate(username=request.POST['username'], password=request.POST['password1'])

            #Since everything worked, log them in and send them to the main page.
            auth_login(request, new_user)
            return HttpResponseRedirect('/')

        #TODO: We currently don't show errors in the template, we just return register.html again.
    else:
        form = RegistrationForm()

    return render_to_response('registration/register.html', dict(form = form), context_instance=RequestContext(request))

##### SHARER #####

#TODO: Bug fix.. let's see if SO can get it.
#TODO: See Rui's recent commits
#TODO: Probably make customer_sharer_identifier + customer_id unique_together (read docs on that first tho)
def main_page(request):

    if request.user.is_authenticated():
        customer = Customer.objects.select_related().get(user = request.user)

        if customer.sharer_set.count() == 0 and customer.redirect_link == None: # no sharer and referral program is not set up yet.
            return HttpResponseRedirect('/pluginpage')

        form = DisplaySharerForm(request.GET)  # validation is in the form
        if form.is_valid():

            RESULTS_PER_PAGE = 20
            order_by = form.cleaned_data['order_by']
            direction = form.cleaned_data['direction']
            action_type_id = form.cleaned_data['action_type_id']
            page_number = int(form.cleaned_data['page_number'])

            ls = customer.display_sharers(
                order_by = order_by,
                direction = direction,
                action_type_id = action_type_id,
                page_number = page_number,
                results_per_page = RESULTS_PER_PAGE
            )


            if not ls:
                total_sharer_count = 0 #This is where they're going to begin
                return render_to_response('sharer.html', dict(total_sharer_count = total_sharer_count), context_instance=RequestContext(request))
            else:
                total_sharer_count = customer.sharer_set.count()   # sort by customer_sharer_identifier is the same as sort by created
                # next is to have a list of dicts that I can loop through to give the sorting url and header

                sort_links = [
                        {'order_by':'customer_sharer_identifier','display_name':'sharer_id'},
                        {'order_by':'redirect_link', 'display_name':'link'},
                        {'order_by':'click_total', 'display_name':'visits'}
                ]

                #This completes the header row, by inspecting the first result
                for action_type in ls[0]['action_type_set']:
                    sort_links.append({
                        'order_by':'action_count',
                        'display_name':action_type['action_name'],
                        'action_type_id': action_type['action_type_id'],
                        })

                sort_links.append({'order_by':'enabled', 'display_name':'enabled'}) #Add the reset of the header row

                # Django complains when these aren't set in advance
                next_page_url = None
                previous_page_url = None
                display_end = None
                display_start = None

                for sort_link in sort_links:
                    url = '/?order_by=' + sort_link['order_by']

                    if sort_link['order_by'] == 'action_count':
                        url +='&action_type_id=' + str(sort_link['action_type_id'])

                    #Something is always being sorted on, so this if will always be run at least once.  That's why we can assume that our pagination stuff is done there.
                    if sort_link['order_by'] == order_by and (sort_link['order_by'] != 'action_count' or sort_link['action_type_id'] == action_type_id): #If this is the one currently being sorted on...
                        #Toggle the direction and show the right header
                        if direction == 'DESC':
                            url += '&direction=ASC'
                            sort_link['header_arrow'] = 'headerSortUp'
                        else:
                            url += '&direction=DESC'
                            sort_link['header_arrow'] = 'headerSortDown'

                        #After we set the url stuff specifically for this (selected) one, we need to set the pagination URLs based on it...
                        base_page_url = url + '&direction=' + direction + '&page_number='

                        if (page_number * RESULTS_PER_PAGE) >= total_sharer_count: #it's the last page
                            next_page_url = None
                        else:
                            next_page_url = base_page_url + str(page_number + 1)

                        if page_number > 1:
                            previous_page_url = base_page_url + str(page_number - 1)
                        else: #It's the first page
                            previous_page_url = None

                        display_end = min(page_number * RESULTS_PER_PAGE, total_sharer_count) #we use min() to insure that it doesn't assume the final page is a full one.
                        display_start = (page_number - 1) * RESULTS_PER_PAGE + 1
                    else:
                        url += '&direction=DESC'

                    url += '&page_number=1' #Sort links will always reset the pg number to 1.  We don't do this earlier so we don't mess up the pagination code above.

                    sort_link['sort_url'] = url

                form = get_previous_form(request) # this gets the form from the session var created by the modal dialogue, then discards the session so refresh doesn't cause an issue.

                # EXPLAIN RETURN VARS:
                # sort_links are used to display table headers plus the sort urls
                # ls is the sharer contents
                # default_start is used for pop out form to create sharers
                # previous_page_url and next_page_url are used for previous page and next page
                # passed_page_number is used to disable previous page if it is equal to 0
                # display_start and display_end are used to fill x - x of xxxx
                #return HttpResponse(sort_links)
                return render_to_response('sharer.html', dict(ls=ls, sort_links=sort_links, total_sharer_count = total_sharer_count, previous_page_url = previous_page_url, next_page_url = next_page_url, display_start = display_start, display_end=display_end, form = form), context_instance=RequestContext(request))
        else:
            request.session['form'] = form
            return HttpResponseRedirect('/') #Redirect to the main page w/o invalid parameters
    else:
        form = RegistrationForm()
        return render_to_response('landing_page.html', dict(form=form), context_instance=RequestContext(request))

@login_required
def show_referrer_by_sharer(request, customer_sharer_identifier): #show where the clicks come from by each sharer. we display this in a modal when the client clicks "detail"
    customer = Customer.objects.get(user = request.user)
    data = customer.display_referrers_for_sharer(customer_sharer_identifier)
    results = {}
    if data:
        results['success'] = True
        results['response'] = data 
    else:
        results['success'] = False
    return HttpResponse(simplejson.dumps(results), 'application/javascript')

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
def disable_or_enable_page(request, action, function):  # this is used on four pages: enable/disable sharers and enable/disable actions
    if request.is_ajax():
        ls = request.POST['ls']
        if ls != 'ALL':
            ls = ls[:-1].split(',')
        customer = Customer.objects.get(user=request.user)
        if action == 'disable':
            try:
                if function == 'disable_or_enable_sharer':
                    customer.disable_or_enable_sharer(ls, False)
                elif function == 'disable_or_enable_action':
                    customer.disable_or_enable_action(ls, False)
            except AttributeError:
                return HttpResponse(simplejson.dumps({
                    'status':'fail'
                }))
        if action ==  'enable':
            try:
                if function == 'disable_or_enable_sharer':
                    customer.disable_or_enable_sharer(ls, True)
                elif function == 'disable_or_enable_action':
                    customer.disable_or_enable_action(ls, True)
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
    redirect_link = customer.redirect_link #
    client_key = customer.client_key
    message_title = customer.message_title
    message_body = customer.message_body
    form = get_previous_form(request)
    return render_to_response('plugin_page.html', dict(redirect_link = redirect_link, client_key=client_key, message_title=message_title, message_body=message_body, form=form), context_instance=RequestContext(request))

@login_required
def set_program_page(request):
    if request.method == 'POST':
        customer = Customer.objects.get(user=request.user)
        form = SetProgramForm(request.POST)
        if form.is_valid():
            redirect_link, created = get_or_create_link(form.cleaned_data['redirect_link'])
            customer.update_program(redirect_link, form.cleaned_data['message_title'], form.cleaned_data['message_body'])
        else:
            request.session['form'] = form

    return HttpResponseRedirect('/pluginpage/')

def display_sharer_plugin_page(request, client_key, customer_sharer_identifier):
    # this is the actual promote page the customers link on their websites
    try:
        customer = Customer.objects.select_related().get(client_key = client_key)
    except Customer.DoesNotExist:
        return Http404

    ls = '' # if ls is empty, in templates, I will display example stuff.
    if customer_sharer_identifier != 'example':

        form = AddSharerForm({
            'customer_sharer_identifier':customer_sharer_identifier
        })

        if form.is_valid():
            try:
                sharer = customer.sharer_set.select_related().get(customer_sharer_identifier=form.cleaned_data['customer_sharer_identifier'])
            except: #TODO not sure what catch error should be here. DoesNotExist is not working.
                sharer = customer.create_sharer(customer_sharer_identifier = form.cleaned_data['customer_sharer_identifier'])
        else:  # not a valid sharer identifier
           return HttpResponse('customer sharer identifier needs to be integer or characters.')

        ls = customer.display_sharers(customer_sharer_identifier = customer_sharer_identifier)

    message_title = customer.message_title
    message_body = customer.message_body

    action_types = customer.action_type_set.all()# display action types of this customer for example cases

    # I check whether the ls is empty to decide to show example page. if example page, I use action_types to display the client's action types
    return render_to_response('display_plugin_page.html', dict(ls = ls, message_title = message_title, message_body = message_body, action_types=action_types), context_instance = RequestContext(request))


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

    form = get_previous_form(request)
    return render_to_response('action_type_page.html', dict(action_type_ls=action_type_ls, api_key=api_key, new_action_type_identifier = new_action_type_identifier, form=form), context_instance=RequestContext(request))

@login_required
def create_action_type_page(request):
    if request.method == 'POST':
        customer = Customer.objects.select_related().get(user=request.user)
        next_customer_action_type_identifier = customer.action_type_set.count() + 1
        form  = ActionTypeForm(user=customer, data=request.POST)
        if form.is_valid():
            customer.create_actiontype(next_customer_action_type_identifier, form.cleaned_data['action_name'], form.cleaned_data['action_description'])
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

'''
@login_required
def disable_or_enable_action_page(request, action):
    if request.is_ajax():
        action_type_ls = request.POST['ls'][:-1].split(',')
        customer = Customer.objects.get(user=request.user)
        if action == 'disable':
            try:
                customer.disable_or_enable_action(action_type_ls, False)
            except
        if action == 'enable':
            customer.disable_or_enable_action(action_type_ls, True)
    return HttpResponseRedirect('/actiontype')
'''

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
