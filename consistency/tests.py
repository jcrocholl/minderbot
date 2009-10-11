from django.test import TestCase
from django.contrib.auth.models import User


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


class AdminTest(TestCase):

    def setUp(self):
        admin = User.objects.create_user('admin', 'a@b.com', 'password')
        admin.is_staff = True
        admin.save()
        self.assertTrue(
            self.client.login(username='a@b.com', password='password'))

    def test_index(self):
        response = self.client.get('/consistency/')
        self.failUnlessEqual(response.status_code, 200)
