from django.http import HttpResponseRedirect
from ragendja.template import render_to_response


def index(request):
    
    return render_to_response(request, 'tags/index.html', locals())


def detail(request, tag):
    pass
