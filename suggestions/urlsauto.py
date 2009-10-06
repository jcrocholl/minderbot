from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_list, object_detail

from models import Suggestion

info_dict = {
    'queryset': Suggestion.all(),
}

urlpatterns = patterns('',
    (r'^$', object_list, info_dict),
    (r'^(?P<object_id>[a-z0-9-]+)/$', object_detail, info_dict),
)
