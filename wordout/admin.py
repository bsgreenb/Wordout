from django.contrib import admin
from django_wordout.wordout.models import *

class Full_LinkAdmin(admin.ModelAdmin):
    list_display = ('host', 'path')

class IdentifiersAdmin(admin.ModelAdmin):
    list_display = ('customer', 'identifier', 'code', 'redirect_link')

class RequestAdmin(admin.ModelAdmin):
    list_display = ('referral_code', 'redirect_link', 'referrer','IP', 'created')

class CustomergroupsAdmin(admin.ModelAdmin):
    list_display = ('id', 'max_users')

admin.site.register(Customer)
admin.site.register(HOST)
admin.site.register(Path)
admin.site.register(IP)
admin.site.register(User_Agent)
admin.site.register(Full_Link, Full_LinkAdmin)
admin.site.register(Identifiers, IdentifiersAdmin)
admin.site.register(Request, RequestAdmin)
admin.site.register(Customergroups, CustomergroupsAdmin)
