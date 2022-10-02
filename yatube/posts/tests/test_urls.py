from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post


User = get_user_model()

URLS_AND_TEMPLATES_FOR_ALL = {
    'posts/group_list.html': '/group/test_slug/',
    'posts/profile.html': '/profile/Tester2000/',
    'posts/post_detail.html': 'posts/<int:post_id>/',
    'posts/index.html': '/',
}

URLS_AND_TEMPLATES_FOR_NOT_AUTHOR = {
    'posts/create_post.html': '/create/',
}

URLS_AND_TEMPLATES_FOR_AUTHOR = {
    'posts/create_post.html': '/edit/',
    'posts/create_post.html': '/posts/<int:post_id>/edit/',
}

URLS_UNEXISTING = ['/unexisting_url/', ]


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Tester2000')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_but_not_author = Client()
        self.authorized_client_but_not_author.force_login(PostURLTests.user)

    def test_urls_and_templates_exists_at_desired_location_for_unauth(self):
        '''Проверка доступных страниц и шаблонов для неавторизованных пользователей.'''
        for template, url in URLS_AND_TEMPLATES_FOR_ALL.items():
            with self.subTest(url=url):
                response_guest = self.guest_client.get(url)
                self.assertEqual(response_guest.status_code, 200)
                self.assertTemplateUsed(response_guest, template)

    def test_urls_unexists_at_desired_location_for_all_users(self):
        '''Проверка несуществующих страниц для всех пользователей.'''
        for url in URLS_UNEXISTING:
            with self.subTest(url=url):
                response_guest = self.guest_client.get(url)
                self.assertEqual(response_guest.status_code, 404)

                response_author = self.authorized_client.get(url)
                self.assertEqual(response_author.status_code, 404)

                response_not_author = self.authorized_client_but_not_author.get(url)
                self.assertEqual(response_not_author.status_code, 404)

    def test_urls_and_templates_exists_at_desired_location_for_auth_not_author(self):
        '''Проверка страниц и шаблонов для авторизованных пользователей,не являющихся автором.'''
        for template, url in URLS_AND_TEMPLATES_FOR_NOT_AUTHOR.items():
            with self.subTest(url=url):
                response_not_author = self.authorized_client_but_not_author.get(url)
                self.assertEqual(response_not_author.status_code, 200)
                self.assertTemplateUsed(response_not_author, template)

    def test_urls_and_templates_exists_at_desired_location_for_author(self):
        '''Проверка страниц и шаблонов для авторизованного пользователя,являющегося автором.'''
        for template, url in URLS_AND_TEMPLATES_FOR_AUTHOR.items():
            with self.subTest(url=url):
                response_author = self.authorized_client.get(url)
                self.assertEqual(response_author.status_code, 200)
                self.assertTemplateUsed(response_author, template)



