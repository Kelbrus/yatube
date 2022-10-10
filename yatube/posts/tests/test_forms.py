import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from http import HTTPStatus

from ..forms import PostForm
from ..models import Group, Post, User


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='Tester2000')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.form = PostForm()
        cls.posts_count = Post.objects.count()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.FORM_DATA = {
            'text': 'Тестовый текст',
            'group': cls.group.id,
            'image': cls.uploaded,
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_user = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_author)

    def test_author_user_create_post(self):
        """Валидная форма автора создает запись в Post."""
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=self.FORM_DATA, follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile', kwargs={'username': self.user_author.username}
            ),
        )
        self.assertEqual(Post.objects.count(), self.posts_count + 1)
        post = Post.objects.latest('id')
        self.assertEqual(post.text, self.FORM_DATA['text'])
        self.assertEqual(post.author, self.user_author)
        self.assertEqual(post.group_id, self.FORM_DATA['group'])

    def test_author_user_edit_post(self):
        """Валидная форма автора редактирует запись в Post."""
        self.post = Post.objects.create(
            text='Тестовая запись',
            author=self.user_author,
        )
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[self.post.id]),
            data=self.FORM_DATA,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post = Post.objects.latest('id')
        self.assertEqual(post.text, self.FORM_DATA['text'])
        self.assertEqual(post.author, self.user_author)
        self.assertEqual(post.group_id, self.FORM_DATA['group'])

    def test_guest_user_create_post(self):
        """Проверка валидности формы для гостевого пользователя."""
        response = self.guest_user.post(
            reverse('posts:post_create'), data=self.FORM_DATA, follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        redirect = reverse('login') + '?next=' + reverse('posts:post_create')
        self.assertRedirects(response, redirect)
        self.assertEqual(Post.objects.count(), self.posts_count)
