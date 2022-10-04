from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus


User = get_user_model()


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.URLS_AND_TEMPLATES_FOR_UNAUTH = {
            'users/signup.html': '/auth/signup/',
            'users/login.html': '/auth/login/',
            'users/password_reset_form.html': '/auth/password_reset/',
            'users/password_reset_done.html': '/auth/password_reset/done/',
            # 'users/password_reset_confirm.html': '/auth/reset/<uidb64>/<token>/',
            'users/password_reset_complete.html': '/auth/reset/done/',
        }

        cls.URLS_AND_TEMPLATES_FOR_AUTH ={
            'users/logged_out.html': '/auth/logout/',
            'users/password_change_form.html': '/auth/password_change/',
            'users/password_change_done.html': '/auth/password_change/done/',
        }

        cls.URLS_REDIRECTS_FOR_UNAUTH = {
            '/auth/login/?next=/auth/password_change/': '/auth/password_change/',
            '/auth/login/?next=/auth/password_change/done/': '/auth/password_change/done/',
        }

    def setUp(self):
        self.user = User.objects.create_user(username='simple_user')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_and_templates_for_unauthorized(self):
        '''Проверка доступности URL и соответствующих
        шаблонов для гостевых пользователей.'''
        for template, url in self.URLS_AND_TEMPLATES_FOR_UNAUTH.items():
            with self.subTest(url=url):
                response_guest = self.guest_client.get(url)
                self.assertEqual(response_guest.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response_guest, template)

    def test_urls_and_templates_for_authorized(self):
        '''Проверка доступности URL и соответствующих
        шаблонов для авторизованных пользователей.'''
        for template, url in self.URLS_AND_TEMPLATES_FOR_AUTH.items():
            with self.subTest(url=url):
                response_authorized = self.authorized_client.get(url)
                self.assertEqual(response_authorized, HTTPStatus.OK)
                self.assertTemplateUsed(response_authorized, template)

    def test_urls_redirects_for_unauthentificated(self):
        '''Проверка редиректа URL для гостевых пользователей.'''
        for redirect_url, url in self.URLS_REDIRECTS_FOR_UNAUTH.items():
            with self.subTest(url=url):
                response_checking_status = self.guest_client.get(url)
                self.assertEqual(
                    response_checking_status.status_code, HTTPStatus.FOUND
                )
                response_redirect = self.guest_client.get(url, follow=True)
                self.assertRedirects(
                    response_redirect, redirect_url
                )
