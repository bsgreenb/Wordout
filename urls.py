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
    # Examples:
    # url(r'^$', 'django_wordout.views.home', name='home'),
    # url(r'^django_wordout/', include('django_wordout.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    

    #django plugin for change password and reset password
    (r'^password/change/$', password_change),
    (r'^password/change/done$', password_change_done),
    (r'^password_reset/$', password_reset),
    (r'^password_reset/done/$', password_reset_done),
    (r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm),
    (r'^reset/done/$', password_reset_complete),



    url(r'^admin/', include(admin.site.urls)),

)
