from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_list, object_detail

from reminders.models import Reminder

info_dict = {
    'queryset': Reminder.all().filter('owner', None),
    'template_object_name': 'suggestion',
}

urlpatterns = patterns('',
    (r'^$', object_list, info_dict, 'suggestion_list'),
    (r'^(?P<object_id>[a-z0-9-]+)/$', object_detail, info_dict,
     'suggestion_detail'),
)
