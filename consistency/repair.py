import logging

from django.http import HttpResponseRedirect

from suggestions.models import Suggestion
from tags.models import Tag


def save_tag(tag):
    if tag.count:
        logging.debug('updating %s', repr(tag))
        tag.put()
    else:
        logging.debug('deleting %s', repr(tag))
        tag.delete()


def suggestion_author(request, problems):
    for text, suggestion in problems:
        suggestion.author = request.user
        logging.debug('updating %s', repr(suggestion))
        suggestion.put()
    return HttpResponseRedirect(request.path)


def suggestion_missing(request, problems):
    for text, suggestion_name, tag in problems:
        tag.suggestions.remove(suggestion_name)
        tag.count = len(tag.suggestions)
        save_tag(tag)
    return HttpResponseRedirect(request.path)


def suggestion_tag(request, problems):
    for text, suggestion, tag in problems:
        suggestion.tags.append(tag.key().name())
        logging.debug('updating %s', repr(suggestion))
        suggestion.put()
    return HttpResponseRedirect(request.path)


def tag_count(request, problems):
    for text, tag, count, length in problems:
        tag.count = len(tag.suggestions)
        save_tag(tag)
    return HttpResponseRedirect(request.path)


def tag_created(request, problems):
    for text, tag, suggestion in problems:
        tag.created = suggestion.created
        save_tag(tag)
    return HttpResponseRedirect(request.path)


def tag_empty(request, problems):
    for text, tag in problems:
        save_tag(tag)
    return HttpResponseRedirect(request.path)


def tag_missing(request, problems):
    problems.sort(key=lambda triple: triple[1])
    while problems:
        text, tag_name, suggestion = problems.pop(0)
        created = suggestion.created
        suggestion_names = [suggestion.key().name()]
        while problems and problems[0][1] == tag_name:
            text, tag_name, suggestion = problems.pop(0)
            suggestion_names.append(suggestion.key().name())
            if suggestion.created < created:
                created = suggestion.created
        tag = Tag(key_name=tag_name,
                  count=len(suggestion_names),
                  suggestions=suggestion_names,
                  created=created)
        tag.put()
        logging.debug('created %s', repr(tag))
    return HttpResponseRedirect(request.path)


def tag_suggestion(request, problems):
    for text, tag, suggestion in problems:
        tag.suggestions.append(suggestion.key().name())
        tag.count = len(tag.suggestions)
        save_tag(tag)
    return HttpResponseRedirect(request.path)
