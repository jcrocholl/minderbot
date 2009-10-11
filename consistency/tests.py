from django.test import TestCase
from django.contrib.auth.models import User

from suggestions.models import Suggestion
from tags.models import Tag


class AnonymousTest(TestCase):

    def test_anonymous(self):
        response = self.client.get('/consistency/')
        self.assertRedirects(response, '/accounts/login/?next=/consistency/')


class NotAdminTest(TestCase):

    def setUp(self):
        admin = User.objects.create_user('admin', 'a@b.com', 'password')
        self.assertFalse(admin.is_staff)
        self.assertTrue(
            self.client.login(username='a@b.com', password='password'))

    def test_index(self):
        response = self.client.get('/consistency/')
        self.assertRedirects(response, '/accounts/login/?next=/consistency/')


class CronTest(TestCase):

    def test_index(self):
        response = self.client.get('/consistency/',
                                   HTTP_X_APPENGINE_CRON='true')
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue(response.content, 'http://')
        self.assertTrue(response.content, '/consistency/')


class AdminTest(TestCase):

    def setUp(self):
        admin = User.objects.create_user('admin', 'a@b.com', 'password')
        admin.is_staff = True
        admin.save()
        self.assertTrue(
            self.client.login(username='a@b.com', password='password'))

    def test_tag_missing(self):
        self.assertEqual(Suggestion.all().count(), 0)
        self.assertEqual(Tag.all().count(), 0)
        # Check that this problem doesn't already exist.
        response = self.client.get('/consistency/')
        self.assertFalse('tag_missing' in response.context['problems'])
        # Create a suggestion but not the tags.
        Suggestion(key_name='a-b', title='a b', tags='a b'.split()).put()
        # Check that the tags are missing.
        response = self.client.get('/consistency/')
        self.assertTrue('tag_missing' in response.context['problems'])
        self.assertTrue("Tag a is referenced by a-b but does not exist."
                        in response.content)
        self.assertTrue("Tag b is referenced by a-b but does not exist."
                        in response.content)
        # Simulate button click to create the missing tags.
        response = self.client.post('/consistency/',
                                    {'tag_missing': "Create missing tags"})
        self.assertRedirects(response, '/consistency/')
        # Check that the tags are now existing.
        response = self.client.get('/consistency/')
        self.assertFalse('tag_missing' in response.context['problems'])
        self.assertTrue("All referenced tags exist." in response.content)

    def test_suggestion_author(self):
        self.assertEqual(Suggestion.all().count(), 0)
        self.assertEqual(Tag.all().count(), 0)
        # Check that this problem doesn't already exist.
        response = self.client.get('/consistency/')
        self.assertFalse('suggestion_author' in response.context['problems'])
        # Create a suggestion without an author.
        Suggestion(key_name='a-b', title='a b', tags='a b'.split()).put()
        # Check that the author is missing.
        response = self.client.get('/consistency/')
        self.assertTrue('suggestion_author' in response.context['problems'])
        self.assertTrue("Author of a-b is None." in response.content)
        # Simulate button click to create the missing tags.
        response = self.client.post('/consistency/',
                                    {'suggestion_author': "Claim authorship"})
        self.assertRedirects(response, '/consistency/')
        # Check that the tags are now existing.
        response = self.client.get('/consistency/')
        self.assertFalse('suggestion_author' in response.context['problems'])
        self.assertTrue("All suggestions have valid authors."
                        in response.content)

