from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from main.views import LogoutView
from main.views import *

from django.contrib.auth.decorators import login_required, permission_required

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Home
    url(r'^$', TemplateView.as_view(template_name="index.html"), name='home'),

    # Login, Logout
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^logout/$', LogoutView.as_view()),

    # Admin interface and admin docs
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
