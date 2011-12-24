from django.contrib import admin
from django_wordout.wordout.models import *

class Full_LinkAdmin(admin.ModelAdmin):
    list_display = ('host', 'path')

class SharersAdmin(admin.ModelAdmin):
    list_display = ('customer', 'customer_sharer_id', 'code', 'redirect_link')

class ClicksAdmin(admin.ModelAdmin):
    list_display = ('sharer', 'redirect_link', 'referrer','IP', 'created')

class CustomergroupsAdmin(admin.ModelAdmin):
    list_display = ('id', 'max_users')

class ActionTypeAdmin(admin.ModelAdmin):
    list_display = ('customer', 'action_name', 'description')

class ActionsAdmin(admin.ModelAdmin):
    list_display =('click', 'action', 'description')


admin.site.register(Customer)
admin.site.register(HOST)
admin.site.register(Path)
admin.site.register(IP)
admin.site.register(User_Agent)
admin.site.register(Full_Link, Full_LinkAdmin)
admin.site.register(Sharers, SharersAdmin)
admin.site.register(Clicks, ClicksAdmin)
admin.site.register(Customergroups, CustomergroupsAdmin)
admin.site.register(Action_Type, ActionTypeAdmin)
admin.site.register(Actions, ActionsAdmin)
