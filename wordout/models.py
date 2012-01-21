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
    max_users = models.PositiveIntegerField(max_length = 10)
    max_actions = models.PositiveIntegerField(max_length = 2)
    
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

    def display_sharers(self, customer_sharer_identifier = None, order_by='created', desc=True, action_type_id=None, page_number=1, results_per_page = 30):

        def sharers_by_action_count_with_total_clicks(action_type_id):
            """Gives a queryset sharers, ordered by a given action type (action_type_id), with the total number of clicks"""
            if desc:
                direction = 'DESC'
            else:
                direction = 'ASC'

            sharers_by_action_count = Sharer.objects.raw('''
            SELECT wordout_sharer.id COUNT(actions_of_type.id) AS action_count
            FROM
            wordout_customer
            INNER JOIN wordout_sharer
             ON wordout_sharer.customer_id = wordout_customer.id
            LEFT JOIN wordout_click
             ON wordout_sharer.id = wordout_click.sharer_id
            LEFT JOIN
            (SELECT wordout_action.id, wordout_action.click_id
            FROM wordout_action
            WHERE
            wordout_action.action_type_id = %s) as actions_of_type
             ON actions_of_type.click_id = wordout_click.id
            WHERE wordout_customer.id = %s
            GROUP BY wordout_sharer.id
            ORDER BY action_count %s
            ''', [action_type_id, self.id, direction])

            sharers_by_action_count = (sharer.id for sharer in sharers_by_action_count)

            return Sharer.objects.select_related().filter(id__in=sharers_by_action_count).annotate(click_total = Count('click__id')) #Note: we select_related() so that we can access everything we need later

        results = []
        if customer_sharer_identifier: # they specified a specific sharer rather than asking to sort by some criteria
            try:
                sharer_ls_with_total_clicks = Sharer.objects.get(customer=self,customer_sharer_identifier=customer_sharer_identifier).annotate(click_total = Count('click__id'))
            except Sharer.DoesNotExist:
                return [] # Most likely either a hacker, or they sent an incorrect sharer_identifier through the API
        else: #We are to return a page of sharers sorted in the specified fashion.
            if order_by == 'action_count': #we have to make a special query for when they want to sort by the count of a specific action
                sharer_ls_with_total_clicks = sharers_by_action_count_with_total_clicks(action_type_id)
            else:
                #TODO: Write this part out once I'm done with the action_count logic
                #Note: we select_related() so that we can access everything we need later
                sharer_ls_with_total_clicks = Sharer.objects.select_related().filter(customer=self).annotate(click_total = Count('click__id')) #get the total number of clicks for every sharer of this customer

                #order by the specified field
                if desc:
                    order_by = '-' + order_by
                sharer_ls_with_total_clicks.order_by(order_by)

            # Now it's time to slice (regardless of what they're ordering by)
            page_number -= 1 #Because SQL's limit's are 0 based, but the page_number's API users provide are 1-based
            start = results_per_page * page_number
            end = results_per_page * (page_number + 1)
            sharer_ls_with_total_clicks = sharer_ls_with_total_clicks[start:end]

        #Next we want to get the total # of each of type of action for these sharers. We force it to a list right array so we don't need to requery every time to match it to the sharers
        sharer_action_counts = Action.objects.select_related().filter(click__sharer__in=sharer_ls_with_total_clicks).values('click__sharer_id','action_type_id').annotate(action_total=Count('id'))

        #With our sharers+total_clicks, and the number of actions of each type for each sharer, it's time to build our result dictionary

        # First, create a dictionary of this Customer's actions for storing this stuff
        action_type_ls = Action_Type.objects.filter(customer = self)
        action_type_arr = {action_type.action_name: 0 for action_type in action_type_ls} # A dictionary for all the action_names, with counts as values initialized to 0.

        for sharer in sharer_ls_with_total_clicks:
            # build sharer dictionary instead of return query set. issues: 1. DateTime can't be json dumped. 2. queryset gives redirect_link_id instead of actual redirect link.

            sharer_dict = {
                'sharer_identifier': sharer.customer_sharer_identifier,
                'code': sharer.code,
                'redirect_link': sharer.redirect_link.host.host_name + sharer.redirect_link.path,
                'enabled': sharer.enabled,
                'click_total': sharer.click_total,
                'action_type_set': action_type_arr
            }

            for sharer_action_count in sharer_action_counts:
                if sharer_action_count.sharer_id == sharer.id:
                    sharer_dict['action_type_set'][sharer_action_count.action_name] = sharer_action_count.action_total

            results.append(sharer_dict)

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
    customer_sharer_identifier = models.PositiveIntegerField(max_length = 10)
    code = models.CharField(max_length = 8, unique = True, db_index = True)
    redirect_link = models.ForeignKey(Full_Link, related_name='sharer_redirect_link')
    enabled = models.BooleanField(default = True)
    modified = models.DateTimeField(auto_now = True)
    created = models.DateTimeField(auto_now_add = True)

    def __unicode__(self):
        return unicode(self.id)

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
    customer_action_type_identifier = models.PositiveIntegerField(max_length=2)
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
    

