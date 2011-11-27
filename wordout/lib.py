import re, string, random

def code_generator(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for i in range(size))

def force_subdomain(netloc):
    m = re.compile(r'^[a-zA-Z0-9\-\.]+\.[a-zA-Z0-9\-\.]+\.(com|org|net|mil|edu|me|ly|biz|COM|ORG|NET|MIL|EDU|ME|LY|BIZ)$')
    search = m.search(netloc)
    if not search:
        netloc = 'www.' + netloc
    return netloc


