from xml.dom import minidom

from django.test import TestCase


class ClientTest(TestCase):

    def test_trailing_slash(self):
        response = self.client.get('/pages/faq')
        self.assertRedirects(response, '/pages/faq/', status_code=301)

    def test_welcome(self):
        response = self.client.get('/pages/welcome/')
        self.assertEqual(response.status_code, 200)
        minidom.parseString(response.content)

    def test_about(self):
        response = self.client.get('/pages/about/')
        self.assertEqual(response.status_code, 200)
        minidom.parseString(response.content)

    def test_faq(self):
        response = self.client.get('/pages/faq/')
        self.assertEqual(response.status_code, 200)
        minidom.parseString(response.content)

    def test_terms(self):
        response = self.client.get('/pages/terms/')
        self.assertEqual(response.status_code, 200)
        minidom.parseString(response.content)

    def test_privacy(self):
        response = self.client.get('/pages/privacy/')
        self.assertEqual(response.status_code, 200)
        minidom.parseString(response.content)

    def test_404(self):
        response = self.client.get('/pages/doesnotexist/')
        self.assertEqual(response.status_code, 404)
