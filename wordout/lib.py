import re, string, random
from datetime import datetime

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

def valid_wordout_url(url):
    """
    matches url on the complete wordout HTTP rules (basically, you must specify http:// or https://) as well as the subdomain e.g. 'www'.  Can be used for both validation and for capturing specific parts like the host or the path.
    """
    url_format = re.compile(r'^(https?\://[a-zA-Z0-9\-\.]+\.[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3})((/\S*)?)$')
    return url_format.search(url)

def get_previous_form(request): # Because of modal dialogues, sometimes we want to pass the form from modals to the main page that called them for displaying their error msgs
    if request.session.get('form', ''):
        form = request.session['form']
        del request.session['form']
    else:
        form = ''
    return form

def get_api_metaset(status, message):
    #if the api call fail, we simply return the following dict in json format. if the call is valid, we add data to result['response']
    result = {
        'meta':{
            'status':status,
            'message':message,
            'timestamp':str(datetime.now())
        }
    }
    return result
