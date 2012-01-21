from wordout.models import *


def test_shit():
    customer = Customer.objects.get(pk=1)
    n = 1
    result = customer.display_sharers(order_by='action_count',action_type_id=n)
    print result
