from wordout.models import *
from django.db import connection

def test_shit():
    customer = Customer.objects.get(pk=1)
    sharer = Sharer.objects.get(customer=customer, customer_sharer_identifier='abc')
    clicks = Click.objects.filter(sharer=sharer).values('referrer__host__host_name','referrer__path').annotate(click_total=Count('id')).order_by('click_total')
    return clicks
