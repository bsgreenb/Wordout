from wordout import models
from django import forms
import re
from django.contrib.auth.models import User

'''
question: do I need a form to validate all inputs from my redirect_page?
'''


class NumericIdenForm(forms.Form):
    start = forms.IntegerField()
    end = forms.IntegerField()
    redirect_link = forms.URLField(verify_exists=True)
    def clean_start(self):
        #make sure the start is 1 bigger than the last numeric identifier
        if 'start' in self.cleaned_data:
            start = self.cleaned_data['start']
            try:
                last = int(Identifier.objects.filter(customer = request.user, identifier_type = 1).order_by('-created')[0])
            except Identifier.IndexError:
                last = 0
            if last < start
                return start
        raise forms.Validation('start < last')

    
    def clean_end(self):
        if 'start' in self.cleaned_data and 'end' in self.cleaned_data:
            start = self.cleaned_data['start']
            end = self.cleaned_data['end']

            if end > start:
                return end
        raise forms.Validation('end < start')

class CustomIdenForm(forms.Form):
    identifer = forms.CharField()
    redirect_link = forms.URLField(verify_exists=True)



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

