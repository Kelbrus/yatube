from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from ..models import Group, Post


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username="Tester2000")
        cls.user = User.objects.create_user(username="simple_user")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            text="Тестовый текст",
            author=cls.user_author,
            group=cls.group,
        )

        cls.URLS_AND_TEMPLATES_FOR_ALL = {
            "posts/group_list.html": "/group/test_slug/",
            "posts/profile.html": "/profile/Tester2000/",
            "posts/post_detail.html": f"/posts/{cls.post.id}/",
            "posts/index.html": "/",
        }

        cls.URLS_AND_TEMPLATES_FOR_NOT_AUTHOR = {
            "posts/create_post.html": "/create/",
        }

        cls.URLS_AND_TEMPLATES_FOR_AUTHOR = {
            "posts/create_post.html": "/edit/",
            "posts/create_post.html": f"/posts/{cls.post.id}/edit/",
        }

        cls.URLS_UNEXISTING = [
            "/unexisting_url/",
        ]

        cls.URLS_REDIRECT_FOR_GUEST = {
            f"/posts/{cls.post.id}/edit/": f"/auth/login/?next=/posts/{cls.post.id}/edit/",
            "/create/": "/auth/login/?next=/create/",
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_author)
        self.authorized_client_but_not_author = Client()
        self.authorized_client_but_not_author.force_login(self.user)

    def test_urls_and_templates_exists_at_desired_location_for_unauth(self):
        """Проверка доступных страниц и шаблонов
        для неавторизованных пользователей.
        """
        for template, url in self.URLS_AND_TEMPLATES_FOR_ALL.items():
            with self.subTest(url=url):
                response_guest = self.guest_client.get(url)
                self.assertEqual(response_guest.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response_guest, template)

    def test_urls_unexists_at_desired_location_for_all_users(self):
        """Проверка несуществующих страниц для всех пользователей."""
        for url in self.URLS_UNEXISTING:
            with self.subTest(url=url):
                response_guest = self.guest_client.get(url)
                self.assertEqual(
                    response_guest.status_code, HTTPStatus.NOT_FOUND
                )

                response_author = self.authorized_client.get(url)
                self.assertEqual(
                    response_author.status_code, HTTPStatus.NOT_FOUND
                )

                response_not_author = (
                    self.authorized_client_but_not_author.get(url)
                )
                self.assertEqual(
                    response_not_author.status_code, HTTPStatus.NOT_FOUND
                )

    def test_urls_and_templates_exists_at_right_place_for_not_author(self):
        """Проверка страниц и шаблонов для авторизованных
        пользователей,не являющихся автором.
        """
        for template, url in self.URLS_AND_TEMPLATES_FOR_NOT_AUTHOR.items():
            with self.subTest(url=url):
                response_not_author = (
                    self.authorized_client_but_not_author.get(url)
                )
                self.assertEqual(
                    response_not_author.status_code, HTTPStatus.OK
                )
                self.assertTemplateUsed(response_not_author, template)

    def test_urls_and_templates_exists_at_desired_location_for_author(self):
        """Проверка страниц и шаблонов для
        авторизованного пользователя,являющегося автором.
        """
        for template, url in self.URLS_AND_TEMPLATES_FOR_AUTHOR.items():
            with self.subTest(url=url):
                response_author = self.authorized_client.get(url)
                self.assertEqual(response_author.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response_author, template)

    def test_redirect_urls_for_unauthorized_user(self):
        """Проверка переадресации на страницу авторизации
        для гостевых пользователей с последующим редиректом.
        """
        for url, redirect_url in self.URLS_REDIRECT_FOR_GUEST.items():
            with self.subTest(url=url):
                response_checking_status = self.guest_client.get(url)
                self.assertEqual(
                    response_checking_status.status_code, HTTPStatus.FOUND
                )
                response_redirect = self.guest_client.get(url, follow=True)
                self.assertRedirects(response_redirect, redirect_url)
