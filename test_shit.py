from wordout.models import *
from django.db import connection

def test_shit():
    customer = Customer.objects.get(pk=1)
    result = customer.display_sharers(desc=True)
    print len(connection.queries)
    return result
