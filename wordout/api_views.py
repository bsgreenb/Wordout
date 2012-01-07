from datetime import datetime
from django.shortcuts import render_to_response
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.template import RequestContext
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from wordout.forms import *
from wordout.models import *
from wordout.lib import code_generator, get_api_metaset
from django.utils import simplejson
from django.db.models import Max


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

##### above is for apidoc #####
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
        customer, result = get_customer_by_api_key(api_key) #this function is in lib.py. if customer is there, return customer, otherwise, return api fail metaset.
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
        
        if click.sharer.customer != customer:
            #does the click id belong to this customer
            message = 'invalid wordout click id for this api_key'
            result = get_api_metaset(status, message) #return httpresponse of a json with fail message
            return HttpResponse(simplejson.dumps(result), 'application/javascript')
        else:
            try:
                action = Action.objects.create(click = click, action_type = action_type, extra_data = data['extra_data'])
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
        redirect_link, created = get_or_create_link(data['redirect_link'])
        
        next_customer_sharer_identifier = Sharer.objects.filter(customer=customer).aggregate(current_identifier=Max('customer_sharer_identifier'))['current_identifier'] + 1
        loop = True
        while loop == True:
            code = code_generator()
            try:
                Sharer.objects.get(code=code)
            except Sharer.DoesNotExist:
                loop = False
                sharer = Sharer.objects.create(customer = customer, customer_sharer_identifier = next_customer_sharer_identifier, code = code, redirect_link = redirect_link)
        status = 'OK'
        message = 'The new sharer is added'
        result = get_api_metaset(status, message)
        result['response'] = {
                'new_sharer_identifier':next_customer_sharer_identifier, 
                'code': code,
                'redirect_link': redirect_link.host.host_name + redirect_link.path
                }
        return HttpResponse(simplejson.dumps(result), 'application/javascript')
    else:
        return HttpResponse('aa')
    result = get_api_metaset(status, 'invalid redirect link sent. You need match the format: http(s)://subdomain.example.com/(path)')
    #return HttpResponse(redirect_link)
    return HttpResponse(simplejson.dumps(result), 'application/javascript')
