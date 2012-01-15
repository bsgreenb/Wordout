from django.db import models
from django.db.models import Count
from django.contrib.auth.models import User

from lib import code_generator, force_url_format

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
    result = force_url_format(url) #regular expression forcing http(s)://subdomain.example.extension
    netloc, path = result.group(1), result.group(2)
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
 
    
    def display_sharers(self, sharer_identifier = None):
        results = []

        # Create a dictionary of this Customer's actions
        action_type_ls = Action_Type.objects.filter(customer = self).order_by('-created')

        # Next we get a list of their sharers and total clicks
        sharer_ls = Sharer.objects.select_related().filter(customer = self)

        if sharer_identifier:  #
            sharer_ls = sharer_ls.filter(customer_sharer_identifier = sharer_identifier) # for api_get_sharer_by_identifier

        sharer_ls = sharer_ls.annotate(click_total = Count('click__id')).order_by('-created').values() # this returns sharer info and total clicks

        action_ls = Action.objects.select_related().filter(action_type__customer = self) # A list of all actions by this customer's sharers

        #What will we do next: loop through sharer_ls, then use filter on sharer and action type to get the # of actions for that one

        for sharer in sharer_ls:
            sharer['action_type_set'] = []
            for action_type in action_type_ls:
                action_count = action_ls.filter(click__sharer=sharer['id'], action_type=action_type).count()
                sharer['action_type_set'].append({
                    'action_type_name': action_type.action_name,
                    'action_total': action_count
                })

            results.append(sharer)

        return results

    def display_referrer_by_sharer(self, customer_sharer_identifier):
        #show where the clicks come from by each sharer
        sharer = Sharer.objects.get(customer = self, customer_sharer_identifier=customer_sharer_identifier)
        ls = Full_Link.objects.filter(click__sharer=sharer).annotate(clicks=Count('click__id')).order_by('clicks')
        #haven't gotten the offical way to serialization models. need replace the code below in the future
        data = []
        if ls:
            for i in ls:
                holder = {
                    'referrer':i.host.host_name + i.path,
                    'clicks':i.clicks
                }
                data.append(holder)

           #data = [{'referrer': i.host.host_name + i.path, 'clicks': i.clicks} for i in ls]
        return data


    def create_sharer(self, start, end, redirect_link):
        redirect_link, created = get_or_create_link(redirect_link)

        for i in range(start, end+1):
            while True:
                code = code_generator()
                try:
                    Sharer.objects.get(code = code)
                except Sharer.DoesNotExist:
                    Sharer.objects.create(customer = self, customer_sharer_identifier = i, code = code, redirect_link = redirect_link)
                    break
   
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
        ls = Full_Link.objects.filter(click__sharer__in = self.sharer_set.all()).annotate(clicks=Count('click__id')).order_by('clicks')
        return ls

    def display_path(self, host_id):
        ls = Full_Link.objects.filter(click__sharer__in = self.sharer_set.all(), host__id = host_id).annotate(clicks=Count('click__id')).order_by('clicks')
        data = []
        if ls:
            for i in ls:
                holder = {
                    'referrer':i.host.host_name + i.path,
                    'clicks':i.clicks
                }
                data.append(holder)
        return data

    ##### api call #####
    def api_add_action(self, click, action_type, extra_data):
        action = Action.objects.create(click=click, action_type=action_type, extra_data=extra_data)


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
    

