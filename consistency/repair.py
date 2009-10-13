from django.http import HttpResponseRedirect

from reminders.models import Reminder
from tags.models import Tag


def tag_owner(request, tag):
    tag.owner = request.user
    tag.put()


def tag_suggestion_reverse(request, tag, suggestion):
    suggestion.tags.append(tag.key().name())
    suggestion.put()


def reminder_tag(request, problems):
    for text, reminder, tag in problems:
        reminder.tags.append(tag.key().name())
        reminder.put()


def tag_count(request, tag, count, length):
    tag.count = len(tag.suggestions)
    if tag.count:
        tag.put()
    else:
        tag.delete()


def tag_created_none(request, tag, suggestion):
    tag.created = suggestion.created
    tag.put()


def tag_created_later(request, tag, suggestion):
    tag.created = suggestion.created
    tag.put()


def tag_empty(request, tag):
    tag.delete()


def suggestion_tag_missing(request, suggestion, tag_key):
    tag = Tag.get_by_key_name(tag_key)
    if tag is None:
        tag = Tag(key_name=tag_key, count=0, suggestions=[])
    tag.suggestions.append(suggestion.key().name())
    tag.count = len(tag.suggestions)
    if tag.created is None or suggestion.created < tag.created:
        tag.created = suggestion.created
    tag.put()


def suggestion_tag_reverse(request, suggestion, tag):
    tag.suggestions.append(suggestion.key().name())
    tag.count = len(tag.suggestions)
    tag.put()
