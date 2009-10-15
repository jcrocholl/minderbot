from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_list, object_detail

from reminders.models import Reminder

info_dict = {
    'queryset': Reminder.all().filter('owner', None),
    'template_object_name': 'suggestion',
}

urlpatterns = patterns('suggestions.views',
    url(r'^$', object_list,
        dict(info_dict, template_name='suggestions/index.html'),
        name='suggestion_list'),
    url(r'^(?P<object_id>[a-z0-9-]+)/$', 'detail', name='suggestion_detail'),
)
