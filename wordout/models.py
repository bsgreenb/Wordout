from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from urlparse import urlparse
from lib import *



IDENTIFIER_TYPE = (
        ('1', 'number'),
        ('2', 'custom'),
)

#extend the user object. This is not the best way because I have to query the database once everytime. change it in version two

class HOST(models.Model):
    host_name = models.URLField()
    created = models.DateTimeField(auto_now_add = True)

    def __unicode__(self):
        return self.host_name

class Path(models.Model):
    path_loc = models.CharField(max_length = 200)
    created= models.DateTimeField(auto_now_add = True)

    def __unicode__(self):
        return self.path_loc

class IP(models.Model):
    address = models.IPAddressField()
    created = models.DateTimeField(auto_now_add = True)

    def __unicode__(self):
        return self.address

class User_Agent(models.Model):
    agent = models.CharField(max_length = 200)
    created = models.DateTimeField(auto_now_add = True)
    
    def __unicode__(self):
        return self.agent

class Full_Link(models.Model):
    host = models.ForeignKey(HOST)
    path = models.ForeignKey(Path)
    created = models.DateTimeField(auto_now_add = True)
    
    def __unicode__(self):
        return '%s%s' % (self.host, self.path)


def get_or_create_link(url):
    result = urlparse(url)
    
    path = result.path
    path, created = Path.objects.get_or_create(path_loc=path)

    netloc = result.scheme + '://' + force_subdomain(result.netloc) #prefix www.
    netloc, created = HOST.objects.get_or_create(host_name = netloc)

    link, created = Full_Link.objects.get_or_create(host = netloc, path = path)
    return (link, created)


class Customer(models.Model):
    user = models.OneToOneField(User)
    def __unicode__(self):
        return str(self.user)
    
    '''
    the customer can create two identifiers. 1. numberic. 2. custom.
    those are given on two forms with two save methods.
    '''

    def numeric_ident_save(self, start, end, redirect_link):
        redirect_link, created = get_or_create_link(redirect_link)

        for i in range(start, end+1):
            loop = True
            while loop == True:
                code = code_generator()
                try:
                    Identifiers.objects.get(code = code)
                except Identifiers.DoesNotExist:
                    loop = False
                    Identifiers.objects.create(customer = self, identifier = i, identifier_type = 1, code = code, redirect_link = redirect_link)

    def custom_ident_save(self, identifier, redirect_link):
       
        redirect_link, created = get_or_create_link(redirect_link)
        loop = True
        while loop == True:
            code = code_generator()
            try:
                Identifiers.objects.get(code=code)
            except Identifiers.DoesNotExist:
                loop = False
                Identifiers.objects.create(customer = self, identifier = identifier, identifier_type = 2, code = code, redirect_link = redirect_link)


class Identifiers(models.Model):
    customer = models.ForeignKey(Customer)
    identifier = models.CharField(max_length = 50)
    identifier_type = models.CharField(max_length = 1, choices = IDENTIFIER_TYPE)
    code = models.CharField(max_length = 8, unique = True, db_index = True)
    redirect_link = models.ForeignKey(Full_Link, related_name='identifier_redirect_link')
    enabled = models.BooleanField(default = True)
    modified = models.DateTimeField(auto_now = True)
    created = models.DateTimeField(auto_now_add = True)

    def __unicode__(self):
        return self.code

class Request(models.Model):
    referral_code = models.ForeignKey(Identifiers)
    redirect_link = models.ForeignKey(Full_Link, related_name='request_redirect_link')
    referrer = models.ForeignKey(Full_Link, blank=True, null=True)
    IP = models.ForeignKey(IP, blank=True, null=True)
    Agent = models.ForeignKey(User_Agent, blank=True, null=True)
    created = models.DateTimeField(auto_now_add = True)
    

