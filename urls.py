from django.conf.urls.defaults import *
from django.contrib import admin

from ragendja.urlsauto import urlpatterns

admin.autodiscover()

handler500 = 'ragendja.views.server_error'

urlpatterns = patterns('',
    ('^admin/(.*)', admin.site.root),
    (r'^$', 'pages.views.page', {'page_name': 'welcome'}),
) + urlpatterns
