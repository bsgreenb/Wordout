import re
from django import forms
from django.contrib.auth.models import User

from wordout.lib import valid_wordout_url
from wordout.models import *

# customize each error messages and all ValidationError

class RegistrationForm(forms.Form):
    username = forms.CharField(label=u'Username', max_length = 30, error_messages={'required':'', 'invalid':''})
    email = forms.EmailField(label=u'Email', error_messages={'required':'', 'invalid':''})
    password1 = forms.CharField(label=u'Password', widget=forms.PasswordInput(), error_messages={'required':'', 'invalid':''})
    password2 = forms.CharField(label=u'Confirm Password', widget=forms.PasswordInput(), error_messages={'required':'', 'invalid':''})

    def clean_password2(self):
        if 'password1' in self.cleaned_data:
            password1 = self.cleaned_data['password1']
            password2 = self.cleaned_data['password2']

            if password1 == password2:
                return password2
        raise forms.ValidationError('Passwords do not match')

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.search(r'^\w+$', username):
            raise forms.ValidationError('Usernames can only contain letters, numbers, and underscores.')
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError('An account with this username is already registered.')

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError('That email address is already in use for an existing account.')

class DisplaySharerForm(forms.Form):
    ORDER_BY_CHOICES = (
        ('customer_sharer_identifier', 'customer_sharer_identifier'),
        ('action_count', 'action_count'),
        ('redirect_link', 'redirect_link'),
        ('enabled', 'enabled'),
        ('click_total', 'click_total')
    )

    DIRECTION = (
        ('DESC','DESC'),
        ('ASC', 'ASC')
    )

    #These are the sorting options.  By default it's set to order by the customer_sharer_identifiers, descending, beginning at page 1.
    order_by = forms.ChoiceField(choices=ORDER_BY_CHOICES, required=False)
    direction = forms.ChoiceField(choices=DIRECTION, required=False)
    action_type_id = forms.IntegerField(required=False)
    page_number = forms.IntegerField(required=False)

    #For when we want info a particular Sharer
    customer_sharer_identifier = forms.IntegerField(required=False)

    #We need to do custom clean functions because initial will not work in this case.  initial is just for setting up the form default values prior to submit but won't get anything the first time.
    def clean_order_by(self):
        if 'order_by' in self.cleaned_data and self.cleaned_data['order_by'] == '':
            return 'customer_sharer_identifier'
        elif 'order_by' in self.cleaned_data:
            return self.cleaned_data['order_by']
        raise forms.ValidationError('order by is invalid')

    def clean_direction(self):
        if 'direction' in self.cleaned_data and self.cleaned_data['direction'] == '':
            return 'DESC'
        elif 'direction' in self.cleaned_data:
            return self.cleaned_data['direction']
        raise forms.ValidationError('direction is invalid')

    def clean_action_type_id(self):
        if 'action_type_id' in self.cleaned_data and self.cleaned_data['action_type_id'] == None:
            return None
        elif 'action_type_id' in self.cleaned_data:
            return self.cleaned_data['action_type_id']
        raise forms.ValidationError('action type id is invalid')

    def clean_page_number(self):
        if 'page_number' in self.cleaned_data and self.cleaned_data['page_number'] == None:
            return '1'
        elif 'page_number' in self.cleaned_data:
            return self.cleaned_data['page_number']
        raise forms.ValidationError('page number is invalid')

    def clean_customer_sharer_identifier(self):
        if 'customer_sharer_identifier' in self.cleaned_data and self.cleaned_data['customer_sharer_identifier'] == None:
            return None
        elif 'customer_sharer_identifier' in self.cleaned_data:
            return self.cleaned_data['customer_sharer_identifier']
        raise forms.ValidationError('customer sharer identifier is invalid')

class ChangeLinkForm(forms.Form):
    redirect_link = forms.URLField(error_messages={'required':'', 'invalid':''})

    def clean_redirect_link(self):
        if 'redirect_link' in self.cleaned_data:
            redirect_link = self.cleaned_data['redirect_link']
            if valid_wordout_url(redirect_link):
                #regular expression testing out the format
               return redirect_link
        raise forms.ValidationError('The URL needs to match the format: "http(s)://subdomain.example.com(path)" (parentheses mean optional)".')

class ActionTypeForm(forms.Form):
    action_name = forms.CharField(max_length=20, error_messages={'required':'', 'invalid':''})
    action_description = forms.CharField(max_length=250, required=False, error_messages={'invalid':''})
    
    def __init__(self, user=None, *args, **kwargs): #Because forms.Form.__init__ isn't a normal init that just stores variables, we have to super it to pass user.
        super(ActionTypeForm, self).__init__(*args, **kwargs)
        self._user = user

    def clean_action_name(self): # BAD NAME to call function. But I do want to check the max actions on this form and give form errors.
        if self._user.action_type_set.count() >= self._user.customer_group.max_actions: # current number of actions is equal or more than max actions
            raise forms.ValidationError('The max number of  actions is %s' % max_actions)
        return self.cleaned_data['action_name']

class SetProgramForm(forms.Form):
    redirect_link = forms.URLField(error_messages={'required':'', 'invalid':''})
    message_title = forms.CharField(max_length=200, required=False, error_messages={'invalid':''})
    message_body = forms.CharField(required=False, error_messages={'invalid':''})

    def clean_redirect_link(self):
        if 'redirect_link' in self.cleaned_data:
            redirect_link = self.cleaned_data['redirect_link']
            if valid_wordout_url(redirect_link):
            #regular expression testing out the format
                return redirect_link
        raise forms.ValidationError('The URL need match the format: "http(s)://subdomain.example.com/(path) (brackets means optional)".')

class ValidateReferrer(forms.Form):
    referrer = forms.URLField(error_messages={'required':'', 'invalid':''})

    def clean_referrer(self): # i need modify the referrer to match our format: "http(s)://subdomain.example.com/(path)"

        case = re.compile(r'^(https?\://)?([a-zA-Z0-9\-\.]+\.)?([a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?)$')
        match = case.search(self.cleaned_data['referrer'])
        if match:
            s = ''
            if match.group(1): # http://
                s += match.group(1)
            else:
                s += 'http://'

            if match.group(2): # www.
                s += match.group(2)
            else:
                s += 'www.'

            s += match.group(3)
            return s

        else:
            return referrer  # this is not necessary but in case we fucked up the previous cases.

class ValidateIP(forms.Form):
    ip = forms.IPAddressField(error_messages={'required':'', 'invalid':''})

##### api call #####

# I am not returning form error through api calls, instead, I use all customized errors.
class DoActionForm(forms.Form):
    click_id = forms.IntegerField(min_value=1)
    action_type_identifier = forms.IntegerField(min_value=1, max_value=99)
    extra_data = forms.CharField(max_length=500, required=False)

class AddSharerForm(forms.Form):
    customer_sharer_identifier = forms.CharField(max_length=50)

class ToggleSharerForm(forms.Form):
    customer_sharer_identifier = forms.CharField(max_length=50)
    enabled = forms.BooleanField(required=False)


    
