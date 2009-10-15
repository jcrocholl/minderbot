from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from ragendja.template import render_to_response

from reminders.models import Reminder


@login_required
def index(request):
    """
    List all reminders for a registered user.
    """
    reminder_list = Reminder.all().filter('owner', request.user)
    return render_to_response(
        request, 'reminders/index.html', locals())
