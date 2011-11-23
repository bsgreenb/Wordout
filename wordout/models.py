from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

IDENTIFIER_TYPE = (
        ('1', 'number'),
        ('2', 'custom'),
)
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

class Identifiers(models.Model):
    user = models.ForeignKey(User)
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
    referrer = models.ForeignKey(Full_Link)
    IP = models.ForeignKey(IP)
    Agent = models.ForeignKey(User_Agent)
    created = models.DateTimeField(auto_now_add = True)

