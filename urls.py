#from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login, password_reset, password_reset_done, password_reset_confirm, password_reset_complete, password_change, password_change_done
from django.contrib import admin
admin.autodiscover()

from wordout.custom_decorator import anonymous_required
from wordout import views, api_views

urlpatterns = patterns('',
    (r'^$', views.main_page),
    (r'^accounts/login/$', anonymous_required(login)),
    (r'^logout/$', views.logout_page),
    (r'^register/$', anonymous_required(views.register_page)),
    
    #django plugin for change password and reset password
    (r'^password/change/$', password_change),
    (r'^password/change/done$', password_change_done),
    #(r'^password_reset/$', password_reset),
    #(r'^password_reset/done/$', password_reset_done),
    #(r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm),
    #(r'^reset/done/$', password_reset_complete),
    url(r'^admin/', include(admin.site.urls)),

    #sharer
    (r'^createsharer/$', views.create_sharer_page),
    (r'^sharer/([0-9]+)/$', views.show_referrer_by_sharer),
    (r'^changelink/$', views.change_redirect_link_page),
    (r'^disablesharer/$', views.disable_or_enable_sharer_page, {'action':'disable'}),
    (r'^enablesharer/$', views.disable_or_enable_sharer_page, {'action':'enable'}),

    #sharer plugin page
    (r'^pluginpage/$', views.sharer_plugin_page),
    (r'^editmsg/$', views.edit_msg_page),


    #display sharer page (the actual promote page plus this sharer's analysis)
    (r'^share/(?P<client_key>\w{9})/(?P<sharer_identifier>[0-9]+)/$', views.display_sharer_plugin_page),

    #action page
    (r'^actiontype/$', views.action_type_page),
    (r'^createactiontype/$', views.create_action_type_page),
    (r'^editactiontype/$', views.edit_action_type_page),
    (r'^disableaction/$', views.disable_or_enable_action_page, {'action':'disable'}),
    (r'^enableaction/$', views.disable_or_enable_action_page, {'action':'enable'}),


    #api doc page
    (r'^apidoc/overview/$', api_views.apidoc_overview_page),
    (r'^apidoc/doAction/$', api_views.apidoc_do_action_page),
    (r'^apidoc/getAllSharers/$', api_views.apidoc_get_all_sharers_page),
    (r'^apidoc/getSharerInfo/$', api_views.apidoc_get_sharer_info_page),
    (r'^apidoc/addSharer/$', api_views.apidoc_add_sharer),
    (r'^apidoc/toggleSharer/$', api_views.apidoc_toggle_sharer),
    (r'^apidoc/getActionType/$', api_views.apidoc_get_action_type),
    
    #apicall I think this could go into a subdomain. decide later
    (r'^api/doAction/(?P<api_key>\w{30})/$', api_views.api_do_action_page),
    (r'^api/addSharer/(?P<api_key>\w{30})/$', api_views.api_add_sharer_page),
    (r'^api/toggleSharer/(?P<api_key>\w{30})/$', api_views.api_toggle_sharer_page),
    (r'^api/getAllSharers/(?P<api_key>\w{30})/$', api_views.api_get_all_sharers_page),
    (r'^api/getSharerInfoById/(?P<api_key>\w{30})/$', api_views.api_get_sharer_by_identifier),
    (r'^api/getActionTypes/(?P<api_key>\w{30})/$', api_views.api_get_action_type_page),

    (r'^referrer/$', views.referrer_page),
    (r'^referrer/([0-9]+)/$', views.path_page),
    (r'^([0-9a-z]{6})/$', views.direct_page)
)

'''
if settings.DEBUG:
    # some debug pages
    urlpatterns += patterns('',
        (r'^debuginfo/$', ''),
    )
'''