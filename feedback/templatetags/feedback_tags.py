from django import template
from django.template.loader import render_to_string

from feedback.models import Feedback, Vote
from feedback.forms import FeedbackForm
from feedback.views import get_already_voted

register = template.Library()


@register.simple_tag
def feedback_form(request):
    page = request.META['PATH_INFO']
    feedback_form = FeedbackForm(initial={'page': page})
    return render_to_string('feedback/form.html', locals())


@register.simple_tag
def feedback_recently(request):
    page = request.META['PATH_INFO']
    feedback_list = Feedback.all().filter('page', page)
    feedback_list.order('-points').order('-submitted')
    already_voted = get_already_voted(request)
    return render_to_string('feedback/messages.html', locals())


@register.filter
def in_list(value, arg):
   return value in arg


@register.filter
def is_equal(value, arg):
   return value == arg
