import logging
from datetime import datetime, timedelta

from google.appengine.api import datastore_errors

from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import mail_admins
from django.contrib.auth.models import User

from ragendja.template import render_to_response

from suggestions.models import Suggestion
from tags.models import Tag
from feedback.models import Feedback

from consistency import repair


PROBLEM_MESSAGES = {
    'suggestion_author': [
        "Claim authorship",
        "Some suggestion have missing authors.",
        "All suggestions have valid authors."],
    'suggestion_missing': [
        "Delete dangling tag references",
        "Some suggestions are missing.",
        "All referenced suggestions exist."],
    'suggestion_tag': [
        "Create missing references",
        "Some tag-suggestion references don't have a reverse.",
        "All tag-suggestion references have a reverse."],
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
        "Some tags don't reference any suggestions.",
        "All tags reference at least one suggestion."],
    'tag_missing': [
        "Create missing tags",
        "Some referenced tags don't exist.",
        "All referenced tags exist."],
    'tag_suggestion': [
        "Create missing references",
        "Some suggestion-tag references don't have a reverse.",
        "All suggestion-tag references have a reverse."],
    }


def index(request):
    """
    Check suggestions and tags for consistency.
    """
    if (request.META.get('HTTP_X_APPENGINE_CRON', '') != 'true'
        and not request.user.is_staff):
        return HttpResponseRedirect('/accounts/login/?next=/consistency/')

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

    # Prepare list of problems.
    problems = {}
    for problem in PROBLEM_MESSAGES:
        problems[problem] = []

    # Check for missing tags or missing references to suggestions.
    for suggestion in suggestion_list:
        try:
            if suggestion.author is None:
                problems['suggestion_author'].append(
                    ("Author of %s is None.", suggestion))
        except datastore_errors.Error:
            problems['suggestion_author'].append(
                ("Author of %s could not be found.", suggestion))
        for tag in suggestion.tags:
            if tag not in tag_dict:
                problems['tag_missing'].append(
                    ("Tag %s is referenced by %s but does not exist.",
                     tag, suggestion))
                continue
            tag = tag_dict[tag]
            if suggestion.key().name() not in tag.suggestions:
                problems['tag_suggestion'].append(
                    ("Tag %s does not reverse reference %s.",
                     tag, suggestion))

    # Check for missing suggestions or missing references to tags.
    for tag in tag_list:
        if tag.count != len(tag.suggestions):
            problems['tag_count'].append(
                ("Tag %s has count %d but references %d suggestions.",
                 tag, tag.count, len(tag.suggestions)))
        elif tag.count == 0:
            problems['tag_empty'].append(
                ("Tag %s does not reference any suggestions.", tag))
        oldest = None
        for suggestion in tag.suggestions:
            if suggestion not in suggestion_dict:
                problems['suggestion_missing'].append(
                    ("Suggestion %s is referenced by %s but does not exist.",
                     suggestion, tag))
                continue
            suggestion = suggestion_dict[suggestion]
            if tag.key().name() not in suggestion.tags:
                problems['suggestion_tag'].append(
                    ("Suggestion %s does not reverse reference %s.",
                     suggestion, tag))
            if oldest is None or suggestion.created < oldest.created:
                oldest = suggestion
        if tag.created is None or (
            oldest and tag.created > oldest.created):
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

    if problems and request.META.get('HTTP_X_APPENGINE_CRON', '') == 'true':
        message = []
        for name in problems:
            message.append(PROBLEM_MESSAGES[name][1].rstrip('.') + ':')
            for problem in problems[name]:
                message.append("* " + format_problem(problem))
            message.append('')
        message.append('http://minderbot.appspot.com/consistency/')
        message = '\n'.join(message)
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
    logging.info(problem[0])
    logging.info(problem[1:])
    return problem[0] % tuple(problem[1:])
