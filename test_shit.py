from wordout.models import *
from django.db import connection

#TODO: test out with all the parameters

def test_shit():
    customer = Customer.objects.get(pk=1)
    n = 4
    result = customer.display_sharers(order_by='action_count', action_type_id=n)
    print connection.queries
    return result
