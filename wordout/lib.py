import re, string, random
from django.utils import simplejson


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

def force_subdomain(netloc):
    m = re.compile(r'^[a-zA-Z0-9\-\.]+\.[a-zA-Z0-9\-\.]+\.(com|org|net|mil|edu|me|ly|biz|COM|ORG|NET|MIL|EDU|ME|LY|BIZ)$')
    search = m.search(netloc)
    if not search:
        netloc = 'www.' + netloc
    return netloc

def generate_json_for_detail(ls):
    '''
    identifier and referrer details return the same data in json format
    '''
    try:
        if ls[0]:
            results = [{'success':True}]
            results.extend(ls)
    except:
        results = [{'success':False}]

    results = simplejson.dumps(results)

    return results
