from datetime import datetime, timedelta

from django.test import TestCase
from django.contrib.auth.models import User

from tags.models import Tag
from reminders.models import Reminder


class AnonymousTest(TestCase):

    def test_anonymous(self):
        response = self.client.get('/reminders/')
        self.assertRedirects(response, '/accounts/login/?next=/reminders/')


class ReminderTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('user', 'a@b.com', 'pass')

    def test_reminder(self):
        reminder = Reminder(
            title="Replace smoke alarm batteries", year=1,
            tags='home safety fire smoke alarm batteries'.split(),
            next=datetime(2008, 10, 10, 10, 10, 10),
            owner=self.user)
        reminder.put()
        self.assertEqual(unicode(reminder), "Replace smoke alarm batteries")


class IntervalTest(TestCase):

    def interval_test(self):
        # Singular.
        self.assertEqual(Reminder(days=1).interval(), 'day')
        self.assertEqual(Reminder(weeks=1).interval(), 'week')
        self.assertEqual(Reminder(days=7).interval(), 'week')
        self.assertEqual(Reminder(months=1).interval(), 'month')
        self.assertEqual(Reminder(years=1).interval(), 'year')
        self.assertEqual(Reminder(miles=1).interval(), 'mile')
        self.assertEqual(Reminder(kilometers=1).interval(), 'kilometer')
        # Plural.
        self.assertEqual(Reminder(days=2).interval(), '2 days')
        self.assertEqual(Reminder(weeks=2).interval(), '2 weeks')
        self.assertEqual(Reminder(days=14).interval(), '2 weeks')
        self.assertEqual(Reminder(months=2).interval(), '2 months')
        self.assertEqual(Reminder(years=2).interval(), '2 years')
        self.assertEqual(Reminder(miles=2).interval(), '2 miles')
        self.assertEqual(Reminder(kilometers=2).interval(), '2 kilometers')
        # Alternatives.
        self.assertEqual(Reminder(days=7, month=1).interval(),
                         'week or month')
        self.assertEqual(Reminder(miles=1000, kilometers=1600).interval(),
                         '100 miles or 160 kilometers')
