# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib import auth

from ragendja.template import render_to_response


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'class': 'text span-6 focus'}))
    password = forms.CharField(max_length=40,
        widget=forms.PasswordInput(attrs={'class': 'text span-6'}))
    next = forms.CharField(required=False)

    def clean(self):
        email = self.cleaned_data.get('email', '')
        password = self.cleaned_data.get('password', '')
        if not (email and password):
            return self.cleaned_data # Enough errors already.
        user = auth.authenticate(username=email, password=password)
        if user is None:
            raise forms.ValidationError("Incorrect email or password.")
        if not user.is_active:
            raise forms.ValidationError("Your user account is inactive.")
        self.cleaned_data['user'] = user
        return self.cleaned_data


def login(request):
    login_form = LoginForm(request.POST or None)
    if login_form.is_valid():
        user = login_form.cleaned_data['user']
        auth.login(request, user)
        next = login_form.cleaned_data['next']
        if not next:
            next = settings.LOGIN_REDIRECT_URL
        return HttpResponseRedirect(next)
    if login_form.errors.get('__all__', False):
        login_error = login_form.errors['__all__'][0]
    return render_to_response(request, 'accounts/login.html', locals())


def logout(request):
    auth.logout(request)
    return render_to_response(request, 'accounts/logout.html', locals())
