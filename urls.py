# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.contrib import admin

from ragendja.urlsauto import urlpatterns
from ragendja.auth.urls import urlpatterns as auth_patterns

from override.forms import UserRegistrationForm

admin.autodiscover()

handler500 = 'ragendja.views.server_error'

urlpatterns = auth_patterns + patterns('',
    ('^admin/(.*)', admin.site.root),
    (r'^$', 'welcome.views.index'),
    # Override the default registration form
    url(r'^account/register/$', 'registration.views.register',
        kwargs={'form_class': UserRegistrationForm,
                'template_name': 'override/registration_form.html'},
        name='registration_register'),
) + urlpatterns
