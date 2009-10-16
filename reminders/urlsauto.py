from django.conf.urls.defaults import *

urlpatterns = patterns('reminders.views',
    url(r'^$', 'index'),
    url(r'^(?P<key_id>\d+)/$', 'detail'),
)
