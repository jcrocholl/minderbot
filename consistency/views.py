import logging
from datetime import datetime, timedelta

from google.appengine.api import datastore_errors

from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import mail_admins
from django.contrib.auth.models import User

from ragendja.template import render_to_response

from reminders.models import Reminder
from tags.models import Tag
from feedback.models import Feedback

from consistency import repair

PROBLEM_MESSAGES = {
    'tag_count': "Tag %s has count %d but references %d suggestions.",
    'tag_empty': "Tag %s does not reference any suggestions.",
    'tag_created_none': "Tag %s is missing a timestamp.",
    'tag_created_later': "Tag %s was created after suggestion %s.",
    'tag_suggestion_missing': "Tag %s references missing suggestion %s.",
    'tag_suggestion_reverse': "Tag %s references %s but not reverse.",

    'suggestion_tag_missing': "Suggestion %s references missing tag %s.",
    'suggestion_tag_reverse': "Suggestion %s references %s but not reverse.",
    }


def index(request):
    """
    Check reminders and tags for consistency.
    """
    if (request.META.get('HTTP_X_APPENGINE_CRON', '') != 'true'
        and not request.user.is_staff):
        return HttpResponseRedirect('/accounts/login/?next=/consistency/')

    # Get all tags and suggestions from the datastore.
    tag_dict = dict((tag.key().name(), tag) for tag in Tag.all())
    suggestion_dict = dict((suggestion.key().name(), suggestion)
        for suggestion in Reminder.all().filter('owner', None))

    # Initialize empty problems dict.
    problems = dict((problem, []) for problem in PROBLEM_MESSAGES)

    # Check all tags.
    for tag_key, tag in tag_dict.items():
        if tag.count != len(tag.suggestions):
            problems['tag_count'].append(
                (tag, tag.count, len(tag.suggestions)))
        elif tag.count == 0:
            problems['tag_empty'].append((tag, ))
        oldest = None
        for suggestion_key in tag.suggestions:
            if suggestion_key not in suggestion_dict:
                problems['tag_suggestion_missing'].append(
                    (tag, suggestion_key))
                continue
            suggestion = suggestion_dict[suggestion_key]
            if tag.key().name() not in suggestion.tags:
                problems['tag_suggestion_reverse'].append((tag, suggestion))
            if oldest is None or suggestion.created < oldest.created:
                oldest = suggestion
        if oldest:
            if tag.created is None:
                problems['tag_created_none'].append((tag, oldest))
            elif tag.created > oldest.created:
                problems['tag_created_later'].append((tag, oldest))

    # Check all suggestions.
    for suggestion_key, suggestion in suggestion_dict.items():
        for tag_key in suggestion.tags:
            if tag_key not in tag_dict:
                problems['suggestion_tag_missing'].append(
                    (suggestion, tag_key))
                continue
            tag = tag_dict[tag_key]
            if suggestion.key().name() not in tag.suggestions:
                problems['suggestion_tag_reverse'].append((suggestion, tag))

    # Fix inconsistencies if admin clicked one of the buttons.
    if request.user.is_staff:
        for problem in problems:
            if problems[problem] and problem in request.POST:
                func = getattr(repair, problem)
                assert callable(func)
                for item in problems[problem]:
                    func(request, *item)
                return HttpResponseRedirect(request.path)

    # Collect errors and remove sections without problems.
    consistency_results = []
    for problem in PROBLEM_MESSAGES:
        if not problems[problem]:
            assert problems.pop(problem) == []
            continue
        consistency_results.append((problem,
             [format_problem(problem, item) for item in problems[problem]]))
    consistency_results.sort()
    return render_to_response(request, 'consistency/index.html', locals())


def format_problem(problem, data):
    message = PROBLEM_MESSAGES[problem]
    count = message.count('%')
    data = list(data)
    for index in range(count):
        if hasattr(data[index], 'key'):
            data[index] = data[index].key().name()
    return message % tuple(data[:count])


def obsolete():
    # Check reminders.
    for reminder in Reminder.all():
        try:
            owner = suggestion.owner # Attempt to dereference.
        except datastore_errors.Error:
            problems['reminder_owner'].append(
                ("Owner of %s does not exist.", suggestion))


    if request.META.get('HTTP_X_APPENGINE_CRON', '') == 'true':
        message = []
        for name in problems:
            message.append(PROBLEM_MESSAGES[name][1].rstrip('.') + ':')
            for problem in problems[name]:
                message.append("* " + format_problem(problem))
            message.append('')
        message.append('http://minderbot.appspot.com/consistency/')
        message = '\n'.join(message)
        if problems:
            logging.error(message)
            mail_admins('Consistency check found problems',
                        message, fail_silently=True)
        return HttpResponse(message, mimetype="text/plain")

