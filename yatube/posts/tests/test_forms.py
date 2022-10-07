from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post


User = get_user_model()


class PostsCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username="Tester2000")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_slug",
            description="Тестовое описание",
        )
        cls.form = PostForm()
        cls.FORM_DATA = {
            "text": "Тестовый текст",
            "group": cls.group.id,
        }

    def setUp(self):
        self.guest_user = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_author)

    def test_author_user_create_post(self):
        """Валидная форма автора создает запись в Post."""
        posts_count = Post.objects.count()

        response = self.authorized_client.post(
            reverse("posts:post_create"), data=self.FORM_DATA, follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                "posts:profile", kwargs={"username": self.user_author.username}
            ),
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.latest("id")
        self.assertEqual(post.text, self.FORM_DATA["text"])
        self.assertEqual(post.author, self.user_author)
        self.assertEqual(post.group_id, self.FORM_DATA["group"])

    def test_author_user_edit_post(self):
        """Валидная форма автора редактирует запись в Post."""
        self.post = Post.objects.create(
            text="Тестовая запись",
            author=self.user_author,
            group=self.group,
        )
        response = self.authorized_client.post(
            reverse("posts:post_edit", args=[self.post.id]),
            data=self.FORM_DATA,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"post_id": self.post.id}),
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post = Post.objects.latest("id")
        self.assertEqual(post.text, self.FORM_DATA["text"])
        self.assertEqual(post.author, self.user_author)
        self.assertEqual(post.group_id, self.FORM_DATA["group"])

    def test_guest_user_create_post(self):
        """Проверка валидности формы для гостевого пользователя."""
        posts_count = Post.objects.count()
        response = self.guest_user.post(
            reverse("posts:post_create"), deta=self.FORM_DATA, follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        redirect = reverse("login") + "?next=" + reverse("posts:post_create")
        self.assertRedirects(response, redirect)
        self.assertEqual(Post.objects.count(), posts_count)
