from wordout.models import *
from urlparse import urlparse
from django.db import connection

def test_shit():
    customer = Customer.objects.get(pk=1)
    sharer = Sharer.objects.get(customer=customer, customer_sharer_identifier='abc')
    clicks = Click.objects.filter(sharer=sharer).values('referrer__host__host_name','referrer__path').annotate(click_total=Count('id')).order_by('click_total')
    return clicks

def test_shit2():
    customer = Customer.objects.get(pk=1)
    for sharer in customer.sharer_set.all():
        data = customer.get_referrers_for_sharer(sharer.customer_sharer_identifier)
        print data
        if data != []:
            for referrer_and_click in data:
                if referrer_and_click.get('referrer', ''):
                    url = urlparse(referrer_and_click['referrer'])
                    host_name, path = url.scheme + '://' + url.netloc, url.path
                    print str(host_name) + '|||' + str(path) + '|||' + sharer.customer_sharer_identifier + '|||' + str(referrer_and_click['clicks']) + '|||||'+ str(Click.objects.filter(sharer__customer=customer, referrer__host__host_name=host_name, referrer__path=path, sharer__customer_sharer_identifier = sharer.customer_sharer_identifier).count())
                else:
                    print str('') + '|||' + str('') + '|||' + sharer.customer_sharer_identifier + '|||' + str(referrer_and_click['clicks']) + '|||||'+ str(Click.objects.filter(sharer__customer=customer, referrer = None, sharer__customer_sharer_identifier = sharer.customer_sharer_identifier).count())
