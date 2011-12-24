from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from urlparse import urlparse
from lib import dictfetchall, force_subdomain
from django.db.models import Count, Sum
from django.db import connection, transaction

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

class Customergroups(models.Model): # identify paid/unpaid users
    max_users = models.IntegerField(max_length = 10)
    
    def __unicode__(self):
        return str(self.id)

def get_default_customergroup():
    return Customergroups.objects.get(id=1) #set default customergroup for new customer

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
    client_key = models.CharField(max_length = 9, unique=True)
    api_key = models.CharField(max_length = 9, unique=True)
    message_title = models.CharField(max_length = 200, null=True, blank=True)
    message_body = models.TextField(null=True, blank=True)
    customergroup = models.ForeignKey(Customergroups, default=get_default_customergroup())

    def __unicode__(self):
        return str(self.user)

    def create_sharers(self, start, end, redirect_link):
        redirect_link, created = get_or_create_link(redirect_link)

        for i in range(start, end+1):
            loop = True
            while loop == True:
                code = code_generator()
                try:
                    Sharers.objects.get(code = code)
                except Sharers.DoesNotExist:
                    loop = False
                    Sharers.objects.create(customer = self, customer_sharer_id = i, code = code, redirect_link = redirect_link)

   
    def change_redirect_link(self, new_redirect_link):
        new_redirect_link, created = get_or_create_link(new_redirect_link)
        Sharers.objects.filter(customer=self).update(redirect_link = new_redirect_link)

    
    def display_sharers(self, least_click=None, start=None, end=None):
        
        #######I NEED EITHER BEN OR ERIN'S HELP ON THIS 
        ls = Sharers.objects.select_related().filter(customer = self)
        if start and end:
            ls = ls.filter(request__created__range=(start, end))
        ls = ls.annotate(num = Count('Clicks'))
        if least_click:
            ls = ls.filter(num__gte=least_click)

        ls = ls.order_by('-created')
        sum_clicks = ls.aggregate(sum_clicks=Sum('num'))['sum_clicks']
        return (ls, sum_clicks)
        
    def display_referrer_by_sharer(self, customer_sharer_id):
        cursor = connection.cursor()
        cursor.execute('''
        SELECT wordout_clicks.id, wordout_clicks.referrer_id, count(wordout_clicks.id) as clicks, wordout_host.host_name, wordout_path.path_loc
        FROM wordout_clicks
        LEFT JOIN wordout_full_link
            ON wordout_full_link.id = wordout_request.referrer_id
        LEFT JOIN wordout_host
            ON wordout_full_link.host_id = wordout_host.id
        LEFT JOIN wordout_path
            ON wordout_full_link.path_id = wordout_path.id
        LEFT JOIN wordout_sharers
            ON wordout_sharers.id = wordout_clicks.sharer_id
        WHERE
            wordout_sharers.customer_id = %s AND wordout_sharers.customer_sharer_id = %s
        GROUP BY 
            wordout_clicks.referrer_id
        ORDER BY
            clicks DESC
        ''', (self.id, customer_sharer_id))
        return dictfetchall(cursor)

    def display_referrer(self):
        cursor = connection.cursor()
        cursor.execute('''
        SELECT wordout_host.id, wordout_host.host_name, COUNT(wordout_clicks.id) as clicks
        FROM wordout_host
        LEFT JOIN wordout_full_link
            ON wordout_full_link.host_id = wordout_host.id
        LEFT JOIN wordout_clicks
            ON wordout_full_link.id = wordout_clicks.referrer_id
        LEFT JOIN wordout_sharers
            ON wordout_clicks.sharer_id = wordout_sharers.id
        WHERE
            wordout_sharers.customer_id = %s
        GROUP BY
            wordout_host.id
        ORDER BY
            clicks DESC
        ''', [self.id])
        return dictfetchall(cursor)


    def display_path(self, host_id):
        cursor = connection.cursor()
        cursor.execute('''
        SELECT wordout_path.id, wordout_path.path_loc, wordout_host.host_name, wordout_host.id, COUNT(wordout_clicks.id) as clicks
        FROM wordout_path
        LEFT JOIN wordout_full_link
            ON wordout_full_link.path_id = wordout_path.id
        LEFT JOIN wordout_host
            ON wordout_full_link.host_id = wordout_host.id
        LEFT JOIN wordout_clicks
            ON wordout_full_link.id = wordout_clicks.referrer_id
        LEFT JOIN wordout_sharers
            ON wordout_clicks.sharer_id = wordout_sharers.id
        WHERE wordout_sharers.customer_id = %s AND wordout_host.id = %s
        GROUP BY wordout_path.id
        ORDER BY clicks DESC
        ''', (self.id, host_id))
        return dictfetchall(cursor)

class Sharers(models.Model):
    customer = models.ForeignKey(Customer)
    customer_sharer_id = models.IntegerField(max_length = 10)
    code = models.CharField(max_length = 8, unique = True, db_index = True)
    redirect_link = models.ForeignKey(Full_Link, related_name='sharer_redirect_link')
    enabled = models.BooleanField(default = True)
    modified = models.DateTimeField(auto_now = True)
    created = models.DateTimeField(auto_now_add = True)

    def __unicode__(self):
        return self.code

class Clicks(models.Model):
    sharer = models.ForeignKey(Sharers)
    redirect_link = models.ForeignKey(Full_Link, related_name='click_redirect_link') # it could be different from sharers' redirect link because sharer's link can be changed.
    referrer = models.ForeignKey(Full_Link, blank=True, null=True)
    IP = models.ForeignKey(IP, blank=True, null=True)
    Agent = models.ForeignKey(User_Agent, blank=True, null=True)
    created = models.DateTimeField(auto_now_add = True)

class Action_Type(models.Model):
    customer = models.ForeignKey(Customer)
    action_name = models.CharField(max_length=20)
    description = models.CharField(max_length=250, blank=True, null=True)
    enabled = models.BooleanField(default = True)
    created = models.DateTimeField(auto_now_add=True)


class Actions(models.Model):
    click = models.ForeignKey(Clicks)
    action = models.ForeignKey(Action_Type)
    description = models.CharField(max_length=250, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
