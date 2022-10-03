from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus


User = get_user_model()


class AboutURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='simple_user')

        cls.URLS_AND_TEMPLATES = {
            'about/tech.html': '/about/tech/',
            'about/author.html': '/about/author/',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_and_templates_for_all_users(self):
        '''
        Проверка доступности URL и соответствующих
        шаблонов для всех пользователей.'''
        for template, url in self.URLS_AND_TEMPLATES.items():
            with self.subTest(url=url):
                response_guest = self.guest_client.get(url)
                self.assertEqual(response_guest.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response_guest, template)

                # response_authorized = self.authorized_client.get(url)
                # self.assertEqual(response_authorized, HTTPStatus.OK)
                # self.assertTemplateUsed(response_authorized, template)
