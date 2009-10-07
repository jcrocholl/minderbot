from django import forms
from django.http import HttpResponseRedirect

from ragendja.template import render_to_response
from ragendja.auth.decorators import staff_only

from suggestions.models import Suggestion


class SuggestionForm(forms.Form):
    """
    URL input form.
    """
    title = forms.CharField(max_length=120, label="Title",
        widget=forms.TextInput(attrs={'class': 'text span-10'}))
    slug = forms.CharField(max_length=120, label="Slug",
        widget=forms.TextInput(attrs={'class': 'text span-10'}))
    tags = forms.CharField(max_length=120, label="Tags",
        widget=forms.TextInput(attrs={'class': 'text span-10'}))


@staff_only
def index(request):
    suggestion_count = Suggestion.all().count()
    suggestion_list = Suggestion.all().order('-created').fetch(10)
    suggestion_form = SuggestionForm(request.POST or None)
    if suggestion_form.is_valid():
        suggestion = Suggestion(
            key_name=suggestion_form.cleaned_data['slug'],
            title=suggestion_form.cleaned_data['title'],
            submitter=request.user)
        suggestion.put()
        return HttpResponseRedirect(suggestion.get_absolute_url())
    return render_to_response(request, 'dashboard/index.html', locals())
