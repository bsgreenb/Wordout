from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login, logout
from wordout.views import *
from django.contrib import admin
admin.autodiscover()
from wordout.custom_decorator import anonymous_required

urlpatterns = patterns('',
    (r'^$', main_page),
    (r'^login/$', anonymous_required(login)),
    (r'^logout/$', logout_page),
    (r'^register/$', anonymous_required(register_page)),
    # Examples:
    # url(r'^$', 'django_wordout.views.home', name='home'),
    # url(r'^django_wordout/', include('django_wordout.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
