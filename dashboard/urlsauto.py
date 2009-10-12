from django.conf.urls.defaults import *

urlpatterns = patterns('dashboard.views',
    (r'^$', 'index'),
)
