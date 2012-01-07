from wordout.models import *
from django import forms
import re
from django.contrib.auth.models import User
from wordout.lib import force_url_format
#todo
#how i can validate the user agent.

class CreateSharerForm(forms.Form):
    start = forms.IntegerField()
    end = forms.IntegerField()
    redirect_link = forms.URLField()

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
        raise forms.ValidationError('Sharer id is already taken.')
    
    def clean_end(self):
        if 'start' in self.cleaned_data and 'end' in self.cleaned_data:
            start = self.cleaned_data['start']
            end = self.cleaned_data['end']
            
            #limit the number of identifiers. current is 1000
            total = Sharer.objects.filter(customer = self._user).count()
            num_created = end - start + 1
            max_users = Customer.objects.get(user = self._user).customergroup.max_users
            if (total + num_created) > max_users:
                raise forms.ValidationError('The amount of sharer is limited to %s' % max_users)

            if end >= start:
                return end
        raise forms.ValidationError('The end number should be bigger than the start number.')

class ChangeLinkForm(forms.Form):
    redirect_link = forms.URLField()

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


class RegistrationForm(forms.Form):
    username = forms.CharField(label=u'Username', max_length = 30)
    email = forms.EmailField(label=u'Email')
    password1 = forms.CharField(label=u'Password', widget=forms.PasswordInput())
    password2 = forms.CharField(label=u'Confirm Password', widget=forms.PasswordInput()) 
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
            raise forms.ValidationError('Username can only contain alphanumeric characters and the underscore.')
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError('Username is already taken')

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError('Email is already taken')


class ActionTypeForm(forms.Form):
    customer_action_type_identifier = forms.IntegerField()
    action_name = forms.CharField(max_length=20)
    action_description = forms.CharField(max_length=250, required=False)
    
    def __init__(self, user=None, *args, **kwargs):
        super(ActionTypeForm, self).__init__(*args, **kwargs)
        self._user = user

    def clean_action_id(self):
        if 'customer_action_type_identifier' in self.cleaned_data:
            customer_action_type_identifier = self.cleaned_data['customer_action_type_identifier']
            max_actions = self._user.customergroup.max_actions
            if customer_action_type_identifier >= max_actions:
                raise forms.ValidationError('The max number of  actions is %s' % max_actions)
            return customer_action_type_identifier

class MessageForm(forms.Form):
    message_title = forms.CharField(max_length=200, required=False)
    message_body = forms.CharField(required=False)

class ValidateReferrer(forms.Form):
    referrer = forms.URLField()

class ValidateIP(forms.Form):
    ip = forms.IPAddressField()

##### api call #####
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
    
