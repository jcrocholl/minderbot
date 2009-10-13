from django.http import HttpResponseRedirect

from reminders.models import Reminder
from tags.models import Tag


def tag_owner(request, tag):
    tag.owner = request.user
    tag.put()


def suggestion(request, problems):
    for text, reminder_name, tag in problems:
        tag.reminders.remove(reminder_name)
        tag.count = len(tag.reminders)
        save_tag(tag)


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


def tag_missing(request, problems):
    problems.sort(key=lambda triple: triple[1])
    while problems:
        text, tag_name, reminder = problems.pop(0)
        created = reminder.created
        reminder_names = [reminder.key().name()]
        while problems and problems[0][1] == tag_name:
            text, tag_name, reminder = problems.pop(0)
            reminder_names.append(reminder.key().name())
            if reminder.created < created:
                created = reminder.created
        tag = Tag(key_name=tag_name,
                  count=len(reminder_names),
                  reminders=reminder_names,
                  created=created)
        tag.put()


def tag_reminder(request, problems):
    for text, tag, reminder in problems:
        tag.reminders.append(reminder.key().name())
        tag.count = len(tag.reminders)
        save_tag(tag)
