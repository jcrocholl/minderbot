from django import forms
from django.http import HttpResponseRedirect

from ragendja.template import render_to_response
from ragendja.dbutils import get_object_or_404

from reminders.models import Reminder


class ReminderForm(forms.Form):
    title = forms.CharField(max_length=100,
        widget=forms.TextInput(attrs={'class': 'text span-17 h1'}))
    interval = forms.CharField(max_length=100,
        widget=forms.TextInput(attrs={'class': 'text span-5'}))
    tags = forms.CharField(max_length=200,
        widget=forms.TextInput(attrs={'class': 'text span-10'}))
    email = forms.EmailField(max_length=200,
        widget=forms.TextInput(attrs={'class': 'text span-10'}))

    class Meta:
        model = Reminder
        fields = 'title tags interval'.split()


def detail(request, object_id):
    """
    List all reminders for a registered user.
    """
    suggestion = get_object_or_404(Reminder, key_name=object_id)
    reminder_form = ReminderForm(request.POST or {
            'title': suggestion.title,
            'tags': ' '.join(suggestion.tags),
            'interval': suggestion.interval()})
    reminders = Reminder.all().filter('user=', request.user)
    return render_to_response(
        request, 'suggestions/detail.html', locals())
