from datetime import datetime, timedelta

from django import forms
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User

from ragendja.template import render_to_response
from ragendja.auth.decorators import staff_only

from suggestions.models import Suggestion
from tags.models import Tag
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
    # Simple form to add new suggestions.
    suggestion_form = SuggestionForm(request.POST or None)
    if suggestion_form.is_valid():
        return submit_suggestion(request, suggestion_form)
    day = datetime.now() - timedelta(hours=24)
    week = datetime.now() - timedelta(days=7)
    # Reminder suggestions.
    suggestion_count = Suggestion.all().count()
    suggestion_count_24h = Suggestion.all().filter('created >', day).count()
    suggestion_count_7days = Suggestion.all().filter('created >', week).count()
    suggestion_list = Suggestion.all().order('-created').fetch(RECENT_LIMIT)
    # Tags for suggestions.
    tag_count = Tag.all().count()
    tag_count_24h = Tag.all().filter('created >', day).count()
    tag_count_7days = Tag.all().filter('created >', week).count()
    tag_list = Tag.all().order('-created').fetch(RECENT_LIMIT * 4)
    # Feedback for website improvements.
    # feedback_count = Feedback.all().count()
    # feedback_count_24h = Feedback.all().filter('submitted >', day).count()
    # feedback_count_7days = Feedback.all().filter('submitted >', week).count()
    # feedback_list = Feedback.all().order('-submitted').fetch(RECENT_LIMIT)
    # Registered user accounts.
    user_count = User.all().count()
    user_count_24h = User.all().filter('date_joined >', day).count()
    user_count_7days = User.all().filter('date_joined >', week).count()
    user_list = User.all().order('-date_joined').fetch(RECENT_LIMIT)
    return render_to_response(request, 'dashboard/index.html', locals())


def submit_suggestion(request, suggestion_form):
    tag_list = suggestion_form.cleaned_data['tags'].split()
    suggestion = Suggestion(
        author=request.user,
        key_name=suggestion_form.cleaned_data['slug'],
        title=suggestion_form.cleaned_data['title'],
        tags=tag_list,
        submitter=request.user)
    suggestion.put()
    for tag_name in tag_list:
        tag = Tag.get_by_key_name(tag_name)
        if tag is None:
            tag = Tag(key_name=tag_name, count=0)
        tag.suggestions.append(suggestion.key().name())
        tag.count += 1
        tag.put()
    return HttpResponseRedirect(suggestion.get_absolute_url())


def consistency(request):
    suggestion_list = Suggestion.all().fetch(1000)
    suggestion_names = [s.key().name() for s in suggestion_list]
    tag_list = Tag.all().fetch(1000)
    tag_names = [tag.key().name() for tag in tag_list]
    missing_tag_list = []
    for suggestion in suggestion_list:
        for tag in suggestion.tags:
            if tag not in tag_names:
                missing_tag_list.append((tag, suggestion))
    missing_suggestion_list = []
    for tag in tag_list:
        for suggestion in tag.suggestions:
            if suggestion not in suggestion_names:
                missing_suggestion_list.append((suggestion, tag))
    return render_to_response(request, 'dashboard/consistency.html', locals())
