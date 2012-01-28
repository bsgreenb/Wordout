from wordout.models import *
from django.db import connection

def test_shit():
    customer = Customer.objects.get(pk=1)
    result = customer.display_sharers(order_by='action_count',action_type_id=1)
    print len(connection.queries)
    return result
