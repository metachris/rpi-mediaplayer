from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from main.views import *

from django.contrib.auth.decorators import login_required, permission_required

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Home
    url(r'^$', index_view, name='home'),

    url(r'^playlist_save/$', playlist_save, name="playlist_save"),
    url(r'^settings/$', settings_view, name="settings"),
    url(r'^settings/restore_defaults$', settings_restore, name="settings_restore"),
    url(r'^ajax/player_cmd$', ajax_cmd_playerd, name="ajax_player_cmd"),

    # Login, Logout
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^logout/$', LogoutView.as_view()),

    # Admin interface and admin docs
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
