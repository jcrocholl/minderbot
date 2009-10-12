from datetime import datetime, timedelta

from django.test import TestCase
from django.contrib.auth.models import User

from tags.models import Tag
from suggestions.models import Suggestion
from reminders.models import Reminder


class AnonymousTest(TestCase):

    def test_anonymous(self):
        response = self.client.get('/reminders/')
        self.assertRedirects(response, '/accounts/login/?next=/reminders/')


class ReminderTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('user', 'a@b.com', 'pass')
        self.suggestion = Suggestion(
            user=self.user,
            title="Replace smoke alarm batteries",
            tags='home safety smoke fire alarm batteries'.split(),
            days=7)
        self.suggestion.put()

    def test_reminder(self):
        reminder = Reminder(
            suggestion=self.suggestion,
            title="Replace smoke alarm batteries in the basement",
            next=datetime(2008, 10, 10, 10, 10, 10))
        self.assertEqual(unicode(reminder),
                         "Replace smoke alarm batteries in the basement")
