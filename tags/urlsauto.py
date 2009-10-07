from django.conf.urls.defaults import *

urlpatterns = patterns('tags.views',
    url(r'^$', 'index'),
    url(r'^(?P<key_name>[a-z0-9]+)/$', 'detail'),
)
