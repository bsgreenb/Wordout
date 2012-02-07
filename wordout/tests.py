from urlparse import urlparse

from django.test import TestCase
from django.db import IntegrityError # Exception raised when the relational integrity of the database is affected, e.g. a foreign key check fails, duplicate key, etc.
from django.contrib.auth.models import User

from wordout.models import *
from wordout.forms import *





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
    pass  # figure out the flow first.

    # requirement 1. test when customer_sharer_identifier is given. (click_total, action_type_set)
    # requirement 2. test the order by is right at not oder by 'action_count' case

    '''
    def test_sharer_data(self, sharer, sharer_dict):
        # sharer data matches sharer_dict
        self.assertEqual(sharer.customer_sharer_identifier, sharer_dict['sharer_identifier'])
        self.assertEqual(sharer.code, sharer_dict['code'])
        self.assertEqual(sharer.redirect_link, sharer_dict['redirect_link'])
        self.assertEqual(Click.objects.filter(sharer=sharer).count(), sharer_dict['click_total']
        self.assertEqual(sharer.enabled, sharer_dict['enabled'])

        sharer_action_counts = Action.objects.filter(click__sharer = sharer).values('click__sharer_id','action_type_id', 'action_type__action_name').annotate(action_count=Count('id'))

        for action_count in sharer_action_counts:
            for action_count_in_set in sharer_dict['action_type_set']:
                if action_count['action_type_id']  == action_count_in_set['action_type_id']:
                    self.assertEqual(action_count['action_count'], action_count_in_set['action_count'])

    # Now I am able to check out the sharer and sharer_dict. I can start to write all the cases.
    '''

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



#############  unittest for the forms ##############
# I think we only need test out the customized validation, but not the default validation for the django fields. Like RegistrationForm, I only need test out clean_password2, clean_username, clean_email

class Test_RegistrationForm(TestCase):
    fixtures = ['test_data.json']

    # setUp the
    def setUp(self):
        self.data = {
            'username':'testcase',
            'email':'testcase@gmail.com',
            'password1':'mopyard1',
            'password2':'mopyard1'
        }

    def test_valid_case(self):
        self.assertTrue(RegistrationForm(data).is_valid())

    def test_invalid_cases(self):
        user = User.objects.get(pk=1)
        existing_username = user.username
        existing_email = user.email

        cases = {
            # cover clean_password2, clean_username and clean_email casess
            'password2':'mopyard111',
            'username':existing_username,
            'email':existing_email
        }

        for case in cases:
            if case == 'password2':
                self.data['password2'] = case['password2']
            elif case == 'username':
                self.data['username'] = case['username']
            elif case == 'email':
                self.data['email'] = case['email']

        f = RegistrationForm(data)
        self.assertFalse(f.is_valid())
        self.assertIsNotNone(f.errors[case])

class Test_ChangeLinkForm(TestCase):
    # have cases in a dictionary. key is the actual url. value is True of False as indicator for valid and invalid.

    def test_clean_redirect_link(self):
        cases = [
            {'link': 'http://www.wordout.me', 'valid': True},
            {'link': 'http://www.wordout.me/abc', 'valid':True},
            {'link': 'https://www.twitter.com/api', 'valid': True},
            {'link': 'www.wordout.me', 'valid': False},
            {'link': 'http://wordout.me', 'valid': False},
            {'link': 'https://twitter.com', 'valid': False},
            {'link': 'http://www.me', 'valid': False}
        ]

        for case in cases:
            f = ChangeLinkForm({'redirect_link':case['link']})
            if case['valid']:
                self.assertTrue(f.is_valid())
            else:
                self.assertFalse(f.is_valid())

class Test_ValidateReferrer(TestCase):
    # the form should always return a valid referrer that
    def test_clean_referrer(self):

        cases = [
                {'link': 'http://www.wordout.me', 'test': None},
                {'link': 'http://www.wordout.me/abc', 'test':None},
                {'link': 'https://www.twitter.com/api', 'test': None},
                {'link': 'www.wordout.me', 'test': 'scheme'},
                {'link': 'http://wordout.me', 'test': 'subdomain'},
                {'link': 'https://twitter.com', 'test': 'subdomain'},
                {'link': 'http://www.me/aapi', 'test': 'subdomain'}
        ]

        for case in cases:
            f = ValidateReferer({'referrer':case['link']})
            self.assertTrue(f.is_valid())

            if not case['test']:
                self.assertEqual(case['link'], f.cleaned_data['referrer'])
            elif case['test'] == 'scheme':
                self.assertEqual('http://' + case['link'], f.cleaned_data['referrer'])
            elif case['test'] == 'subdomain':
                parse = urlparse(case['link'])
                link = parse.scheme + '://' + 'www.' + parse.netloc + parse.path
                self.assertEqual(link, f.cleaned_data['referrer'])



from django.test.client import RequestFactory
####### start to write unittest for the views ########
class Test_Logout_Page(TestCase):
    fixtures = ['test_data.json']

    def test_logout_page(self):
        # requirement 1. a logged in user can be logged out.
        user = User.objects.create_user('fakename', 'fake@gmail.com', 'wangshi')

        login = self.client.login(username = user.username, password='wangshi') # can't use user.password because it's hashed

        self.assertTrue(login) # logged in user.
        response = self.client.get('/logout/', follow=True)
        #todo how I can test out the user is anonymous now.
        self.assertTemplateUsed(response, 'landing_page.html')


class Test_Register_Page(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.data = {'username':'test', 'password1':'mopyard1', 'password2':'mopyard2', 'email':'test@gmail.com'} # it's invalid data. the password is different

    def test_get(self):
        response = self.client.get('/register/')
        self.assertTemplateUsed(response, 'registration/register.html')

    def test_post_invalid_data(self):
        #todo Do I only need test one invalid case since i already tested out most invalid cases in the form and knew the form will be invalid.

        response = self.client.post('/register/', self.data)
        self.assertTemplateUsed(response, 'registration/register.html') # invalid data.

    def test_post_valid_data(self):

        self.data['password2'] = 'mopyard1'  # now, the data is valid
        response = self.client.post('/register/', self.data, follow=True)
        last_user = User.objects.all().order_by('-date_joined')[0]
        last_customer = Customer.objects.get(user=last_user)
        self.assertEqual(last_user.username, self.data['username'])
        self.assertEqual(last_customer.customer_group.id, 1) # free group id
        self.assertRedirects(response, '/pluginpage/') # first time user is redirected to the sharer page config.





















