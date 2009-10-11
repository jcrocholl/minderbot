from django.conf.urls.defaults import *

import views

urlpatterns = patterns('dashboard.views',
    (r'^$', 'index'),
    (r'^check/$', 'check'),
)
