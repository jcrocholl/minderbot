from django.conf.urls.defaults import *

urlpatterns = patterns('pages.views',
    (r'^(?P<page_name>[a-z0-9-]+)/$', 'page'),
)
