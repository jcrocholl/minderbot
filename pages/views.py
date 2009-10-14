from django import forms
from django.http import HttpResponseRedirect, Http404
from django.template import TemplateDoesNotExist
from django.template.loader import get_template

from ragendja.template import render_to_response


def page(request, page_name):
    template_name = 'pages/%s.html' % page_name
    try:
        get_template(template_name)
    except TemplateDoesNotExist:
        raise Http404
    return render_to_response(request, template_name, locals())
