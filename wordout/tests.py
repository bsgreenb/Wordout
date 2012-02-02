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

    # requirement 1: accept valid identifiers. reject invalid identifiers
    # requirement 2: the code is not in EXCLUE_CODE_LIST = ('sharer', 'apidoc').  TODO how to test out this case?
    # requirement 3: redirect link, identifier are right for the inserted sharers.
    # requirement 4: code length is matching the length of the code.

    def setUp(self):
        self.customer = Customer.objects.get(pk=1)
        self.count = self.customer.sharer_set.count()
        self.length_of_code = 6
        self.valid_identifiers = ['aaa', 'ccc', '12354', 'fdasf1', 'hgfhggfh521321', '!!!!', '#$#@%$3']

    def test_create_sharer(self):
        for identifier in self.valid_identifiers:
            current_count = self.customer.sharer_set.count()
            sharer = self.customer.create_sharer(customer_sharer_identifier = identifier)

            self.assertEqual(current_count + 1, self.customer.sharer_set.count())
            self.assertEqual(sharer.customer_sharer_identifier, identifier)
            self.assertEqual(sharer.redirect_link, self.customer.redirect_link)
            self.assertEqual(len(sharer.code), self.length_of_code)


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
        self.customer.update_program(self.customer.redirect_link, self.title, self.body)
        self.assertEqual(self.body, self.customer.message_body)
        self.assertEqual(self.title, self.customer.message_title)

class Test_Create_ActionType(TestCase):
    fixtures = ['test_data.json']

    # requirement 1. action_name is inserted
    # requirement 2. description is inserted
    # requirement 3. the number of action type is added by one

    def setUp(self):
        self.customer = Customer.objects.get(pk=1)
        self.action_name = 'test'
        self.description = 'test out'
        self.count = Action_Type.objects.filter(customer=self.customer).count()
        self.next_action_type = Action_Type.objects.filter(customer=self.customer).order_by('-created')[0].customer_action_type_identifier + 1

    def test_create_action_type(self):
        self.customer.create_actiontype(self.next_action_type, self.action_name, self.description)
        current_action_types = Action_Type.objects.filter(customer=self.customer)

        self.assertEqual(self.count+1, current_action_types.count())

        last_action = current_action_types.order_by('-created')[0]
        self.assertEqual(self.action_name, last_action.action_name)
        self.assertEqual(self.description, last_action.description)

class Test_Edit_ActionType(TestCase):
    fixtures = ['test_data.json']

    # requirement 1. action_name is saved
    # requirement 2. description is saved.

    def setUp(self):
        self.customer = Customer.objects.get(pk=1)
        self.new_action_name = 'fk'
        self.new_description = 'fkfk'
        self.edited_actiontype = Action_Type.objects.filter(customer=self.customer).order_by('-created')[0]

    def test_edit_action_type(self):
        self.edited_actiontype.action_name = self.new_action_name
        self.edited_actiontype.description = self.new_description
        self.edited_actiontype.save()

        after_edited_actiontype = Action_Type.objects.filter(customer=self.customer).order_by('-created')[0]
        self.assertEqual(after_edited_actiontype.action_name, self.new_action_name)
        self.assertEqual(after_edited_actiontype.description, self.new_description)


class Test_Disable_Or_Enable_Action(TestCase):
    fixtures = ['test_data.json']

    # requirement 1. [[1], [1,2], [1,2,3]] / disable and enable. the code should work for all six cases
    pass














