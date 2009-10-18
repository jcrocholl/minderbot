import logging

from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Message

from ragendja.template import render_to_response
from ragendja.dbutils import get_object_or_404

from utils.english_passwords import generate_password
from reminders.models import Reminder


class EmailForm(forms.Form):
    email = forms.EmailField(max_length=200,
        widget=forms.TextInput(attrs={'class': 'text span-6 focus'}))


def detail(request, key_name):
    """
    Show details for a public suggestion, and a button to create a
    reminder from it.
    """
    suggestion = get_object_or_404(Reminder, key_name=key_name)
    logging.debug(request.method)
    email_form = EmailForm(request.POST)
    if request.method == "POST":
        user = request.user
        if user.is_anonymous() and email_form.is_valid():
            email = email_form.cleaned_data['email']
            existing = User.all().filter('email', email).fetch(1)
            if len(existing):
                return HttpResponseRedirect(
                    '/accounts/login/?email=%s&next=%s' %
                    (email, request.path))
            user = create_user(request, email)
        return create_reminder(request, user, suggestion)
    return render_to_response(
        request, 'suggestions/detail.html', locals())


def create_reminder(request, user, suggestion):
    reminder = Reminder(
        owner=user,
        title=suggestion.title,
        tags=suggestion.tags,
        days=suggestion.days,
        months=suggestion.months,
        years=suggestion.years,
        miles=suggestion.miles,
        kilometers=suggestion.kilometers)
    reminder.put()
    Message(message='<p class="success message">%s</p>' %
            "Your reminder was created successfully. You can edit it below.",
            user=user).put()
    return HttpResponseRedirect(reminder.get_absolute_url())


def create_user(request, email):
    password = generate_password(digits=1)
    User.objects.create_user(email, email, password)
    user = authenticate(username=email, password=password)
    assert user
    login(request, user)
    assert user.is_authenticated()
    send_mail("Welcome to Minderbot", """\
We have created a user account on www.minderbot.com for you.
If you have not requested reminders for this email address,
you can ignore this message.

Your username is your email address: %(email)s
You can login with this password: %(password)s

Thank you for using Minderbot!
""" % locals(), settings.DEFAULT_FROM_EMAIL, [email],
fail_silently=True)
    return user
