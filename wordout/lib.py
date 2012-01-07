import re, string, random
from django.utils import simplejson
from datetime import datetime
from django.http import HttpResponse

def dictfetchall(cursor):
    #returns all rows from a cursor as a dict
    desc = cursor.description
    return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
            ]

def get_ip(request):
    ip = request.META.get("HTTP_X_FORWARDED_FOR", None)
    if ip:
    # X_FORWARDED_FOR returns client1, proxy1, proxy2,...
        ip = ip.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR", None)
    
    return ip

def code_generator(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for i in range(size))

def force_url_format(url):
    url_format = re.compile(r'^(https?\://[a-zA-Z0-9\-\.]+\.[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3})((/\S*)?)$')
    return url_format.search(url)

def generate_json_for_detail(ls):
    #sharer and referrer details return the same data in json format
    results = {}
    try:
        if ls[0]:
            results['success'] = True
            results['response'] = ls
    except:
        results['success'] = False

    return simplejson.dumps(results)

def check_session_form(request):
    if request.session.get('form', ''):
        form = request.session['form']
        del request.session['form']
    else:
        form = ''
    return form

def get_api_metaset(status, message):
    #if the api call fail, we simply return the following dict in json format. if the call is valid, we add data to result['response']
    result = {}
    result['meta'] = {
            'status':status,
            'message':message,
            'timestamp':str(datetime.now())
            }
    return result
