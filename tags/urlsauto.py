from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',
    (r'^$', views.index),
                       # (r'^(?P<tag>[a-z0-9]+)$/', views.detail),
)
