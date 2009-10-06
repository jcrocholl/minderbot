import uuid

from django import forms
from django.http import HttpResponseRedirect
from ragendja.template import render_to_response


class URLForm(forms.Form):
    """
    URL input form.
    """
    url = forms.URLField(max_length=400,
        label="Enter your URL here:",
        widget=forms.TextInput(attrs={'class': 'text span-17'}))


def index(request):
    url_form = URLForm(request.POST or None)
    if url_form.is_valid():
        # source = Source(
        #    key_name=uuid.uuid4().hex,
        #    audio_url=url_form.cleaned_data['url'],
        #    submitter=request.user)
        # source.put()
        return HttpResponseRedirect(source.get_absolute_url())
    return render_to_response(request, 'welcome/index.html', locals())
