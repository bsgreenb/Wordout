from urlparse import urlparse
from django.test import TestCase
from django.db import IntegrityError # Exception raised when the relational integrity of the database is affected, e.g. a foreign key check fails, duplicate key, etc.
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
    fixtures = ['test_data.json']

    # requirement 1. invalidate customer sharer identifier should return empty ls
    # requirement 2. when the referrer is not None. the referrer has to be one of the full link and the total clicks should be right.
    # requirement 3. when the referrer is None. the total clicks have to match.
    def setUp(self):
        self.customer = Customer.objects.get(pk=1)
        self.clicks = Click.objects.filter(sharer__customer=self.customer)

    def test_invalid_sharer_identifier(self):

        # invalid sharer identifier will return None
        invalid_sharer_ident_ls = ['aaa', 'bbb', 'ccc', 'ddd', 'eee123', 'fff', 'ggg0983', '9751']
        sharer_ident_ls = [sharer['customer_sharer_identifier'] for sharer in Sharer.objects.filter(customer=self.customer).values('customer_sharer_identifier')]
        for invalid_sharer_ident in invalid_sharer_ident_ls:
            if invalid_sharer_ident not in sharer_ident_ls:
                self.assertEqual(self.customer.get_referrers_for_sharer(invalid_sharer_ident), list())

    # loop through the user's sharers. send the referrer and customer sharer id back to the click model. check whether the click total matches.

    def test_get_referrers_for_sharer(self):
        for sharer in self.customer.sharer_set.all():
            data = self.customer.get_referrers_for_sharer(sharer.customer_sharer_identifier)
            if data != []:
                for referrer_and_click in data:
                    if referrer_and_click.get('referrer', ''):
                        url = urlparse(referrer_and_click['referrer'])
                        host_name, path = url.scheme + '://' + url.netloc, url.path
                        # referrer is not empty and has host_name and path
                        self.assertEqual(referrer_and_click['clicks'], Click.objects.filter(sharer__customer=self.customer, referrer__host__host_name=host_name, referrer__path=path, sharer__customer_sharer_identifier = sharer.customer_sharer_identifier).count())
                    else:
                        # referrer is empty
                        self.assertEqual(referrer_and_click['clicks'], Click.objects.filter(sharer__customer=self.customer, referrer=None, sharer__customer_sharer_identifier = sharer.customer_sharer_identifier).count())


class Test_Create_Sharer(TestCase):
    fixtures = ['test_data.json']

    # variables' validation is dealt in views.

    # requirement 1: accept valid identifiers.
    # requirement 2: the code is not in EXCLUE_CODE_LIST = ('sharer', 'apidoc').  TODO how to test out this case?
    # requirement 3: redirect link, identifier are right for the inserted sharers.
    # requirement 4: code length is matching the length of the code.
    # requirement 5: customer id and customer_sharer identifier has to be unique

    def setUp(self):
        self.customer = Customer.objects.get(pk=1)
        self.count = self.customer.sharer_set.count()
        self.length_of_code = 6
        self.valid_identifiers = ['aaa', 'bbb', '12354', 'fdasf1', 'hgfhggfh521321', '!!!!', '#$#@%$3']

    def test_create_sharer(self):
        for identifier in self.valid_identifiers:
            current_count = self.customer.sharer_set.count()
            sharer = self.customer.create_sharer(customer_sharer_identifier = identifier)

            self.assertEqual(current_count + 1, self.customer.sharer_set.count())
            self.assertEqual(sharer.customer_sharer_identifier, identifier)
            self.assertEqual(sharer.redirect_link, self.customer.redirect_link)
            self.assertEqual(len(sharer.code), self.length_of_code)


    def test_unique_customer_id_and_identifier(self):
        duplicate_identifier = self.customer.sharer_set.all()[0].customer_sharer_identifier

        with self.assertRaises(IntegrityError):
            self.customer.create_sharer(customer_sharer_identifier = duplicate_identifier)





class Test_Change_Redirect_Link(TestCase):
    fixtures = ['test_data.json']

    # variables' validation is dealt in views.

    # requirement 1: if sharer_ls is "ALL", all sharers' redirect link would be changed
    # requirement 2: if sharer_ls is a list, only sharers of the list would be changed

    def setUp(self):
        self.customer = Customer.objects.get(pk=1)
        self.link = 'http://www.twitter.com'

        self.part_sharer_ls = [sharer.customer_sharer_identifier for sharer in self.customer.sharer_set.all()[:4]] # build the partial sharer identifier ls
        self.sharer_ls_list = ['ALL', self.part_sharer_ls]

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
        self.part_sharer_ls = [sharer.customer_sharer_identifier for sharer in self.customer.sharer_set.all()[:4]] # build the partial sharer identifier ls
        self.sharer_ls_list = ['ALL', self.part_sharer_ls]

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

    def test_create_action_type(self):
        self.customer.create_actiontype(self.action_name, self.description)
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

    def setUp(self):
        self.customer = Customer.objects.get(pk=1)
        self.enable_or_disable = [True, False]
        self.part_action_ls = [action_type.customer_action_type_identifier for action_type in self.customer.action_type_set.all()[:4]]


    def test_disable_or_enable_action(self):
        for boolean in self.enable_or_disable:
            self.customer.disable_or_enable_action(self.part_action_ls, boolean)

            action_types = self.customer.action_type_set.filter(customer_action_type_identifier__in = self.part_action_ls)

            for action_type in action_types:
                self.assertIs(action_type.enabled, boolean)


class Test_Display_Referrer(TestCase):
    # this function is not used yet.
    pass


class Test_Display_Path(TestCase):
    # this function is not used yet.
    pass


















