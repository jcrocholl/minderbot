from django.test import TestCase
from django.contrib.auth.models import User


class AnonymousTest(TestCase):

    def test_anonymous(self):
        response = self.client.get('/dashboard/')
        self.assertRedirects(response, '/accounts/login/?next=/dashboard/')


class NotAdminTest(TestCase):

    def setUp(self):
        user = User.objects.create_user('user', 'user@example.com', 'pass')
        self.assertFalse(user.is_staff)
        self.assertTrue(
            self.client.login(username='user@example.com', password='pass'))

    def test_not_admin(self):
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Access denied" in response.content)
        self.assertTrue("This page is for staff members only."
                        in response.content)


class AdminTest(TestCase):

    def setUp(self):
        admin = User.objects.create_user('admin', 'admin@example.com', 'pass')
        admin.is_staff = True
        admin.save()
        self.assertTrue(
            self.client.login(username='admin@example.com', password='pass'))

    def test_admin(self):
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
