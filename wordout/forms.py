from wordout.models import *
from django import forms
import re
from django.contrib.auth.models import User
from wordout.lib import force_url_format

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
            return 'desc'
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

class CreateSharerForm(forms.Form):
    start = forms.IntegerField(error_messages={'required':'', 'invalid':''})
    end = forms.IntegerField(error_messages={'required':'', 'invalid':''})
    redirect_link = forms.URLField(error_messages={'required':'', 'invalid':''})

    def __init__(self, user=None, *args, **kwargs):
        super(CreateSharerForm, self).__init__(*args, **kwargs)
        self._user = user
    
    def clean_redirect_link(self):
        if 'redirect_link' in self.cleaned_data:
            redirect_link = self.cleaned_data['redirect_link']
            if force_url_format(redirect_link):
                #regular expression testing out the format
               return redirect_link
        raise forms.ValidationError('The URL need match the format: "http(s)://subdomain.example.com(path) (brackets means optional)".')

    def clean_start(self):
        #make sure the start is 1 bigger than the last numeric identifier
        if 'start' in self.cleaned_data:
            start = self.cleaned_data['start']
            try:
                last = Sharer.objects.filter(customer = self._user).order_by('-created')[0]
                last = int(last.customer_sharer_identifier)
            except IndexError:
                last = 0
            if last < start:
                return start
        raise forms.ValidationError('Sharers have been added since this page loaded.  Please try again.')
    
    def clean_end(self):
        if 'start' in self.cleaned_data and 'end' in self.cleaned_data:
            start = self.cleaned_data['start']
            end = self.cleaned_data['end']
            
            #limit the number of identifiers. current is 1000
            total = Sharer.objects.filter(customer = self._user).count()
            num_created = end - start + 1
            max_users = Customer.objects.get(user = self._user).customer_group.max_users
            if (total + num_created) > max_users:
                raise forms.ValidationError('The amount of sharer is limited to %s' % max_users)

            if end >= start:
                return end
        raise forms.ValidationError('The end number should be bigger than the start number.')

class ChangeLinkForm(forms.Form):
    redirect_link = forms.URLField(error_messages={'required':'', 'invalid':''})

    def __init__(self, user=None, *args, **kwargs):
        super(ChangeLinkForm, self).__init__(*args, **kwargs)
        self._user = user

    def clean_redirect_link(self):
        if 'redirect_link' in self.cleaned_data:
            redirect_link = self.cleaned_data['redirect_link']
            if force_url_format(redirect_link):
                #regular expression testing out the format
               return redirect_link
        raise forms.ValidationError('The URL need match the format: "http(s)://subdomain.example.com(path) (brackets means optional)".')

class ActionTypeForm(forms.Form):
    customer_action_type_identifier = forms.IntegerField(error_messages={'required':'', 'invalid':''})
    action_name = forms.CharField(max_length=20, error_messages={'required':'', 'invalid':''})
    action_description = forms.CharField(max_length=250, required=False, error_messages={'invalid':''})
    
    def __init__(self, user=None, *args, **kwargs):
        super(ActionTypeForm, self).__init__(*args, **kwargs)
        self._user = user

    def clean_action_id(self):
        if 'customer_action_type_identifier' in self.cleaned_data:
            customer_action_type_identifier = self.cleaned_data['customer_action_type_identifier']
            max_actions = self._user.customer_group.max_actions
            if customer_action_type_identifier >= max_actions:
                raise forms.ValidationError('The max number of  actions is %s' % max_actions)
            return customer_action_type_identifier

class MessageForm(forms.Form):
    message_title = forms.CharField(max_length=200, required=False, error_messages={'invalid':''})
    message_body = forms.CharField(required=False, error_messages={'invalid':''})

class ValidateReferrer(forms.Form):
    referrer = forms.URLField(error_messages={'required':'', 'invalid':''})

class ValidateIP(forms.Form):
    ip = forms.IPAddressField(error_messages={'required':'', 'invalid':''})

##### api call #####

# I am not returning form error through api calls, instead, I use all customized errors.
class DoActionForm(forms.Form):
    click_id = forms.IntegerField(min_value=1)
    action_type_identifier = forms.IntegerField(min_value=1, max_value=99)
    extra_data = forms.CharField(max_length=250, required=False)

class AddSharerForm(forms.Form):
    redirect_link = forms.URLField()
    
    def clean_redirect_link(self):
        if 'redirect_link' in self.cleaned_data:
            redirect_link = self.cleaned_data['redirect_link']
            if force_url_format(redirect_link):
                #regular expression testing out the format
               return redirect_link
        raise forms.ValidationError('The URL need match the format: "http(s)://subdomain.example.com(path) (brackets means optional)".')

class ToggleSharerForm(forms.Form):
    customer_sharer_identifier = forms.IntegerField(min_value=1)
    enabled = forms.BooleanField(required=False)

class GetSharerByIdForm(forms.Form):
    #check if the sharer id is an integer
    customer_sharer_identifier = forms.IntegerField(min_value=1)

    
