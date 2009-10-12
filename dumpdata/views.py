from ragendja.template import render_to_response

from reminders.models import Reminder
from tags.models import Tag


def dump_app(request, app_name, format):
    if app_name == 'reminders':
        reminder_list = Reminder.all()
    elif app_name == 'tags':
        tag_list = Tag.all()
    template = 'dumpdata/%s.%s' % (app_name, format)
    return render_to_response(request, template, locals())


