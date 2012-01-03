from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from urlparse import urlparse
from lib import dictfetchall, force_subdomain, code_generator
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

class Customergroup(models.Model): # identify paid/unpaid users
    max_users = models.IntegerField(max_length = 10)
    max_actions = models.IntegerField(max_length = 2)
    
    def __unicode__(self):
        return str(self.id)

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
    customergroup = models.ForeignKey(Customergroup)

    def __unicode__(self):
        return str(self.user)

    def create_sharer(self, start, end, redirect_link):
        redirect_link, created = get_or_create_link(redirect_link)

        for i in range(start, end+1):
            loop = True
            while loop == True:
                code = code_generator()
                try:
                    Sharer.objects.get(code = code)
                except Sharer.DoesNotExist:
                    loop = False
                    Sharer.objects.create(customer = self, customer_sharer_id = i, code = code, redirect_link = redirect_link)
   
    def change_redirect_link(self, new_redirect_link, sharer_ls):
        new_redirect_link, created = get_or_create_link(new_redirect_link)
        Sharer.objects.filter(customer=self, customer_sharer_id__in = sharer_ls).update(redirect_link = new_redirect_link)

    def disable_or_enable_sharer(self, sharer_ls, boolean):
        Sharer.objects.filter(customer=self, customer_sharer_id__in = sharer_ls).update(enabled = boolean)
    
    def update_title_and_body(self, message_title, message_body):
        self.message_title=message_title
        self.message_body=message_body
        self.save()
        #Customer.objects.get(user=self).update(message_title=message_title, message_body=message_body)

    def create_actiontype(self, action_id, action_name, description):
        entry = Action_Type(customer=self, action_id=action_id, action_name=action_name, description=description)
        entry.save()
        
    def edit_actiontype(self, action_id, action_name, description):
        action_type = Action_Type.objects.get(customer=self, action_id = action_id)
        action_type.action_name=action_name
        action_type.description=description
        action_type.save()

    def disable_or_enable_action(self, action_ls, boolean):
        Action_Type.objects.filter(customer=self, action_id__in = action_ls).update(enabled = boolean)
    
    def display_sharers(self):
        
        #######I NEED EITHER BEN OR ERIN'S HELP ON THIS 
        ls = Sharer.objects.select_related().filter(customer = self).annotate(num = Count('click')).order_by('-created')
        return ls
        
    def display_referrer_by_sharer(self, customer_sharer_id):
        #show where the clicks come from by each sharer
        cursor = connection.cursor()
        cursor.execute('''
        SELECT wordout_click.id, wordout_click.referrer_id, count(wordout_click.id) as clicks, wordout_host.host_name, wordout_path.path_loc
        FROM wordout_click
        LEFT JOIN wordout_full_link
            ON wordout_full_link.id = wordout_click.referrer_id
        LEFT JOIN wordout_host
            ON wordout_full_link.host_id = wordout_host.id
        LEFT JOIN wordout_path
            ON wordout_full_link.path_id = wordout_path.id
        LEFT JOIN wordout_sharer
            ON wordout_sharer.id = wordout_click.sharer_id
        WHERE
            wordout_sharer.customer_id = %s AND wordout_sharer.customer_sharer_id = %s
        GROUP BY 
            wordout_click.referrer_id
        ORDER BY
            clicks DESC
        ''', (self.id, customer_sharer_id))
        return dictfetchall(cursor)

    def display_referrer(self):
        cursor = connection.cursor()
        cursor.execute('''
        SELECT wordout_host.id, wordout_host.host_name, COUNT(wordout_click.id) as clicks
        FROM wordout_host
        LEFT JOIN wordout_full_link
            ON wordout_full_link.host_id = wordout_host.id
        LEFT JOIN wordout_click
            ON wordout_full_link.id = wordout_click.referrer_id
        LEFT JOIN wordout_sharer
            ON wordout_click.sharer_id = wordout_sharer.id
        WHERE
            wordout_sharer.customer_id = %s
        GROUP BY
            wordout_host.id
        ORDER BY
            clicks DESC
        ''', [self.id])
        return dictfetchall(cursor)


    def display_path(self, host_id):
        cursor = connection.cursor()
        cursor.execute('''
        SELECT wordout_path.id, wordout_path.path_loc, wordout_host.host_name, wordout_host.id, COUNT(wordout_click.id) as clicks
        FROM wordout_path
        LEFT JOIN wordout_full_link
            ON wordout_full_link.path_id = wordout_path.id
        LEFT JOIN wordout_host
            ON wordout_full_link.host_id = wordout_host.id
        LEFT JOIN wordout_click
            ON wordout_full_link.id = wordout_click.referrer_id
        LEFT JOIN wordout_sharer
            ON wordout_click.sharer_id = wordout_sharer.id
        WHERE wordout_sharer.customer_id = %s AND wordout_host.id = %s
        GROUP BY wordout_path.id
        ORDER BY clicks DESC
        ''', (self.id, host_id))
        return dictfetchall(cursor)

class Sharer(models.Model):
    customer = models.ForeignKey(Customer)
    customer_sharer_id = models.IntegerField(max_length = 10)
    code = models.CharField(max_length = 8, unique = True, db_index = True)
    redirect_link = models.ForeignKey(Full_Link, related_name='sharer_redirect_link')
    enabled = models.BooleanField(default = True)
    modified = models.DateTimeField(auto_now = True)
    created = models.DateTimeField(auto_now_add = True)

    def __unicode__(self):
        return self.code

class Click(models.Model):
    sharer = models.ForeignKey(Sharer)
    redirect_link = models.ForeignKey(Full_Link, related_name='click_redirect_link') # it could be different from sharers' redirect link because sharer's link can be changed.
    referrer = models.ForeignKey(Full_Link, blank=True, null=True)
    IP = models.ForeignKey(IP, blank=True, null=True)
    Agent = models.ForeignKey(User_Agent, blank=True, null=True)
    created = models.DateTimeField(auto_now_add = True)

class Action_Type(models.Model):
    customer = models.ForeignKey(Customer)
    action_id = models.IntegerField(max_length=2)
    action_name = models.CharField(max_length=20)
    description = models.CharField(max_length=250, blank=True, null=True)
    enabled = models.BooleanField(default = True)
    created = models.DateTimeField(auto_now_add=True)


class Action(models.Model):
    click = models.ForeignKey(Click)
    action = models.ForeignKey(Action_Type)
    description = models.CharField(max_length=250, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
