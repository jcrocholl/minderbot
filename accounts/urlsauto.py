from django.conf.urls.defaults import *

urlpatterns = patterns('accounts.views',
    url(r'^login/$', 'login'),
    url(r'^logout/$', 'logout'),
)
