from django.http import HttpResponseRedirect

from tags.models import Tag


def feedback_submitter(feedback, request_user):
    feedback.submitter = None
    feedback.put()


def reminder_owner(reminder, request_user):
    reminder.owner = request_user
    reminder.put()


def tag_suggestion_reverse(tag, suggestion):
    suggestion.tags.append(tag.key().name())
    suggestion.put()


def tag_suggestion_missing(tag, suggestion_key):
    tag.suggestions.remove(suggestion_key)
    tag.count = len(tag.suggestions)
    if tag.count:
        tag.put()
    else:
        tag.delete()


def tag_suggestion_duplicate(tag, count, suggestion_key):
    while tag.suggestions.count(suggestion_key) > 1:
        tag.suggestions.remove(suggestion_key)
    tag.count = len(tag.suggestions)
    tag.put()


def reminder_tag(problems):
    for text, reminder, tag in problems:
        reminder.tags.append(tag.key().name())
        reminder.put()


def tag_count(tag, count, length):
    tag.count = len(tag.suggestions)
    if tag.count:
        tag.put()
    else:
        tag.delete()


def tag_created_none(tag, suggestion):
    tag.created = suggestion.created
    tag.put()


def tag_created_later(tag, suggestion):
    tag.created = suggestion.created
    tag.put()


def tag_empty(tag):
    tag.delete()


def suggestion_tag_missing(suggestion, tag_key):
    tag = Tag.get_by_key_name(tag_key)
    if tag is None:
        tag = Tag(key_name=tag_key, count=0, suggestions=[])
    tag.suggestions.append(suggestion.key().name())
    tag.count = len(tag.suggestions)
    if tag.created is None or suggestion.created < tag.created:
        tag.created = suggestion.created
    tag.put()


def suggestion_tag_reverse(suggestion, tag):
    if suggestion.key().name() is None:
        return
    tag.suggestions.append(suggestion.key().name())
    tag.count = len(tag.suggestions)
    tag.put()
