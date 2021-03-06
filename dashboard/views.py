import logging
from datetime import datetime, timedelta

from django import forms
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User

from ragendja.template import render_to_response
from ragendja.auth.decorators import staff_only

from reminders.models import Reminder
from tags.models import Tag
from feedback.models import Feedback

RECENT_LIMIT = 5


class SuggestionForm(forms.Form):
    """
    URL input form.
    """
    title = forms.CharField(max_length=120,
        widget=forms.TextInput(attrs={'class': 'text span-12'}))
    slug = forms.CharField(max_length=120,
        widget=forms.TextInput(attrs={'class': 'text span-12'}))
    tags = forms.CharField(max_length=120,
        widget=forms.TextInput(attrs={'class': 'text span-12'}))
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


@staff_only
def index(request):
    """
    Display the current system status.
    """
    # Simple form to add new suggestions.
    suggestion_form = SuggestionForm(request.POST or None)
    if suggestion_form.is_valid():
        return submit_suggestion(request, suggestion_form)

    # Recent time intervals.
    day = datetime.now() - timedelta(hours=24)
    week = datetime.now() - timedelta(days=7)

    # Show newest suggestions.
    suggestion_count = Reminder.all().filter('owner', None).count()
    suggestion_count_24h = (Reminder.all().filter('owner', None)
                            .filter('created >', day).count())
    suggestion_count_7d = (Reminder.all().filter('owner', None)
                           .filter('created >', week).count())
    suggestion_list = (Reminder.all().filter('owner', None)
                       .order('-created').fetch(RECENT_LIMIT))

    # Show newest tags.
    tag_count = Tag.all().count()
    tag_count_24h = Tag.all().filter('created >', day).count()
    tag_count_7d = Tag.all().filter('created >', week).count()
    tag_list = Tag.all().order('-created').fetch(RECENT_LIMIT * 4)

    # Registered user accounts.
    user_count = User.all().count()
    user_count_24h = User.all().filter('date_joined >', day).count()
    user_count_7d = User.all().filter('date_joined >', week).count()
    user_list = User.all().order('-date_joined').fetch(RECENT_LIMIT)

    # Show newest feedback.
    # feedback_count = Feedback.all().count()
    # feedback_count_24h = Feedback.all().filter('submitted >', day).count()
    # feedback_count_7d = Feedback.all().filter('submitted >', week).count()
    # feedback_list = Feedback.all().order('-submitted').fetch(RECENT_LIMIT)
    return render_to_response(request, 'dashboard/index.html', locals())


def submit_suggestion(request, suggestion_form):
    """
    Save a new suggestion in the database.
    """
    slug = suggestion_form.cleaned_data['slug']
    tag_list = suggestion_form.cleaned_data['tags'].split()
    for tag_name in tag_list:
        tag = Tag.get_by_key_name(tag_name)
        if tag is None:
            tag = Tag(key_name=tag_name, count=0)
        tag.suggestions.append(slug)
        tag.count += 1
        tag.put()
    suggestion = Reminder(
        key_name=slug,
        title=suggestion_form.cleaned_data['title'],
        days=suggestion_form.cleaned_data['days'],
        months=suggestion_form.cleaned_data['months'],
        years=suggestion_form.cleaned_data['years'],
        miles=suggestion_form.cleaned_data['miles'],
        kilometers=suggestion_form.cleaned_data['kilometers'],
        tags=tag_list)
    logging.debug(suggestion)
    suggestion.put()
    return HttpResponseRedirect(suggestion.get_absolute_url())
