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
        try: #does the api_key match a customer
            customer = Customer.objects.get(api_key=api_key)
        except Customer.DoesNotExist:
            message = 'invalid api key.'
            result = get_api_metaset(status, message) #return httpresponse of a json with fail message
            return HttpResponse(simplejson.dumps(result), 'application/javascript')
        
        try: #is the click_id valid
            click = Click.objects.get(id=data['click_id'])
        except Click.DoesNotExist:
            message = 'invalid wordout click id.'
            result = get_api_metaset(status, message) #return httpresponse of a json with fail message
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
    api_call_fail(status, message)



