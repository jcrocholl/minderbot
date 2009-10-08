from ragendja.template import render_to_response

from suggestions.models import Suggestion
from tags.models import Tag


def dump_app(request, app_name, format):
    if app_name == 'suggestions':
        suggestion_list = Suggestion.all()
    elif app_name == 'tags':
        tag_list = Tag.all()
    template = 'dumpdata/%s.%s' % (app_name, format)
    return render_to_response(request, template, locals())


