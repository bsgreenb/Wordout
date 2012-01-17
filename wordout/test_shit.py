from django.db import connection
from wordout.models import *

customer = Customer.objects.get(pk=1)
if __name__ == '__main__':
    print customer.display_sharers()