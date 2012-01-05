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

    #sharer
    (r'^createsharer/$', create_sharer_page),
    (r'^sharer/([0-9]+)/$', show_referrer_by_sharer),
    (r'^changelink/$', change_redirect_link_page),      
    (r'^disablesharer/$', disable_or_enable_sharer_page, {'action':'disable'}),
    (r'^enablesharer/$', disable_or_enable_sharer_page, {'action':'enable'}),

    #sharer plugin page
    (r'^pluginpage/$', sharer_plugin_page),
    (r'^editmsg/$', edit_msg_page),
    #action page
    (r'^actiontype/$', action_type_page),
    (r'^createactiontype/$', create_action_type_page),
    (r'^editactiontype/$', edit_action_type_page),
    (r'^disableaction/$', disable_or_enable_action_page, {'action':'disable'}),
    (r'^enableaction/$', disable_or_enable_action_page, {'action':'enable'}),
    
    #api page
    (r'api/overview/$', api_overview_page),
    #(r'api/overview/recordaction/$', api_overview_record_action_page),
    #(r'api/overview/clickstats/$', api_overview_clickstats_page),
    #(r'api/overview/actionstats/$', api_overview_actionstats_page),
    #(r'api/overview/sharerstats/$', api_overview_sharerstats_page),
    #(r'api/overview/plugininfo/$', api_overview_plugin_info_page),
    #(r'api/overview/actiontypelist/$', api_overview_action_type_list_page),
   # (r'api/overview/referrerbreakdown/$', api_overview_referrer_breakdown_page),



    (r'^referrer/$', referrer_page),
    (r'^referrer/([0-9]+)/$', path_page),
    (r'^api/([0-9A-Za-z]{9})/([0-9]+)/$', api_page),
    (r'^apisettings/$', api_settings_page),
    (r'^([0-9a-z]{6})/$', direct_page)
)
