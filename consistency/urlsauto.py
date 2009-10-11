from django.conf.urls.defaults import *

import views

urlpatterns = patterns('consistency.views',
    (r'^$', 'index'),
)
