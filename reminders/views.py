import logging

from django import forms
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Message
from django.contrib.auth.decorators import login_required

from ragendja.template import render_to_response
from ragendja.dbutils import get_object_or_404

from reminders.models import Reminder


@login_required
def index(request):
    """
    List all reminders for a registered user.
    """
    reminder_list = Reminder.all().filter('owner', request.user)
    return render_to_response(request, 'reminders/index.html', locals())


class ReminderForm(forms.ModelForm):
    title = forms.CharField(max_length=100,
        widget=forms.TextInput(attrs={'class': 'h1 text span-17'}))
    tags = forms.CharField(max_length=200,
        widget=forms.TextInput(attrs={'class': 'text span-10'}))
    days = forms.IntegerField(required=False,
        widget=forms.TextInput(attrs={'class': 'text span-1'}))
    months = forms.IntegerField(required=False,
        widget=forms.TextInput(attrs={'class': 'text span-1'}))
    years = forms.IntegerField(required=False,
        widget=forms.TextInput(attrs={'class': 'text span-1'}))
    miles = forms.IntegerField(required=False,
        widget=forms.TextInput(attrs={'class': 'text span-2'}))
    kilometers = forms.IntegerField(required=False,
        widget=forms.TextInput(attrs={'class': 'text span-2'}))

    class Meta:
        model = Reminder
        exclude = 'owner previous next created'.split()


def detail(request, key_id):
    reminder = get_object_or_404(Reminder, id=int(key_id))
    reminder_form = ReminderForm(request.POST or None, instance=reminder)
    if reminder_form.is_valid():
        reminder_form.save()
        Message(message='<p class="success message">%s</p>' %
                "Your changes were saved successfully.",
                user=request.user).put()
    return render_to_response(request, 'reminders/detail.html', locals())
