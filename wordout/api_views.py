from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import simplejson
from django.db.models import Max

from wordout.forms import *
from wordout.models import *
from wordout.lib import get_api_metaset


#i tried to have the following function in lib.py but it wouldn't work. not sure why.
def get_customer_by_api_key(api_key):
    customer = ''
    result = ''
    try:
        customer = Customer.objects.get(api_key=api_key)
    except:
        result = get_api_metaset('failed', 'invalid api key')
    return (customer, result)

##### APIDOC #####
@login_required
def apidoc_overview_page(request):
    customer = Customer.objects.get(user=request.user)
    api_key = customer.api_key
    return render_to_response('api_overview.html', dict(api_key=api_key), context_instance=(RequestContext(request)))

##### actual api request ####
def api_do_action_page(request, api_key):
    #all data valid?
    #api matches a user?
    #click sent maches a click?
    #click belongs to the user?
    status = 'failed'
    wocid = request.GET.get('wocid', '')
    if not wocid:
        message = 'missing wordout click id.'
        result = get_api_metaset(status, message) #return httpresponse of a json with fail message
        return HttpResponse(simplejson.dumps(result), 'application/javascript')

    action_type_identifier = request.GET.get('action_type_identifier', '')
    if not action_type_identifier:
        message = 'missing action type identifier.'       
        result = get_api_metaset(status, message) #return httpresponse of a json with fail message
        return HttpResponse(simplejson.dumps(result), 'application/javascript')

    extra_data = request.GET.get('extra_data', '')
    
    form = DoActionForm({
        'click_id':wocid,
        'action_type_identifier':action_type_identifier,
        'extra_data':extra_data
        })
    if form.is_valid():
        data = form.cleaned_data
        customer, result = get_customer_by_api_key(api_key) 
        if result:
            return HttpResponse(simplejson.dumps(result), 'application/javascript')
        
        try: #is the click_id valid
            click = Click.objects.get(id=data['click_id'])
        except Click.DoesNotExist:
            result = get_api_metaset(status, 'invalid wordout click id') #return httpresponse of a json with fail message
            return HttpResponse(simplejson.dumps(result), 'application/javascript')
        
        try: #is the action_type_identifier valid?
            action_type = Action_Type.objects.get(customer = customer, customer_action_type_identifier = data['action_type_identifier'])
        except Action_Type.DoesNotExist:
            message = 'invalid action type identifier'
            result = get_api_metaset(status, message) #return httpresponse of a json with fail message
            return HttpResponse(simplejson.dumps(result), 'application/javascript')
        
        if action_type.enabled == False:
            message = 'this action type is disabled'
            result = get_api_metaset(status, message)
            return HttpResponse(simplejson.dumps(result), 'application/javascript')

        if click.sharer.customer != customer:
            #does the click id belong to this customer
            message = 'invalid wordout click id for this api_key'
            result = get_api_metaset(status, message) #return httpresponse of a json with fail message
            return HttpResponse(simplejson.dumps(result), 'application/javascript')
        else:
            try:
                action = customer.api_add_action(click = click, action_type = action_type, extra_data = data['extra_data'])
            except:
                messasge = 'service is not available.'
                result = get_api_metaset(status, message) #return httpresponse of a json with fail message
                return HttpResponse(simplejson.dumps(result), 'application/javascript')
            else:
                #succeded
                status = 'OK'
                message = 'The action is recorded.'
                result = get_api_metaset(status, message)
                return HttpResponse(simplejson.dumps(result), 'application/javascript')

    #failed
    message = 'Invalid data sent.'
    result = get_api_metaset(status, message)
    return HttpResponse(simplejson.dumps(result), 'application/javascript')


def api_add_sharer_page(request, api_key):
    status = 'failed'
    redirect_link = request.GET.get('redirect_link', '')
    if not redirect_link:
        message = 'redirect link is required'
        result = get_api_metaset(status, message)
        return HttpResponse(simplejson.dumps(result), 'application/javascript')

    form = AddSharerForm({
        'redirect_link':redirect_link
        })
    
    if form.is_valid():
        data = form.cleaned_data
        customer, result = get_customer_by_api_key(api_key)
        if result:
            return HttpResponse(simplejson.dumps(result), 'application/javascript')

        next_customer_sharer_identifier = Sharer.objects.filter(customer=customer).aggregate(current_identifier=Max('customer_sharer_identifier'))['current_identifier'] + 1
        
        try: 
            customer.create_sharer(start = next_customer_sharer_identifier, end = next_customer_sharer_identifier, redirect_link = data['redirect_link'])
        except:
            message = 'the service is not avaible.'
            result = get_api_metaset(status, message)
            return HttpResponse(simplejson.dumps(result), 'application/javascript')

        status = 'OK'
        message = 'The new sharer is added'
        result = get_api_metaset(status, message)
        result['response'] = {
                'new_sharer_identifier':next_customer_sharer_identifier, 
                'code': code,
                'redirect_link': redirect_link.host.host_name + redirect_link.path
                }
        return HttpResponse(simplejson.dumps(result), 'application/javascript')
    result = get_api_metaset(status, 'invalid redirect link sent. You need match the format: http(s)://subdomain.example.com/(path)')
    return HttpResponse(simplejson.dumps(result), 'application/javascript')

def api_toggle_sharer_page(request, api_key):
    #call it enable instead of enabled.
    enabled = request.GET.get('enabled', '')
    if not enabled:
        message = 'status is required.'
        result = get_api_metaset('failed', message)
        return HttpResponse(simplejson.dumps(result), 'application/javascript')

    customer_sharer_identifier = request.GET.get('sharer_identifier', '')
    if not customer_sharer_identifier:
        message = 'sharer identifier is required.'
        result = get_api_metaset('failed', message)
        return HttpResponse(simplejson.dumps(result), 'application/javascript')

    form = ToggleSharerForm({
        'customer_sharer_identifier':customer_sharer_identifier,
        'enabled':enabled
        })

    if form.is_valid():
        #customer_sharer_identifier is one of them
        data = form.cleaned_data
        customer, result = get_customer_by_api_key(api_key)
        if result:
            return HttpResponse(simplejson.dumps(result), 'application/javascript')
        customer_sharer_identifier = data['customer_sharer_identifier']
        enabled = data['enabled']

        try:
            sharer = Sharer.objects.get(customer=customer, customer_sharer_identifier = customer_sharer_identifier)
        except Sharer.DoesNotExist:
            message = 'invalid sharer identifier.'
            result = get_api_metaset('failed', message)
            return HttpResponse(simplejson.dumps(result), 'application/javascript')
        sharer.enabled=enabled
        sharer.save()
        status = 'OK'
        message = 'the identifier is toggled.'
        result = get_api_metaset(status, message)
        result['response'] = {
                'sharer_identifier': sharer.customer_sharer_identifier,
                'enabled': enabled
                }
        return HttpResponse(simplejson.dumps(result), 'application/javascript')
    result = get_api_metaset('failed', 'invalid data sent.')
    return HttpResponse(simplejson.dumps(result), 'application/javascript')
        
def api_get_action_type_page(request, api_key):
    customer, result = get_customer_by_api_key(api_key)
    if result:
        return HttpResponse(simplejson.dumps(result), 'application/javascript')
    action_type_ls = Action_Type.objects.filter(customer = customer)
    status = 'OK'
    message = 'your action type is listed.'
    result = get_api_metaset(status, message)
    result['response'] = []
    holder = {}
    for i in action_type_ls:
        holder['action_type_identifier'] = i.customer_action_type_identifier
        holder['action_name'] = i.action_name
        holder['description'] = i.description
        holder['enabled'] = i.enabled
        result['response'].append(holder)
    return HttpResponse(simplejson.dumps(result), 'application/javascript')

def api_get_all_sharers_page(request, api_key):
    customer, result = get_customer_by_api_key(api_key)
    if result:
        return HttpResponse(simplejson.dumps(result), 'application/javascript')

    ls = customer.display_sharers()
    status = 'OK'
    message = 'query succeed.'
    result = get_api_metaset(status, message)
    result['response'] = ls
    return HttpResponse(simplejson.dumps(result), 'application/javascript')


