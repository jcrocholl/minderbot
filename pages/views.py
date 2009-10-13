import uuid

from django import forms
from django.http import HttpResponseRedirect
from ragendja.template import render_to_response


def page(request, page_name):
    template_name = 'pages/%s.html' % page_name
    return render_to_response(request, template_name, locals())
