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
    'reminder_owner': [
        "Claim ownership",
        "Some reminder have missing owners.",
        "All reminders have valid owners."],
    'reminder_missing': [
        "Delete dangling tag references",
        "Some reminders are missing.",
        "All referenced reminders exist."],
    'reminder_tag': [
        "Create missing references",
        "Some tag-reminder references don't have a reverse.",
        "All tag-reminder references have a reverse."],
    'tag_count': [
        "Adjust count fields",
        "Some tag count fields are incorrect.",
        "All tag count fields are correct."],
    'tag_created': [
        "Adjust timestamps",
        "Some tag timestamps are missing or too late.",
        "All tag timestamps are reasonable."],
    'tag_empty': [
        "Delete empty tags",
        "Some tags don't reference any reminders.",
        "All tags reference at least one reminder."],
    'tag_missing': [
        "Create missing tags",
        "Some referenced tags don't exist.",
        "All referenced tags exist."],
    'tag_reminder': [
        "Create missing references",
        "Some reminder-tag references don't have a reverse.",
        "All reminder-tag references have a reverse."],
    }


def index(request):
    """
    Check reminders and tags for consistency.
    """
    if (request.META.get('HTTP_X_APPENGINE_CRON', '') != 'true'
        and not request.user.is_staff):
        return HttpResponseRedirect('/accounts/login/?next=/consistency/')

    # Get all reminders.
    reminder_list = Reminder.all().fetch(1000) # TODO: fetch unlimited
    reminder_dict = {}
    for reminder in reminder_list:
        reminder_dict[reminder.key().name()] = reminder

    # Get all tags.
    tag_list = Tag.all().fetch(1000) # TODO: fetch unlimited
    tag_dict = {}
    for tag in tag_list:
        tag_dict[tag.key().name()] = tag

    # Prepare list of problems.
    problems = {}
    for problem in PROBLEM_MESSAGES:
        problems[problem] = []

    # Check for missing tags or missing references to reminders.
    for reminder in reminder_list:
        try:
            owner = reminder.owner # Use automatic dereferencing.
        except datastore_errors.Error:
            problems['reminder_owner'].append(
                ("Owner of %s does not exist.", reminder))
        for tag in reminder.tags:
            if tag not in tag_dict:
                problems['tag_missing'].append(
                    ("Tag %s is referenced by %s but does not exist.",
                     tag, reminder))
                continue
            tag = tag_dict[tag]
            if reminder.key().name() not in tag.reminders:
                problems['tag_reminder'].append(
                    ("Tag %s does not reverse reference %s.",
                     tag, reminder))

    # Check for missing reminders or missing references to tags.
    for tag in tag_list:
        if tag.count != len(tag.reminders):
            problems['tag_count'].append(
                ("Tag %s has count %d but references %d reminders.",
                 tag, tag.count, len(tag.reminders)))
        elif tag.count == 0:
            problems['tag_empty'].append(
                ("Tag %s does not reference any reminders.", tag))
        oldest = None
        for reminder in tag.reminders:
            if reminder not in reminder_dict:
                problems['reminder_missing'].append(
                    ("Reminder %s is referenced by %s but does not exist.",
                     reminder, tag))
                continue
            reminder = reminder_dict[reminder]
            if tag.key().name() not in reminder.tags:
                problems['reminder_tag'].append(
                    ("Reminder %s does not reverse reference %s.",
                     reminder, tag))
            if oldest is None or reminder.created < oldest.created:
                oldest = reminder
        if tag.created is None:
            problems['tag_created'].append(
                ("Timestamp of tag %s is not set.", tag, oldest))
        elif oldest and tag.created > oldest.created:
            problems['tag_created'].append(
                ("Timestamp of tag %s is younger than %s.", tag, oldest))

    # Collect errors and remove sections without problems.
    consistency_results = []
    for problem in PROBLEM_MESSAGES:
        headline = PROBLEM_MESSAGES[problem][1]
        headline_class = 'error'
        items = problems[problem]
        if not items:
            assert problems.pop(problem) == []
            headline = PROBLEM_MESSAGES[problem][2]
            headline_class = 'success'
        button = PROBLEM_MESSAGES[problem][0]
        consistency_results.append(
            (problem, headline_class, headline, button,
             [format_problem(item) for item in items]))
        consistency_results.sort()

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

    # Fix inconsistencies if admin clicked one of the buttons.
    if request.user.is_staff:
        for problem in problems:
            if problem in request.POST:
                func = getattr(repair, problem)
                assert callable(func)
                return func(request, problems[problem])

    # Show results of consistency checks.
    return render_to_response(request, 'consistency/index.html', locals())


def format_problem(problem):
    problem = list(problem)
    for index in range(1, len(problem)):
        try:
            problem[index] = problem[index].key().name()
        except AttributeError:
            pass
    message = problem.pop(0)
    arguments = tuple(problem[:message.count('%')])
    return message % arguments
