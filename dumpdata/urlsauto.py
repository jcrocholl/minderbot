from django.conf.urls.defaults import *

urlpatterns = patterns('dumpdata.views',
    url(r'^(?P<app_name>[a-z]+).(?P<format>[a-z]+)$', 'dump_app'),
)
