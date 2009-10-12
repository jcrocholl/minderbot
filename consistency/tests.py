from datetime import datetime, timedelta

from django.test import TestCase
from django.contrib.auth.models import User

from suggestions.models import Suggestion
from tags.models import Tag

from consistency import views


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

    def test_no_problem(self):
        response = self.client.get('/consistency/')
        self.assertFalse(response.context['problems'])
        for problem in views.PROBLEM_MESSAGES:
            self.assertFalse(problem in response.content)
            self.assertTrue(views.PROBLEM_MESSAGES[problem][2]
                            in response.content)
        self.assertTrue('class="success"' in response.content)
        self.assertFalse('class="error"' in response.content)

    def test_suggestion_author(self):
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
        self.assertEqual(Tag.all().count(), 0)
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

    def test_tag_created(self):
        # Create two tags with incorrect timestamp.
        Suggestion(key_name='a-b', title='a b', tags='a b'.split(),
                   created=datetime.now() - timedelta(hours=3)).put()
        Tag(key_name='a', suggestions='a-b'.split(), count=1,
            created=None).put()
        Tag(key_name='b', suggestions='a-b'.split(), count=1).put()
        # Check that the incorrect count is detected.
        response = self.client.get('/consistency/')
        self.assertTrue('tag_created' in response.context['problems'])
        self.assertTrue("Timestamp of tag a is not set." in response.content)
        self.assertTrue("Timestamp of tag b is younger than a-b."
                        in response.content)
        # Simulate button click to fix this problem.
        response = self.client.post('/consistency/',
                                    {'tag_created': "Adjust timestamps"})
        self.assertRedirects(response, '/consistency/')
        # Check that the timestamps are now correct.
        self.assertEqual(Suggestion.get_by_key_name('a-b').created,
                         Tag.get_by_key_name('a').created)
        self.assertEqual(Suggestion.get_by_key_name('a-b').created,
                         Tag.get_by_key_name('b').created)
        response = self.client.get('/consistency/')
        self.assertFalse('tag_created' in response.context['problems'])
        self.assertTrue("All tag timestamps are reasonable."
                        in response.content)

    def test_tag_empty(self):
        # Create a tag without suggestion references.
        self.assertEqual(Tag.all().count(), 0)
        Tag(key_name='a', suggestions=[], count=0).put()
        self.assertEqual(Tag.all().count(), 1)
        # Check that the empty tag is detected.
        response = self.client.get('/consistency/')
        self.assertTrue('tag_empty' in response.context['problems'])
        self.assertTrue("Tag a does not reference any suggestions."
                        in response.content)
        # Simulate button click to fix this problem.
        response = self.client.post('/consistency/',
                                    {'tag_empty': "Create missing tags"})
        self.assertRedirects(response, '/consistency/')
        # Check that the tags are now existing.
        self.assertEqual(Tag.all().count(), 0)
        response = self.client.get('/consistency/')
        self.assertFalse('tag_empty' in response.context['problems'])
        self.assertTrue("All tags reference at least one suggestion."
                        in response.content)

    def test_tag_missing(self):
        self.assertEqual(Tag.all().count(), 0)
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

    def test_tag_suggestion(self):
        # Create a suggestion but not the tags.
        Suggestion(key_name='a-b', title='a b', tags='a b'.split()).put()
        Suggestion(key_name='b-c', title='b c', tags='b'.split()).put()
        Tag(key_name='a', suggestions='a-b'.split(), count=0).put()
        Tag(key_name='b', suggestions='b-c'.split(), count=0).put()
        self.assertEqual(Suggestion.all().count(), 2)
        self.assertEqual(Tag.all().count(), 2)
        self.assertEqual(len(Tag.get_by_key_name('b').suggestions), 1)
        # Check that the missing tag-suggestion reference is detected.
        response = self.client.get('/consistency/')
        self.assertTrue('tag_suggestion' in response.context['problems'])
        self.assertTrue("Tag b does not reverse reference a-b."
                        in response.content)
        # Simulate button click to fix this problem.
        response = self.client.post('/consistency/',
                                    {'tag_suggestion': "Create references"})
        self.assertRedirects(response, '/consistency/')
        # Check that the tags are now existing.
        self.assertEqual(Suggestion.all().count(), 2)
        self.assertEqual(Tag.all().count(), 2)
        self.assertEqual(len(Tag.get_by_key_name('b').suggestions), 2)
        response = self.client.get('/consistency/')
        self.assertFalse('tag_suggestion' in response.context['problems'])
        self.assertTrue("All suggestion-tag references have a reverse."
                        in response.content)
