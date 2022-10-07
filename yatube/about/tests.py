from django.test import TestCase, Client
from http import HTTPStatus


class AboutURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.URLS_AND_TEMPLATES = {
            'about/tech.html': '/about/tech/',
            'about/author.html': '/about/author/',
        }

    def setUp(self):
        self.guest_client = Client()

    def test_urls_and_templates_for_all_users(self):
        """Проверка доступности URL и соответствующих
        шаблонов для всех пользователей.
        """
        for template, url in self.URLS_AND_TEMPLATES.items():
            with self.subTest(url=url):
                response_guest = self.guest_client.get(url)
                self.assertEqual(response_guest.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response_guest, template)
