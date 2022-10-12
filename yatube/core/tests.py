from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus


User = get_user_model()


class CoreURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.URLS_TEMPLATES = {
            'core/404.html': '/unexisting_url/',
        }

    def setUp(self):
        self.user = User.objects.create_user(username='simple_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_404_status_code_uses_correct_template(self):
        """Проверка, что несуществующая страница
        использует корректный шаблон.
        """
        for template, url in self.URLS_TEMPLATES.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
                self.assertTemplateUsed(response, template)
