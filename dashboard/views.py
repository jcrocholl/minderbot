from datetime import datetime, timedelta

from django import forms
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User

from ragendja.template import render_to_response
from ragendja.auth.decorators import staff_only

from suggestions.models import Suggestion
from feedback.models import Feedback

RECENT_LIMIT = 5


class SuggestionForm(forms.Form):
    """
    URL input form.
    """
    title = forms.CharField(max_length=120, label="Title",
        widget=forms.TextInput(attrs={'class': 'text span-10'}))
    slug = forms.CharField(max_length=120, label="Slug",
        widget=forms.TextInput(attrs={'class': 'text span-10'}))
    tags = forms.CharField(max_length=120, label="Tags",
        widget=forms.TextInput(attrs={'class': 'text span-10'}))


@staff_only
def index(request):
    day = datetime.now() - timedelta(hours=24)
    week = datetime.now() - timedelta(days=7)
    # Registered user accounts.
    user_count = User.all().count()
    user_count_24h = User.all().filter('date_joined >', day).count()
    user_count_7days = User.all().filter('date_joined >', week).count()
    user_list = User.all().order('-date_joined').fetch(RECENT_LIMIT)
    # Feedback for website improvements.
    feedback_count = Feedback.all().count()
    feedback_count_24h = Feedback.all().filter('submitted >', day).count()
    feedback_count_7days = Feedback.all().filter('submitted >', week).count()
    feedback_list = Feedback.all().order('-submitted').fetch(RECENT_LIMIT)
    # Reminder suggestions.
    suggestion_count = Suggestion.all().count()
    suggestion_count_24h = Suggestion.all().filter('created >', day).count()
    suggestion_count_7days = Suggestion.all().filter('created >', week).count()
    suggestion_list = Suggestion.all().order('-created').fetch(RECENT_LIMIT)
    # Simple form to add new suggestions.
    suggestion_form = SuggestionForm(request.POST or None)
    if suggestion_form.is_valid():
        suggestion = Suggestion(
            key_name=suggestion_form.cleaned_data['slug'],
            title=suggestion_form.cleaned_data['title'],
            submitter=request.user)
        suggestion.put()
        return HttpResponseRedirect(suggestion.get_absolute_url())
    return render_to_response(request, 'dashboard/index.html', locals())
