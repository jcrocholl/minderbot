from datetime import datetime, timedelta

from django.test import TestCase
from django.contrib.auth.models import User

from reminders.models import Reminder
from tags.models import Tag

from consistency import views


class AnonymousTest(TestCase):

    def test_anonymous(self):
        response = self.client.get('/consistency/')
        self.assertRedirects(response, '/accounts/login/?next=/consistency/')


class NotAdminTest(TestCase):

    def setUp(self):
        user = User.objects.create_user('user', 'user@example.com', 'pass')
        self.assertFalse(user.is_staff)
        self.assertTrue(
            self.client.login(username='user@example.com', password='pass'))

    def test_not_admin(self):
        response = self.client.get('/consistency/')
        self.assertRedirects(response, '/accounts/login/?next=/consistency/')


class CronTest(TestCase):

    def test_cron(self):
        response = self.client.get('/consistency/',
                                   HTTP_X_APPENGINE_CRON='true')
        self.failUnlessEqual(response.status_code, 200)
        return
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertTrue('http://' in response.content)
        self.assertTrue('/consistency/' in response.content)


class AdminTest(TestCase):

    def setUp(self):
        admin = User.objects.create_user('admin', 'a@b.com', 'password')
        admin.is_staff = True
        admin.save()
        self.assertTrue(
            self.client.login(username='a@b.com', password='password'))
        # Phantom user doesn't exist: don't save to database.
        self.phantom = User(key_name='phantom', username='phantom',
                            email='phantom@example.com')

    def test_no_problem(self):
        response = self.client.get('/consistency/')
        self.failUnlessEqual(response.status_code, 200)
        self.assertFalse(response.context['problems'])
        for problem in views.PROBLEM_MESSAGES:
            self.assertFalse(problem in response.content)
            self.assertTrue(views.PROBLEM_MESSAGES[problem][2]
                            in response.content)
        self.assertFalse('class="error"' in response.content)
        self.assertTrue('class="success"' in response.content)

    def test_reminder_owner(self):
        return
        # Create a reminder with a owner that doesn't exist.
        Reminder(key_name='a-b', title='a b', owner=self.phantom).put()
        # Check that the phantom owner is detected.
        response = self.client.get('/consistency/')
        self.assertTrue('reminder_owner' in response.context['problems'])
        self.assertTrue("Owner of a-b does not exist." in response.content)
        # Simulate button click to fix this problem.
        response = self.client.post('/consistency/',
                                    {'reminder_owner': "Claim ownership"})
        self.assertRedirects(response, '/consistency/')
        # Check that the tags are now existing.
        response = self.client.get('/consistency/')
        self.assertFalse('reminder_owner' in response.context['problems'])

    def test_reminder_missing(self):
        return
        self.assertEqual(Tag.all().count(), 0)
        # Create tags but not all reminders.
        Reminder(key_name='a-b', title='a b', tags='a b'.split()).put()
        Tag(key_name='a', count=2, reminders='a-b a-c'.split()).put()
        Tag(key_name='b', count=2, reminders='b-c'.split()).put()
        self.assertEqual(Tag.all().count(), 2)
        # Check that the missing reminders are detected.
        response = self.client.get('/consistency/')
        self.assertTrue('reminder_missing' in response.context['problems'])
        self.assertTrue("Reminder a-c is referenced by a but does not exist."
                        in response.content)
        self.assertTrue("Reminder b-c is referenced by b but does not exist."
                        in response.content)
        # Simulate button click to fix this problem.
        response = self.client.post('/consistency/',
                                    {'reminder_missing': "Create missing"})
        self.assertRedirects(response, '/consistency/')
        # Check that the references are now gone.
        self.assertEqual(Tag.all().count(), 1)
        self.assertEqual(Tag.get_by_key_name('a').count, 1)
        self.assertEqual(len(Tag.get_by_key_name('a').reminders), 1)
        response = self.client.get('/consistency/')
        self.assertFalse('reminder_missing' in response.context['problems'])

    def test_reminder_tag(self):
        return
        # Create a reminder and a tag.
        Reminder(key_name='a-b', title='a b', tags='b'.split()).put()
        Tag(key_name='a', count=2, reminders='a-b a-c'.split()).put()
        # Check that the missing reverse reference is detected.
        response = self.client.get('/consistency/')
        self.assertTrue('reminder_tag' in response.context['problems'])
        self.assertTrue("Reminder a-b does not reverse reference a."
                        in response.content)
        # Simulate button click to fix this problem.
        response = self.client.post('/consistency/',
                                    {'reminder_tag': "Create references"})
        self.assertRedirects(response, '/consistency/')
        # Check that the missing references were created.
        self.assertTrue('a' in Reminder.get_by_key_name('a-b').tags)
        response = self.client.get('/consistency/')
        self.assertFalse('reminder_tag' in response.context['problems'])

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

    def test_tag_created_none(self):
        # Create a tag with missing timestamp.
        Reminder(key_name='a-b', title='a b', tags='a b'.split()).put()
        Tag(key_name='a', suggestions=['a-b'], count=1, created=None).put()
        # Check that the missing timestamp is detected.
        response = self.client.get('/consistency/')
        self.assertTrue('tag_created_none' in response.context['problems'])
        self.assertTrue("Tag a is missing a timestamp." in response.content)
        # Simulate button click to fix this problem.
        response = self.client.post('/consistency/',
                                    {'tag_created_none': "Adjust timestamps"})
        self.assertRedirects(response, '/consistency/')
        # Check that the timestamps are now correct.
        self.assertEqual(Reminder.get_by_key_name('a-b').created,
                         Tag.get_by_key_name('a').created)
        response = self.client.get('/consistency/')
        self.assertFalse('tag_created_none' in response.context['problems'])

    def test_tag_created_later(self):
        # Create a tag with timestamp later than suggestion.
        Reminder(key_name='a-b', title='a b', tags='a b'.split()).put()
        later = Reminder.get_by_key_name('a-b').created + timedelta(seconds=1)
        Tag(key_name='a', suggestions=['a-b'], count=1, created=later).put()
        # Check that the missing timestamp is detected.
        response = self.client.get('/consistency/')
        self.assertTrue('tag_created_later' in response.context['problems'])
        print response.content
        self.assertTrue("Tag a was created after suggestion a-b."
                        in response.content)
        # Simulate button click to fix this problem.
        response = self.client.post('/consistency/',
                                    {'tag_created_later': "Adjust timestamps"})
        self.assertRedirects(response, '/consistency/')
        # Check that the timestamps are now correct.
        self.assertEqual(Reminder.get_by_key_name('a-b').created,
                         Tag.get_by_key_name('a').created)
        response = self.client.get('/consistency/')
        self.assertFalse('tag_created_later' in response.context['problems'])

    def test_tag_empty(self):
        # Create a tag without reminder references.
        self.assertEqual(Tag.all().count(), 0)
        Tag(key_name='a', reminders=[], count=0).put()
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

    def test_tag_missing(self):
        return
        self.assertEqual(Tag.all().count(), 0)
        # Create a reminder but not the tags.
        Reminder(key_name='a-b', title='a b', tags='a b'.split()).put()
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

    def test_tag_reminder(self):
        return
        # Create a reminder but not the tags.
        Reminder(key_name='a-b', title='a b', tags='a b'.split()).put()
        Reminder(key_name='b-c', title='b c', tags='b'.split()).put()
        Tag(key_name='a', reminders='a-b'.split(), count=0).put()
        Tag(key_name='b', reminders='b-c'.split(), count=0).put()
        self.assertEqual(Reminder.all().count(), 2)
        self.assertEqual(Tag.all().count(), 2)
        self.assertEqual(len(Tag.get_by_key_name('b').reminders), 1)
        # Check that the missing tag-reminder reference is detected.
        response = self.client.get('/consistency/')
        self.assertTrue('tag_reminder' in response.context['problems'])
        self.assertTrue("Tag b does not reverse reference a-b."
                        in response.content)
        # Simulate button click to fix this problem.
        response = self.client.post('/consistency/',
                                    {'tag_reminder': "Create references"})
        self.assertRedirects(response, '/consistency/')
        # Check that the tags are now existing.
        self.assertEqual(Reminder.all().count(), 2)
        self.assertEqual(Tag.all().count(), 2)
        self.assertEqual(len(Tag.get_by_key_name('b').reminders), 2)
        response = self.client.get('/consistency/')
        self.assertFalse('tag_reminder' in response.context['problems'])
