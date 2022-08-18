from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create_user(
            username='Author',
            first_name='First_author_name',
            last_name='Last_author_name',
        )
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description',
        )
        cls.post = Post.objects.create(
            text='Test post',
            author=cls.author,
            group=cls.group,
        )

        cls.guest_client = Client()

        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(user=PostPagesTests.author)

    def test_pages_use_correct_template(self):
        page_names_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': f'{PostPagesTests.group.slug}'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': f'{PostPagesTests.author.username}'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostPagesTests.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostPagesTests.post.id}
            ): 'posts/create_post.html',
            reverse('posts:create_post'): 'posts/create_post.html',
        }
        for reverse_name, template in page_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = PostPagesTests.authorized_client_author.get(
                    reverse_name
                )
                self.assertTemplateUsed(response, template)

    def test_index_page_shows_correct_context(self):
        response = PostPagesTests.guest_client.get(reverse('posts:index'))

        self.assertIn('title', response.context)
        self.assertEqual(
            response.context['title'],
            'Последние обновления на сайте'
        )

        self.assertIn('page_obj', response.context)
        first_post = response.context['page_obj'][0]
        self.assertEqual(
            first_post.author.username,
            PostPagesTests.post.author.username
        )
        self.assertEqual(
            first_post.author.get_full_name(),
            PostPagesTests.post.author.get_full_name()
        )
        self.assertEqual(
            first_post.id,
            PostPagesTests.post.id
        )
        self.assertEqual(
            first_post.pub_date,
            PostPagesTests.post.pub_date
        )
        self.assertEqual(
            first_post.text,
            PostPagesTests.post.text
        )
        self.assertEqual(
            first_post.group.slug,
            PostPagesTests.post.group.slug
        )

    def test_group_list_page_shows_correct_context(self):
        response = PostPagesTests.guest_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PostPagesTests.post.group.slug}
            )
        )

        self.assertIn('group', response.context)
        group = response.context['group']
        self.assertIsInstance(group, Group)
        self.assertEqual(
            group.title,
            PostPagesTests.post.group.title
        )
        self.assertEqual(
            group.description,
            PostPagesTests.post.group.description
        )

        self.assertIn('page_obj', response.context)
        first_post = response.context['page_obj'][0]
        self.assertEqual(
            first_post.author.username,
            PostPagesTests.post.author.username
        )
        self.assertEqual(
            first_post.author.get_full_name(),
            PostPagesTests.post.author.get_full_name()
        )
        self.assertEqual(
            first_post.id,
            PostPagesTests.post.id
        )
        self.assertEqual(
            first_post.pub_date,
            PostPagesTests.post.pub_date
        )
        self.assertEqual(
            first_post.text,
            PostPagesTests.post.text
        )
        self.assertEqual(
            first_post.group.slug,
            PostPagesTests.post.group.slug
        )

    def test_profile_page_shows_correct_context(self):
        response = PostPagesTests.guest_client.get(
            reverse('posts:profile',
                    kwargs={'username': PostPagesTests.author.username})
        )

        self.assertIn('page_obj', response.context)
        first_post = response.context['page_obj'][0]
        self.assertEqual(
            first_post.id,
            PostPagesTests.post.id
        )
        self.assertEqual(
            first_post.pub_date,
            PostPagesTests.post.pub_date
        )
        self.assertEqual(
            first_post.text,
            PostPagesTests.post.text
        )
        self.assertEqual(
            first_post.group.slug,
            PostPagesTests.post.group.slug
        )

        self.assertIn('profile', response.context)
        profile = response.context['profile']
        self.assertIsInstance(profile, User)
        self.assertEqual(
            profile.username,
            PostPagesTests.post.author.username
        )
        self.assertEqual(
            profile.get_full_name(),
            PostPagesTests.post.author.get_full_name()
        )

    def test_post_detail_page_shows_correct_context(self):
        response = PostPagesTests.guest_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': PostPagesTests.post.id})
        )

        self.assertIn('num_posts', response.context)
        self.assertEqual(
            response.context['num_posts'],
            Post.objects.filter(
                author__username=PostPagesTests.post.author.username).count()
        )

        self.assertIn('post', response.context)
        post = response.context['post']
        self.assertIsInstance(post, Post)
        self.assertEqual(
            post.group.title,
            PostPagesTests.post.group.title
        )
        self.assertEqual(
            post.group.slug,
            PostPagesTests.post.group.slug
        )
        self.assertEqual(
            post.author.username,
            PostPagesTests.post.author.username
        )
        self.assertEqual(
            post.author.get_full_name(),
            PostPagesTests.post.author.get_full_name()
        )
        self.assertEqual(
            post.text,
            PostPagesTests.post.text
        )
        self.assertEqual(
            post.id,
            PostPagesTests.post.id
        )

    def check_post_is_displayed_on_first_page(
        self,
        context,
        new_post_id,
        is_displayed
    ):
        assert settings.NUM_INDEX_POST >= 2, (
            'New post is expected on the first page'
        )
        assert settings.NUM_GROUP_POST >= 2, (
            'New post is expected on the first page'
        )
        assert settings.NUM_USER_POST >= 2, (
            'New post is expected on the first page'
        )
        self.assertIn('page_obj', context)
        post_ids = [post.id for post in context['page_obj']]
        if is_displayed:
            self.assertIn(new_post_id, post_ids)
        else:
            self.assertNotIn(new_post_id, post_ids)

    def test_post_with_new_group_is_correctly_shown(self):
        new_group = Group.objects.create(
            title='New group',
            slug='new-slug',
            description='New description',
        )
        new_post = Post.objects.create(
            text='Test post',
            author=PostPagesTests.author,
            group=new_group
        )
        urls_with_new_post = {
            reverse('posts:index'): True,
            reverse(
                'posts:group_list',
                kwargs={'slug': f'{new_group.slug}'}
            ): True,
            reverse(
                'posts:group_list',
                kwargs={'slug': f'{PostPagesTests.group.slug}'}
            ): False,
            reverse(
                'posts:profile',
                kwargs={'username': f'{PostPagesTests.author.username}'}
            ): True,
        }

        for url, is_appear in urls_with_new_post.items():
            with self.subTest(url=url):
                response = PostPagesTests.guest_client.get(url)
                self.check_post_is_displayed_on_first_page(
                    context=response.context,
                    new_post_id=new_post.id,
                    is_displayed=is_appear
                )

    def test_post_without_group_is_correctly_shown(self):
        new_post = Post.objects.create(
            text='Test post',
            author=PostPagesTests.author,
        )
        urls_with_new_post = {
            reverse('posts:index'): True,
            reverse(
                'posts:group_list',
                kwargs={'slug': f'{PostPagesTests.group.slug}'}
            ): False,
            reverse(
                'posts:profile',
                kwargs={'username': f'{PostPagesTests.author.username}'}
            ): True,
        }

        for url, is_appear in urls_with_new_post.items():
            with self.subTest(url=url):
                response = PostPagesTests.guest_client.get(url)
                self.check_post_is_displayed_on_first_page(
                    context=response.context,
                    new_post_id=new_post.id,
                    is_displayed=is_appear
                )

    def test_create_post_page_shows_correct_context(self):
        response = PostPagesTests.authorized_client_author.get(
            reverse('posts:create_post')
        )
        form_fields = {
            'group': forms.ModelChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_shows_correct_context(self):
        response = PostPagesTests.authorized_client_author.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostPagesTests.post.id}
            )
        )

        form_fields = {
            'group': forms.ModelChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

        self.assertTrue(response.context['is_edit'])
        self.assertEqual(
            response.context['post_id'],
            PostPagesTests.post.id
        )


class PaginatorViewstest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create_user(username='Author')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description',
        )
        cls.num = max(
            settings.NUM_INDEX_POST,
            settings.NUM_GROUP_POST,
            settings.NUM_USER_POST
        ) + 3
        for post_num in range(cls.num):
            cls.post = Post.objects.create(
                text=f'Test post {post_num}',
                author=cls.author,
                group=cls.group,
            )

        cls.guest_client = Client()

    def test_first_page_contains_posts(self):
        page_names_num_posts = {
            reverse('posts:index'): settings.NUM_INDEX_POST,
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginatorViewstest.group.slug}
            ): settings.NUM_GROUP_POST,
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewstest.author.username}
            ): settings.NUM_USER_POST
        }

        for url, num_posts in page_names_num_posts.items():
            with self.subTest(url=url):
                response = PaginatorViewstest.guest_client.get(url)
                self.assertEqual(
                    len(response.context['page_obj']),
                    num_posts
                )

    def test_second_page_contains_posts(self):
        page_names_num_posts = {
            reverse('posts:index') + '?page=2': (
                min(
                    settings.NUM_INDEX_POST,
                    PaginatorViewstest.num - settings.NUM_INDEX_POST
                )
            ),
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginatorViewstest.group.slug}
            ) + '?page=2': (
                min(
                    settings.NUM_GROUP_POST,
                    PaginatorViewstest.num - settings.NUM_GROUP_POST
                )
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewstest.author.username}
            ) + '?page=2': (
                min(
                    settings.NUM_USER_POST,
                    PaginatorViewstest.num - settings.NUM_USER_POST
                )
            ),
        }

        for url, num_posts in page_names_num_posts.items():
            with self.subTest(url=url):
                response = PaginatorViewstest.guest_client.get(url)
                self.assertEqual(
                    len(response.context['page_obj']),
                    num_posts
                )
