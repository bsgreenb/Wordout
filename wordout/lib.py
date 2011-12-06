import re, string, random
from django.utils import simplejson

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
        if ls[0].id:
            results = [{'success':True}]
            for i in ls:
                holder ={}
                holder['host_name'] = i.host_name
                holder['path_loc'] = i.path_loc
                holder['clicks'] = i.clicks
                results.append(holder)
    except:
        results = [{'success':False}]

    results = simplejson.dumps(results)

    return results
