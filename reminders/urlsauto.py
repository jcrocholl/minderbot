from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_list, object_detail

from models import Reminder

info_dict = {
    'queryset': Reminder.all(),
    'template_object_name': 'reminder',
}

urlpatterns = patterns('reminders.views',
    url(r'^$', 'index', name='reminder_list'),
    url(r'^(?P<object_id>[a-z0-9-]+)/$', object_detail, info_dict,
     name='reminder_detail'),
)
