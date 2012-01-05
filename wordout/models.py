from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from urlparse import urlparse
from lib import dictfetchall, force_subdomain, code_generator
from django.db.models import Count, Sum
from django.db import connection

#extend the user object. This is not the best way because I have to query the database once everytime. change it in version two


class HOST(models.Model):
    host_name = models.URLField()
    created = models.DateTimeField(auto_now_add = True)

    def __unicode__(self):
        return self.host_name

class IP(models.Model):
    address = models.IPAddressField()
    created = models.DateTimeField(auto_now_add = True)

    def __unicode__(self):
        return self.address

class User_Agent(models.Model):
    agent = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add = True)
    
    def __unicode__(self):
        return self.agent

class Full_Link(models.Model):
    host = models.ForeignKey(HOST)
    path = models.CharField(max_length=200)
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
    netloc = result.scheme + '://' + force_subdomain(result.netloc) #prefix www.
    netloc, created = HOST.objects.get_or_create(host_name = netloc)
    link, created = Full_Link.objects.get_or_create(host = netloc, path = path)
    return (link, created)


class Customer(models.Model):
    user = models.OneToOneField(User)
    client_key = models.CharField(max_length = 9, unique=True)
    api_key = models.CharField(max_length = 30, unique=True)
    message_title = models.CharField(max_length = 200, null=True, blank=True)
    message_body = models.TextField(null=True, blank=True)
    customergroup = models.ForeignKey(Customergroup)

    def __unicode__(self):
        return str(self.user)
 
    
    def display_sharers(self):
        
        #######I NEED EITHER BEN OR ERIN'S HELP ON THIS 
        ls = Sharer.objects.select_related().filter(customer = self).annotate(num = Count('click')).order_by('-created')
        return ls

    def display_sharers2(self):
        cursor = connection.cursor()
        #todo
        #only give redirect_link_id. need get the full redirect link
        #need get max sharer_id for the modal
        cursor.execute('''
        SELECT wordout_sharer.customer_sharer_id, wordout_sharer.code, wordout_sharer.redirect_link_id, wordout_sharer.enabled, COUNT(*) AS total_clicks, actions_groupwise.action_id, actions_groupwise.action_name, action_total
        FROM
            wordout_sharer
        INNER JOIN
            wordout_click
        ON wordout_sharer.id = wordout_click.sharer_id
        LEFT JOIN
        (
            SELECT wordout_action_type.action_id, wordout_action_type.action_name, wordout_action.click_id, COUNT(*) as action_total
            FROM
                wordout_action
            INNER JOIN
                wordout_action_type
            ON
                wordout_action.action_id = wordout_action_type.id
	    GROUP BY wordout_action_type.action_id
	) AS actions_groupwise
        ON
            (actions_groupswise.click_id = wordout_click.id)
        WHERE wordout_sharer.customer_id = %s 
	GROUP BY wordout_sharer.id, actions_groupwise.action_id
	''', [self.id])
        
        return dictfetchall(cursor)

        
    def display_referrer_by_sharer(self, customer_sharer_identifier):
        #show where the clicks come from by each sharer
        cursor = connection.cursor()
        cursor.execute('''
        SELECT wordout_click.id, wordout_click.referrer_id, COUNT(wordout_click.id) as clicks, wordout_host.host_name, wordout_full_link.path
        FROM wordout_click
        LEFT JOIN wordout_full_link
            ON wordout_full_link.id = wordout_click.referrer_id
        LEFT JOIN wordout_host
            ON wordout_full_link.host_id = wordout_host.id
        LEFT JOIN wordout_sharer
            ON wordout_sharer.id = wordout_click.sharer_id
        WHERE
            wordout_sharer.customer_id = %s AND wordout_sharer.customer_sharer_identifier = %s
        GROUP BY 
            wordout_click.referrer_id
        ORDER BY
            clicks DESC
        ''', (self.id, customer_sharer_identifier))
        return dictfetchall(cursor)

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
                    Sharer.objects.create(customer = self, customer_sharer_identifier = i, code = code, redirect_link = redirect_link)
   
    def change_redirect_link(self, new_redirect_link, sharer_ls):
        new_redirect_link, created = get_or_create_link(new_redirect_link)
        Sharer.objects.filter(customer=self, customer_sharer_identifier__in = sharer_ls).update(redirect_link = new_redirect_link)

    def disable_or_enable_sharer(self, sharer_ls, boolean):
        Sharer.objects.filter(customer=self, customer_sharer_identifier__in = sharer_ls).update(enabled = boolean)
    
    def update_title_and_body(self, message_title, message_body):
        self.message_title=message_title
        self.message_body=message_body
        self.save()

    def create_actiontype(self, customer_action_type_identifier, action_name, description):
        entry = Action_Type(customer=self, customer_action_type_identifier=customer_action_type_identifier, action_name=action_name, description=description)
        entry.save()
        
    def edit_actiontype(self, customer_action_type_identifier, action_name, description):
        action_type = Action_Type.objects.get(customer=self, customer_action_type_identifier = customer_action_type_identifier)
        action_type.action_name=action_name
        action_type.description=description
        action_type.save()

    def disable_or_enable_action(self, action_type_identifier_ls, boolean):
        Action_Type.objects.filter(customer=self, customer_action_type_identifier__in = action_type_identifier_ls).update(enabled = boolean)
    
   
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
        SELECT wordout_host.host_name, wordout_host.id, wordout_full_link.path, COUNT(wordout_click.id) as clicks
        FROM wordout_full_link
        LEFT JOIN wordout_host
            ON wordout_full_link.host_id = wordout_host.id
        LEFT JOIN wordout_click
            ON wordout_full_link.id = wordout_click.referrer_id
        LEFT JOIN wordout_sharer
            ON wordout_click.sharer_id = wordout_sharer.id
        WHERE wordout_sharer.customer_id = %s AND wordout_host.id = %s
        GROUP BY wordout_path
        ORDER BY clicks DESC
        ''', (self.id, host_id))
        return dictfetchall(cursor)

class Sharer(models.Model):
    customer = models.ForeignKey(Customer)
    customer_sharer_identifier = models.IntegerField(max_length = 10)
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

    def __unicode__(self):
        return 'Click from %s on %s' % (self.sharer, self.created)


class Action_Type(models.Model):
    customer = models.ForeignKey(Customer)
    customer_action_type_identifier = models.IntegerField(max_length=2)
    action_name = models.CharField(max_length=20)
    description = models.CharField(max_length=250, blank=True, null=True)
    enabled = models.BooleanField(default = True)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return 'Action %s created by %s' % (self.action_name, self.customer)


class Action(models.Model):
    click = models.ForeignKey(Click)
    action_type = models.ForeignKey(Action_Type)
    extra_data = models.CharField(max_length=250, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s on %s' % (self.action_type, self.created)
    

