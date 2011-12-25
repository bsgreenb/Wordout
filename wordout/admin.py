from django.contrib import admin
from django_wordout.wordout.models import *

class Full_LinkAdmin(admin.ModelAdmin):
    list_display = ('host', 'path')

class SharerAdmin(admin.ModelAdmin):
    list_display = ('customer', 'customer_sharer_id', 'code', 'redirect_link')

class ClickAdmin(admin.ModelAdmin):
    list_display = ('sharer', 'redirect_link', 'referrer','IP', 'created')

class CustomergroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'max_users', 'max_actions')

class ActionTypeAdmin(admin.ModelAdmin):
    list_display = ('customer', 'action_name', 'description')

class ActionAdmin(admin.ModelAdmin):
    list_display =('click', 'action', 'description')


admin.site.register(Customer)
admin.site.register(HOST)
admin.site.register(Path)
admin.site.register(IP)
admin.site.register(User_Agent)
admin.site.register(Full_Link, Full_LinkAdmin)
admin.site.register(Sharer, SharerAdmin)
admin.site.register(Click, ClickAdmin)
admin.site.register(Customergroup, CustomergroupAdmin)
admin.site.register(Action_Type, ActionTypeAdmin)
admin.site.register(Action, ActionAdmin)
