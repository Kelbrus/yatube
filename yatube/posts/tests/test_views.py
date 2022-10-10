from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Group, Post, User


class PostsTestViews(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='Tester2000')
        cls.user = User.objects.create_user(username='simple_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовая запись',
            author=cls.user_author,
            group=cls.group,
        )

        cls.TEMPLATE_PAGES_NAME_FOR_ALL = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': (
                reverse(
                    'posts:group_list', kwargs={'slug': f'{cls.group.slug}'}
                )
            ),
            'posts/profile.html': (
                reverse(
                    'posts:profile', kwargs={'username': f'{cls.user_author}'}
                )
            ),
            'posts/post_detail.html': (
                reverse(
                    'posts:post_detail', kwargs={'post_id': f'{cls.post.id}'}
                )
            ),
        }

        cls.TEMPLATE_PAGES_NAME_FOR_AUTH_NOT_AUTHOR = {
            'posts/create_post.html': reverse('posts:post_create'),
        }

        cls.TEMPLATE_PAGES_NAME_FOR_AUTHOR = {
            'posts/create_post.html': (
                reverse(
                    'posts:post_edit', kwargs={'post_id': f'{cls.post.id}'}
                )
            ),
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_author)
        self.authorized_client_but_not_author = Client()
        self.authorized_client_but_not_author.force_login(self.user)

    def subtest_for_posts(self, post):
        with self.subTest(post=post):
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.group.id, self.post.group.id)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, reverse_name in self.TEMPLATE_PAGES_NAME_FOR_ALL.items():
            with self.subTest(reverse_name=reverse_name):
                response_guest = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response_guest, template)

                response_not_author = (
                    self.authorized_client_but_not_author.get(reverse_name)
                )
                self.assertTemplateUsed(response_not_author, template)

                response_author = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response_author, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index.html сформирован с правильным контекстом."""
        response_not_author = self.authorized_client_but_not_author.get(
            reverse('posts:index')
        )
        self.subtest_for_posts(response_not_author.context['page_obj'][0])

        response_guest = self.guest_client.get(reverse('posts:index'))
        self.subtest_for_posts(response_guest.context['page_obj'][0])

        response_author = self.guest_client.get(reverse('posts:index'))
        self.subtest_for_posts(response_author.context['page_obj'][0])

    def test_group_page_show_correct_context(self):
        """Шаблон group_list.html сформирован с правильным контекстом."""
        response_not_author = self.authorized_client_but_not_author.get(
            reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'})
        )
        self.assertEqual(response_not_author.context['group'], self.group)
        self.subtest_for_posts(response_not_author.context['page_obj'][0])

        response_guest = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'})
        )
        self.assertEqual(response_guest.context['group'], self.group)
        self.subtest_for_posts(response_guest.context['page_obj'][0])

        response_author = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'})
        )
        self.assertEqual(response_author.context['group'], self.group)
        self.subtest_for_posts(response_author.context['page_obj'][0])

    def test_profile_page_show_correct_context(self):
        """Шаблон profile.html сформирован с правильным контекстом."""
        response_not_author = self.authorized_client_but_not_author.get(
            reverse(
                'posts:profile', kwargs={'username': f'{self.user_author}'}
            )
        )
        self.assertEqual(
            response_not_author.context['author'], self.post.author
        )
        self.subtest_for_posts(response_not_author.context['page_obj'][0])

        response_guest = self.guest_client.get(
            reverse(
                'posts:profile', kwargs={'username': f'{self.user_author}'}
            )
        )
        self.assertEqual(response_guest.context['author'], self.post.author)
        self.subtest_for_posts(response_guest.context['page_obj'][0])

        response_author = self.authorized_client.get(
            reverse(
                'posts:profile', kwargs={'username': f'{self.user_author}'}
            )
        )
        self.assertEqual(response_author.context['author'], self.post.author)
        self.subtest_for_posts(response_author.context['page_obj'][0])

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail.html сформирован с правильным контекстом."""
        response_not_author = self.authorized_client_but_not_author.get(
            reverse('posts:post_detail', kwargs={'post_id': f'{self.post.id}'})
        )
        self.subtest_for_posts(response_not_author.context['post'])

        response_guest = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': f'{self.post.id}'})
        )
        self.subtest_for_posts(response_guest.context['post'])

        response_author = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': f'{self.post.id}'})
        )
        self.subtest_for_posts(response_author.context['post'])

    def test_form_show_correct(self):
        context = [
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
        ]
        for reverse_page in context:
            with self.subTest(reverse_page=reverse_page):
                response = self.authorized_client.get(reverse_page)
                self.assertIsInstance(
                    response.context['form'].fields['text'],
                    forms.fields.CharField,
                )
                self.assertIsInstance(
                    response.context['form'].fields['group'],
                    forms.fields.ChoiceField,
                )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='Tester2000')
        cls.user = User.objects.create_user(username='simple_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        for i in range(13):
            Post.objects.create(
                text=f'Пост #{i}', author=cls.user, group=cls.group
            )

    def setUp(self):
        self.guest_client = Client()

    def test_paginator_on_pages(self):
        """Проверка работы паджинатора на страницах."""
        first_page_count = 10
        second_page_count = 3
        pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        ]
        for page in pages:
            with self.subTest(page=page):
                self.assertEqual(
                    len(self.guest_client.get(page).context.get('page_obj')),
                    first_page_count,
                )
                self.assertEqual(
                    len(
                        self.guest_client.get(page + '?page=2').context.get(
                            'page_obj'
                        )
                    ),
                    second_page_count,
                )
