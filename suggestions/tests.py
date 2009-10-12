from datetime import datetime, timedelta

from django.test import TestCase
from django.contrib.auth.models import User

from tags.models import Tag
from suggestions.models import Suggestion
from reminders.models import Reminder


class ClientTest(TestCase):

    def test_index(self):
        response = self.client.get('/suggestions/')
        self.assertEqual(response.status_code, 200)


class SuggestionTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('user', 'a@b.com', 'pass')

    def test_suggestion(self):
        suggestion = Suggestion(
            user=self.user,
            title="Replace smoke alarm batteries",
            tags='home safety smoke fire alarm batteries'.split(),
            days=7)
        suggestion.put()
        self.assertEqual(unicode(suggestion),
                         "Replace smoke alarm batteries")
        self.assertTrue('home' in suggestion.tags)
        self.assertTrue('safety' in suggestion.tags)
        self.assertEqual(len(suggestion.tags), 6)
        self.assertEqual(suggestion.interval(), 'week')
