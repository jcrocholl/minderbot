from django.http import HttpResponseRedirect

from reminders.models import Reminder
from tags.models import Tag


def save_tag(tag):
    if tag.count:
        tag.put()
    else:
        tag.delete()


def reminder_owner(request, problems):
    for text, reminder in problems:
        reminder.owner = request.user
        reminder.put()
    return HttpResponseRedirect(request.path)


def reminder_missing(request, problems):
    for text, reminder_name, tag in problems:
        tag.reminders.remove(reminder_name)
        tag.count = len(tag.reminders)
        save_tag(tag)
    return HttpResponseRedirect(request.path)


def reminder_tag(request, problems):
    for text, reminder, tag in problems:
        reminder.tags.append(tag.key().name())
        reminder.put()
    return HttpResponseRedirect(request.path)


def tag_count(request, problems):
    for text, tag, count, length in problems:
        tag.count = len(tag.reminders)
        save_tag(tag)
    return HttpResponseRedirect(request.path)


def tag_created(request, problems):
    for text, tag, reminder in problems:
        tag.created = reminder.created
        save_tag(tag)
    return HttpResponseRedirect(request.path)


def tag_empty(request, problems):
    for text, tag in problems:
        save_tag(tag)
    return HttpResponseRedirect(request.path)


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
    return HttpResponseRedirect(request.path)


def tag_reminder(request, problems):
    for text, tag, reminder in problems:
        tag.reminders.append(reminder.key().name())
        tag.count = len(tag.reminders)
        save_tag(tag)
    return HttpResponseRedirect(request.path)
