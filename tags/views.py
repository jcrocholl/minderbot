from django.http import HttpResponseRedirect

from ragendja.template import render_to_response
from ragendja.dbutils import get_object_or_404

from tags.models import Tag


def index(request):
    tag_list = list(Tag.all().order('-count').fetch(100))
    tag_list.sort(key=lambda tag: tag.key().name())
    return render_to_response(request, 'tags/index.html', locals())


def detail(request, key_name):
    tag = get_object_or_404(Tag, key_name=key_name)
    suggestion_list = tag.get_suggestions()
    return render_to_response(request, 'tags/detail.html', locals())
