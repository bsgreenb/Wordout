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
    except Customer.DoesNotExist:
        result = get_api_metaset('failed', 'invalid api key')
    return (customer, result)

##### APIDOC #####  this is just the instruction.
@login_required
def apidoc_overview_page(request):
    api_key = Customer.objects.get(user=request.user).api_key
    return render_to_response('apidoc/apidoc_overview.html', dict(api_key=api_key), context_instance=RequestContext(request))

def apidoc_do_action_page(request):
    return render_to_response('apidoc/apidoc_doaction.html', dict(), context_instance = RequestContext(request))


def apidoc_get_sharer_page(request):
    return render_to_response('apidoc/apidoc_getsharerinfo.html', dict(), context_instance = RequestContext(request))


def apidoc_get_all_sharers_page(request):
    return render_to_response('apidoc/apidoc_getallsharer.html', dict(), context_instance = RequestContext(request))


def apidoc_toggle_sharer(request):


    return render_to_response('apidoc/apidoc_togglesharer.html', dict(), context_instance = RequestContext(request))



def apidoc_get_action_type(request):


    return render_to_response('apidoc/apidoc_getactiontype.html', dict(), context_instance = RequestContext(request))



##### actual api request ####
def api_do_action_page(request, api_key):
    #all data valid?
    #api matches a user?
    #click sent is a real click?
    #click belongs to the user?
    status = 'failed'
    wocid = request.GET.get('wocid', '')
    if not wocid:
        message = 'missing wordout click id.'
        result = get_api_metaset(status, message) #return httpresponse of a json with fail message
        return HttpResponse(simplejson.dumps(result), 'application/javascript')

    action_type_identifier = request.GET.get('action_type_identifier', '') # sent 1, 2, 3
    if not action_type_identifier:
        message = 'missing action type identifier.'       
        result = get_api_metaset(status, message)
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
        if result:  # result is true means the user doesn't exist
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
            message = 'invalid wordout click id for this customer'
            result = get_api_metaset(status, message)
            return HttpResponse(simplejson.dumps(result), 'application/javascript')
        else:
            try:
                action = customer.api_add_action(click = click, action_type = action_type, extra_data = data['extra_data'])
            except: #TODO give right catch here.
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


def api_get_sharer_page(request, api_key):
    status = 'failed'
    sharer_identifier = request.GET.get('sharer_identifier', '')
    if not sharer_identifier:
        message = 'sharer identifier is required'
        result = get_api_metaset(status, message)
        return HttpResponse(simplejson.dumps(result), 'application/javascript')

    form = AddSharerForm({
        'customer_sharer_identifier': sharer_identifier
        })

    if form.is_valid():
        customer, result = get_customer_by_api_key(api_key)
        if result:
            return HttpResponse(simplejson.dumps(result), 'application/javascript')
        
        try:
            sharer = customer.sharer_set.select_related().get(customer_sharer_identifier=form.cleaned_data['customer_sharer_identifier']) # sharer is already inserted. get the sharer info
            status = 'OK'
            message = 'get the sharer info'
        except: #TODO not sure what catch error should be here. DoesNotExist is not working.
            sharer = customer.create_sharer(customer_sharer_identifier = form.cleaned_data['customer_sharer_identifier'], redirect_link = customer.redirect_link)
            status = 'OK'
            message = 'The new sharer is added'

        result = get_api_metaset(status, message)
        data = customer.display_sharers(customer_sharer_identifier = sharer.customer_sharer_identifier)  # get the sharer's info.
        result['response'] = data
        return HttpResponse(simplejson.dumps(result), 'application/javascript')

    else:
        result = get_api_metaset(status, 'the sharer identifier is not valid. it has to be integers or characters')
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

    total_number_of_sharers = customer.sharer_set.count() # this is sent as results_per_page.

    ls = customer.display_sharers(results_per_page=total_number_of_sharers)
    status = 'OK'
    message = 'query succeed.'
    result = get_api_metaset(status, message)
    result['response'] = ls
    return HttpResponse(simplejson.dumps(result), 'application/javascript')

def api_get_sharer_by_identifier(request, api_key):
    #i repeat myself with api_toggle_sharer_page.
    customer, result = get_customer_by_api_key(api_key)
    if result:
        return HttpResponse(simplejson.dumps(result), 'application/javascript')

    status = 'failed'
    sharer_identifier = request.GET.get('sharer_identifier', '')
    if not sharer_identifier:
        message = 'sharer identifier is required.'
        result = get_api_metaset(status, message)
        return HttpResponse(simplejson.dumps(result), 'application/javascript')

    form = GetSharerByIdForm({
        'customer_sharer_identifier':sharer_identifier
    })

    if form.is_valid():
        data = form.cleaned_data
        try:
            Sharer.objects.get(customer = customer, customer_sharer_identifier = data['customer_sharer_identifier'])
        except Sharer.DoesNotExist:
            message = 'invalid sharer identifier.'
            result = get_api_metaset(status, message)
            HttpResponse(simplejson.dumps(result), 'application/javascript')

        ls = customer.display_sharers(customer_sharer_identifier = data['customer_sharer_identifier'])
        status = 'OK'
        message = 'query succeed.'
        result = get_api_metaset(status, message)
        result['response'] = ls
        return HttpResponse(simplejson.dumps(result), 'application/javascript')