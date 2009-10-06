from django import forms
from django.contrib.auth.models import User

from ragendja.auth.models import UserTraits
from ragendja.forms import FormWithSets, FormSetField

from registration.forms import RegistrationForm, RegistrationFormUniqueEmail
from registration.models import RegistrationProfile


class UserRegistrationForm(forms.ModelForm):
    username = forms.RegexField(regex=r'^\w+$', max_length=30,
        widget=forms.TextInput(attrs={'maxlength': '30', 'class': 'text'}),
        label='Username')
    first_name = forms.CharField(required=False,
        widget=forms.TextInput(attrs={'class': 'text'}),
        label='First name')
    last_name = forms.CharField(required=False,
        widget=forms.TextInput(attrs={'class': 'text'}),
        label='Last name')
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'maxlength': '75', 'class': 'text'}),
        label='Email address')
    password1 = forms.CharField(
        widget=forms.PasswordInput(render_value=False,
                                   attrs={'class': 'text'}),
        label='Password')
    password2 = forms.CharField(
        widget=forms.PasswordInput(render_value=False,
                                   attrs={'class': 'text'}),
        label='Password (again)')


    class Meta:
        model = User
        exclude = UserTraits.properties().keys()


    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.
        """
        user = User.get_by_key_name(
            "key_" + self.cleaned_data['username'].lower())
        if user and user.is_active:
            raise forms.ValidationError(
                "This username is already taken. Please choose another.")
        return self.cleaned_data['username']


    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.
        """
        email = self.cleaned_data['email'].lower()
        users = User.all().filter('email', email).filter('is_active', True)
        if users.count(1):
            raise forms.ValidationError(' '.join("""
                This email address is already in use.
                Please use a different email address.
                """.split()))
        return email


    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
        """
        if ('password1' in self.cleaned_data and
            'password2' in self.cleaned_data):
            if (self.cleaned_data['password1'] !=
                self.cleaned_data['password2']):
                raise forms.ValidationError(
                    "You must type the same password each time.")
        return self.cleaned_data


    def save(self, domain_override=""):
        """
        Create the new ``User`` and ``RegistrationProfile``, and
        returns the ``User``.

        This is essentially a light wrapper around
        ``RegistrationProfile.objects.create_inactive_user()``,
        feeding it the form data and a profile callback (see the
        documentation on ``create_inactive_user()`` for details) if
        supplied.
        """
        new_user = RegistrationProfile.objects.create_inactive_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password1'],
            email=self.cleaned_data['email'],
            domain_override=domain_override)
        self.instance = new_user
        return super(UserRegistrationForm, self).save()
