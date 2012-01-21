from wordout.models import *


def test_shit(n):
    customer = Customer.objects.get(pk=1)
    result = customer.display_sharers(action_type_id=n)
    print result
