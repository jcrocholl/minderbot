import logging
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
        widget=forms.TextInput(attrs={'class': 'text span-1'}))
    kilometers = forms.IntegerField(required=False,
        widget=forms.TextInput(attrs={'class': 'text span-1'}))


class ActionForm(forms.Form):
    """
    Actions to fix inconsistent tag references.
    """
    create_tags = forms.CharField(required=False)
    delete_tag_suggestions = forms.CharField(required=False)
    delete_empty_tags = forms.CharField(required=False)
    create_tag_suggestions = forms.CharField(required=False)
    create_suggestion_tags = forms.CharField(required=False)
    adjust_tag_count = forms.CharField(required=False)
    adjust_tag_created = forms.CharField(required=False)


@staff_only
def index(request):
    # Simple form to add new suggestions.
    suggestion_form = SuggestionForm(request.POST or None)
    if suggestion_form.is_valid():
        return submit_suggestion(request, suggestion_form)

    # Get all suggestions.
    suggestion_list = Suggestion.all().fetch(1000) # TODO: fetch unlimited
    suggestion_dict = {}
    for suggestion in suggestion_list:
        suggestion_dict[suggestion.key().name()] = suggestion

    # Get all tags.
    tag_list = Tag.all().fetch(1000) # TODO: fetch unlimited
    tag_dict = {}
    for tag in tag_list:
        tag_dict[tag.key().name()] = tag

    # Check for missing tags or missing references to suggestions.
    missing_tags = []
    missing_tag_suggestions = []
    for suggestion in suggestion_list:
        for tag in suggestion.tags:
            if tag not in tag_dict:
                missing_tags.append((tag, suggestion))
                continue
            tag = tag_dict[tag]
            if suggestion.key().name() not in tag.suggestions:
                missing_tag_suggestions.append((tag, suggestion))
    missing_tags.sort()
    missing_tag_suggestions.sort(key=lambda pair: pair[0].key().name())

    # Check for missing suggestions or missing references to tags.
    incorrect_tag_count = []
    incorrect_tag_created = []
    missing_suggestions = []
    missing_suggestion_tags = []
    empty_tags = []
    for tag in tag_list:
        if tag.count != len(tag.suggestions):
            incorrect_tag_count.append(tag)
        elif tag.count == 0:
            empty_tags.append(tag)
        oldest = None
        for suggestion in tag.suggestions:
            if suggestion not in suggestion_dict:
                missing_suggestions.append((suggestion, tag))
                continue
            suggestion = suggestion_dict[suggestion]
            if tag.key().name() not in suggestion.tags:
                missing_suggestion_tags.append((suggestion, tag))
            if oldest is None or suggestion.created < oldest.created:
                oldest = suggestion
        if tag.created is None or (
            oldest and tag.created > oldest.created):
            incorrect_tag_created.append((tag, oldest))
    missing_suggestions.sort()
    missing_suggestion_tags.sort(key=lambda pair: pair[0].key().name())
    incorrect_tag_count.sort(key=lambda tag: tag.key().name())
    incorrect_tag_created.sort(key=lambda pair: pair[0].key().name())

    # Fix inconsistencies if admin clicked one of the buttons.
    action_form = ActionForm(request.POST or None)
    if action_form.is_valid():
        if action_form.cleaned_data['create_tags']:
            return create_tags(request, missing_tags)
        if action_form.cleaned_data['delete_tag_suggestions']:
            return delete_tag_suggestions(request, missing_suggestions)
        if action_form.cleaned_data['delete_empty_tags']:
            return delete_empty_tags(request, empty_tags)
        if action_form.cleaned_data['create_tag_suggestions']:
            return create_tag_suggestions(request, missing_tag_suggestions)
        if action_form.cleaned_data['create_suggestion_tags']:
            return create_suggestion_tags(request, missing_suggestion_tags)
        if action_form.cleaned_data['adjust_tag_count']:
            return adjust_tag_count(request, incorrect_tag_count)
        if action_form.cleaned_data['adjust_tag_created']:
            return adjust_tag_created(request, incorrect_tag_created)

    # Show newest suggestions.
    day = datetime.now() - timedelta(hours=24)
    week = datetime.now() - timedelta(days=7)
    suggestion_count = Suggestion.all().count()
    suggestion_count_24h = Suggestion.all().filter('created >', day).count()
    suggestion_count_7d = Suggestion.all().filter('created >', week).count()
    suggestion_list = Suggestion.all().order('-created').fetch(RECENT_LIMIT)

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
    suggestion_slug = suggestion_form.cleaned_data['slug']
    tag_list = suggestion_form.cleaned_data['tags'].split()
    for tag_name in tag_list:
        tag = Tag.get_by_key_name(tag_name)
        if tag is None:
            tag = Tag(key_name=tag_name, count=0)
        tag.suggestions.append(suggestion_slug)
        tag.count += 1
        tag.put()
    suggestion = Suggestion(
        author=request.user,
        key_name=suggestion_slug,
        title=suggestion_form.cleaned_data['title'],
        days=suggestion_form.cleaned_data['days'],
        months=suggestion_form.cleaned_data['months'],
        years=suggestion_form.cleaned_data['years'],
        miles=suggestion_form.cleaned_data['miles'],
        kilometers=suggestion_form.cleaned_data['kilometers'],
        tags=tag_list,
        submitter=request.user)
    logging.debug(suggestion)
    suggestion.put()
    return HttpResponseRedirect(suggestion.get_absolute_url())


def create_tags(request, missing_tags):
    while missing_tags:
        key_name, suggestion = missing_tags.pop(0)
        created = suggestion.created
        suggestion_names = [suggestion.key().name()]
        while missing_tags and missing_tags[0][0] == key_name:
            key_name, suggestion = missing_tags.pop(0)
            suggestion_names.append(suggestion.key().name())
            if suggestion.created < created:
                created = suggestion.created
        tag = Tag(key_name=key_name,
                  count=len(suggestion_names),
                  suggestions=suggestion_names,
                  created=created)
        tag.put()
        logging.debug('created %s', repr(tag))
    return HttpResponseRedirect(request.path)


def delete_tag_suggestions(request, missing_suggestions):
    for suggestion_name, tag in missing_suggestions:
        tag.suggestions.remove(suggestion_name)
        tag.count = len(tag.suggestions)
        save_tag(tag)
    return HttpResponseRedirect(request.path)


def delete_empty_tags(request, empty_tags):
    for tag in empty_tags:
        save_tag(tag)
    return HttpResponseRedirect(request.path)


def create_tag_suggestions(request, missing_tag_suggestions):
    for tag, suggestion in missing_tag_suggestions:
        tag.suggestions.append(suggestion.key().name())
        tag.count = len(tag.suggestions)
        save_tag(tag)
    return HttpResponseRedirect(request.path)


def create_suggestion_tags(request, missing_suggestion_tags):
    for suggestion, tag in missing_suggestion_tags:
        suggestion.tags.append(tag.key().name())
        logging.debug('updating %s', repr(suggestion))
        suggestion.put()
    return HttpResponseRedirect(request.path)


def adjust_tag_count(request, incorrect_tag_count):
    for tag in incorrect_tag_count:
        tag.count = len(tag.suggestions)
        save_tag(tag)
    return HttpResponseRedirect(request.path)


def adjust_tag_created(request, incorrect_tag_created):
    for tag, suggestion in incorrect_tag_created:
        tag.created = suggestion.created
        save_tag(tag)
    return HttpResponseRedirect(request.path)


def save_tag(tag):
    if tag.count:
        logging.debug('updating %s', repr(tag))
        tag.put()
    else:
        logging.debug('deleting %s', repr(tag))
        tag.delete()
