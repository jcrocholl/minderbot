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
        self.assertTrue('http://' in response.content)
        self.assertTrue('/consistency/' in response.content)


class AdminTest(TestCase):

    def setUp(self):
        admin = User.objects.create_user('admin', 'a@b.com', 'password')
        admin.is_staff = True
        admin.save()
        self.assertTrue(
            self.client.login(username='a@b.com', password='password'))

    def test_suggestion_author(self):
        # Check that this problem doesn't already exist.
        response = self.client.get('/consistency/')
        self.assertFalse('suggestion_author' in response.context['problems'])
        # Create a suggestion without an author.
        Suggestion(key_name='a-b', title='a b', tags='a b'.split()).put()
        # Check that the missing author is detected.
        response = self.client.get('/consistency/')
        self.assertTrue('suggestion_author' in response.context['problems'])
        self.assertTrue("Author of a-b is None." in response.content)
        # Simulate button click to fix this problem.
        response = self.client.post('/consistency/',
                                    {'suggestion_author': "Claim authorship"})
        self.assertRedirects(response, '/consistency/')
        # Check that the tags are now existing.
        response = self.client.get('/consistency/')
        self.assertFalse('suggestion_author' in response.context['problems'])
        self.assertTrue("All suggestions have valid authors."
                        in response.content)

    def test_suggestion_missing(self):
        # Check that this problem doesn't already exist.
        self.assertEqual(Tag.all().count(), 0)
        response = self.client.get('/consistency/')
        self.assertFalse('suggestion_missing' in response.context['problems'])
        # Create tags but not all suggestions.
        Suggestion(key_name='a-b', title='a b', tags='a b'.split()).put()
        Tag(key_name='a', count=2, suggestions='a-b a-c'.split()).put()
        Tag(key_name='b', count=2, suggestions='b-c'.split()).put()
        self.assertEqual(Tag.all().count(), 2)
        # Check that the missing suggestions are detected.
        response = self.client.get('/consistency/')
        self.assertTrue('suggestion_missing' in response.context['problems'])
        self.assertTrue("Suggestion a-c is referenced by a but does not exist."
                        in response.content)
        self.assertTrue("Suggestion b-c is referenced by b but does not exist."
                        in response.content)
        # Simulate button click to fix this problem.
        response = self.client.post('/consistency/',
                                    {'suggestion_missing': "Create missing"})
        self.assertRedirects(response, '/consistency/')
        # Check that the references are now gone.
        self.assertEqual(Tag.all().count(), 1)
        self.assertEqual(Tag.get_by_key_name('a').count, 1)
        self.assertEqual(len(Tag.get_by_key_name('a').suggestions), 1)
        response = self.client.get('/consistency/')
        self.assertFalse('suggestion_missing' in response.context['problems'])
        self.assertTrue("All referenced suggestions exist."
                        in response.content)

    def test_suggestion_tag(self):
        # Check that this problem doesn't already exist.
        response = self.client.get('/consistency/')
        self.assertFalse('suggestion_tag' in response.context['problems'])
        # Create a suggestion and a tag.
        Suggestion(key_name='a-b', title='a b', tags='b'.split()).put()
        Tag(key_name='a', count=2, suggestions='a-b a-c'.split()).put()
        # Check that the missing reverse reference is detected.
        response = self.client.get('/consistency/')
        self.assertTrue('suggestion_tag' in response.context['problems'])
        self.assertTrue("Suggestion a-b does not reverse reference a."
                        in response.content)
        # Simulate button click to fix this problem.
        response = self.client.post('/consistency/',
                                    {'suggestion_tag': "Create references"})
        self.assertRedirects(response, '/consistency/')
        # Check that the missing references were created.
        self.assertTrue('a' in Suggestion.get_by_key_name('a-b').tags)
        response = self.client.get('/consistency/')
        self.assertFalse('suggestion_tag' in response.context['problems'])
        self.assertTrue("All tag-suggestion references have a reverse."
                        in response.content)

    def test_tag_count(self):
        # Check that this problem doesn't already exist.
        response = self.client.get('/consistency/')
        self.assertFalse('tag_count' in response.context['problems'])
        # Create a tag with incorrect count.
        Tag(key_name='a', suggestions='a-b a-c'.split(), count=3).put()
        # Check that the incorrect count is detected.
        response = self.client.get('/consistency/')
        self.assertTrue('tag_count' in response.context['problems'])
        self.assertTrue("Tag a has count 3 but references 2 suggestions."
                        in response.content)
        # Simulate button click to fix this problem.
        response = self.client.post('/consistency/',
                                    {'tag_count': "Adjust tag counts"})
        self.assertRedirects(response, '/consistency/')
        # Check that the count is now correct.
        response = self.client.get('/consistency/')
        self.assertFalse('tag_count' in response.context['problems'])
        self.assertTrue("All tag count fields are correct."
                        in response.content)

    def test_tag_missing(self):
        # Check that this problem doesn't already exist.
        self.assertEqual(Tag.all().count(), 0)
        response = self.client.get('/consistency/')
        self.assertFalse('tag_missing' in response.context['problems'])
        # Create a suggestion but not the tags.
        Suggestion(key_name='a-b', title='a b', tags='a b'.split()).put()
        # Check that the missing tags are detected.
        response = self.client.get('/consistency/')
        self.assertTrue('tag_missing' in response.context['problems'])
        self.assertTrue("Tag a is referenced by a-b but does not exist."
                        in response.content)
        self.assertTrue("Tag b is referenced by a-b but does not exist."
                        in response.content)
        # Simulate button click to fix this problem.
        response = self.client.post('/consistency/',
                                    {'tag_missing': "Create missing tags"})
        self.assertRedirects(response, '/consistency/')
        # Check that the tags are now existing.
        self.assertEqual(Tag.all().count(), 2)
        response = self.client.get('/consistency/')
        self.assertFalse('tag_missing' in response.context['problems'])
        self.assertTrue("All referenced tags exist." in response.content)
