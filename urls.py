from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login, logout, password_reset, password_reset_done, password_reset_confirm, password_reset_complete, password_change, password_change_done

from wordout.views import *
from django.contrib import admin
admin.autodiscover()
from wordout.custom_decorator import anonymous_required
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
    (r'^$', main_page),
    (r'^accounts/login/$', anonymous_required(login)),
    (r'^logout/$', logout_page),
    (r'^register/$', anonymous_required(register_page)),
    
    #django plugin for change password and reset password
    (r'^password/change/$', password_change),
    (r'^password/change/done$', password_change_done),
    #(r'^password_reset/$', password_reset),
    #(r'^password_reset/done/$', password_reset_done),
    #(r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm),
    #(r'^reset/done/$', password_reset_complete),
    url(r'^admin/', include(admin.site.urls)),

    #those two create identifier page should be in module instead of page and use ajax to send query

    (r'^createnumeric/$', create_numeric_page),
    (r'^identifier/([0-9]+)/$', show_referrer_by_ident),
    (r'^editident/$', edit_identifier_page),      
    (r'^referrer/$', referrer_page),
    (r'^referrer/([0-9]+)/$', path_page),
    (r'^api/$', api_page),
    (r'^([0-9a-z]{6})/$', direct_page),
)
