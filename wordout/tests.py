from django.test import TestCase
from wordout.models import *

# test
class SimpleTest(TestCase):
    def test_basic_addition(self):
        self.failUnlessEqual(1 + 1, 2)

# ----- first part -----
# the first part is to unit test all methods of the customer
# the fixture - test_datasource.json includes one customer -- ruixia,  10 sharers and 2 action types
# TODO I need also add clicks and referrers for display_referrer_by_sharer function
# i leave display_sharers at the end because it's the most complex one.

class Test_Display_Sharers(TestCase):
    pass

class Test_Display_Referrer_By_Sharer(TestCase):
    pass


class Test_Create_Sharer(TestCase):
    fixtures = ['test_data.json']

    # variables' validation is dealt in views.

    # requirement 1: end_total_count is equal to end
    # requirement 2: the code is not in EXCLUE_CODE_LIST = ('sharer', 'apidoc').  TODO how to test out this case?
    # requirement 3: redirect link is right for the inserted sharers.

    def setUp(self):
        self.customer = Customer.objects.get(pk=1)
        self.link = "http://www.facebook.com"
        self.count = self.customer.sharer_set.count()

    def test_total_number_and_link(self):
        start = self.count + 1
        end = self.count + 10
        self.customer.create_sharer(start, end, self.link)
        new_count = self.customer.sharer_set.count()

        self.assertEqual(new_count, end)

        inserted_sharers = Sharer.objects.filter(customer=self.customer).order_by('-customer_sharer_identifier')[:end-start+1]
        for sharer in inserted_sharers:
            inserted_link = sharer.redirect_link.host.host_name + sharer.redirect_link.path
            self.assertEqual(self.link, inserted_link)

class Test_Change_Redirect_Link(TestCase):
    fixtures = ['test_data.json']

    # variables' validation is dealt in views.

    # requirement 1: if sharer_ls is "ALL", all sharers' redirect link would be changed
    # requirement 2: if sharer_ls is a list, only sharers of the list would be changed

    def setUp(self):
        self.customer = Customer.objects.get(pk=1)
        self.link = 'http://www.twitter.com'
        self.sharer_ls_list = ['ALL', [10, 9, 8, 7]]

    def test_change_link(self):
        for case in self.sharer_ls_list: # loop through two cases.
            self.customer.change_redirect_link(self.link, case)
            sharers = Sharer.objects.filter(customer=self.customer)
            if case != 'ALL':
                sharers = sharers.filter(customer_sharer_identifier__in = case)

            for sharer in sharers:
                changed_link = sharer.redirect_link.host.host_name + sharer.redirect_link.path
                self.assertEqual(self.link, changed_link)


class Test_Disabled_Or_Enable_Sharer(TestCase):
    fixtures = ['test_data.json']

    # requirement 1. the code should work in all 4 cases: (disable, ls), (enable, ls), (disable, all), (enable, all)

    def setUp(self):
        self.customer = Customer.objects.get(pk=1)
        self.enable_or_disable = [True, False]
        self.sharer_ls_list = ['ALL', [10, 9, 8, 7]]

    def test_disable_enable(self):
        for case in self.sharer_ls_list:
            for boolean in self.enable_or_disable:
                self.customer.disable_or_enable_sharer(case, boolean)
                sharers = Sharer.objects.filter(customer=self.customer)
                if case != 'ALL':
                    sharers = sharers.filter(customer_sharer_identifier__in = case)

                for sharer in sharers:
                    self.assertIs(sharer.enabled, boolean)

class Test_Update_Title_And_Body(TestCase):
    fixtures = ['test_data.json']

    # requirement 1. title and body should be saved

    def setUp(self):
        self.customer= Customer.objects.get(pk=1)
        self.body = 'Hello. This is the body'
        self.title = 'Hello. This is the title'

    def test_title_and_body_save(self):
        self.customer.update_title_and_body(self.title, self.body)
        self.assertEqual(self.body, self.customer.message_body)
        self.assertEqual(self.title, self.customer.message_title)

class Test_Create_ActionType(TestCase):
    fixtures = ['test_data.json']

    # requirement 1.













