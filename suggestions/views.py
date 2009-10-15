from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from ragendja.template import render_to_response
from ragendja.dbutils import get_object_or_404

from utils.passwords import generate_password
from reminders.models import Reminder


class ReminderForm(forms.ModelForm):
    title = forms.CharField(max_length=100,
        widget=forms.TextInput(attrs={'class': 'h1 text span-17'}))
    tags = forms.CharField(max_length=200,
        widget=forms.TextInput(attrs={'class': 'text span-10'}))
    days = forms.IntegerField(required=False,
        widget=forms.TextInput(attrs={'class': 'text span-1'}))
    months = forms.IntegerField(required=False,
        widget=forms.TextInput(attrs={'class': 'text span-1'}))
    years = forms.IntegerField(required=False,
        widget=forms.TextInput(attrs={'class': 'text span-1'}))
    miles = forms.IntegerField(required=False,
        widget=forms.TextInput(attrs={'class': 'text span-2'}))
    kilometers = forms.IntegerField(required=False,
        widget=forms.TextInput(attrs={'class': 'text span-2'}))
    email = forms.EmailField(max_length=200,
        widget=forms.TextInput(attrs={'class': 'text span-6'}))

    class Meta:
        model = Reminder
        exclude = 'owner previous next created'.split()


def detail(request, object_id):
    """
    List all reminders for a registered user.
    """
    suggestion = get_object_or_404(Reminder, key_name=object_id)
    reminder_form = ReminderForm(request.POST or None, instance=suggestion)
    if reminder_form.is_valid():
        email = reminder_form.cleaned_data['email']
        existing = User.all().filter('email', email).fetch(1)
        if len(existing):
            return HttpResponseRedirect(
                '/accounts/login/?email=%s&next=%s' %
                (email, request.path))
        create_reminder(request, reminder_form)
    return render_to_response(
        request, 'suggestions/detail.html', locals())


def create_reminder(request, reminder_form):
    user = request.user
    if user.is_anonymous:
        user = create_user(request, reminder_form.cleaned_data['email'])
    reminder = reminder_form.save(commit=False)
    reminder.owner = user
    reminder.tags = reminder_form.cleaned_data['tags'].split()
    reminder.put()


def create_user(request, email):
    password = generate_password(digits=1)
    send_mail("Welcome to Minderbot", """\
We have created a user account on www.minderbot.com for you.
If you have not requested reminders for this email address,
you can ignore this message.

Your username is your email address: %(email)s
You can login with this password: %(password)s

Thank you for using Minderbot!
""" % locals(), settings.DEFAULT_FROM_EMAIL, [email],
fail_silently=True)
    User.objects.create_user(email, email, password)
    user = authenticate(username=email, password=password)
    assert user
    login(request, user)
    return user
