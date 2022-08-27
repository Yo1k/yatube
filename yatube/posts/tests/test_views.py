import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import reverse

from ..models import Comment, Follow, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create_user(
            username='Author',
            first_name='First_author_name',
            last_name='Last_author_name',
        )
        cls.reader = User.objects.create_user(
            username='Reader',
        )
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif',
        )
        cls.post = Post.objects.create(
            text='Test post',
            author=cls.author,
            group=cls.group,
            image=uploaded,
        )
        cls.comment = Comment.objects.create(
            text='Test comment',
            author=cls.author,
            post=cls.post,
        )

        cls.guest_client = Client()

        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(user=PostPagesTests.author)

        cls.authorized_client_reader = Client()
        cls.authorized_client_reader.force_login(user=PostPagesTests.reader)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def tearDown(self):
        super().tearDown()
        cache.clear()

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
            ): 'posts/post_create.html',
            reverse('posts:post_create'): 'posts/post_create.html',
        }
        for reverse_name, template in page_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = PostPagesTests.authorized_client_author.get(
                    reverse_name
                )
                self.assertTemplateUsed(response, template)

    def test_index_page_is_cached(self):
        new_post = Post.objects.create(
            text='Test post caching',
            author=PostPagesTests.author,
        )
        response = PostPagesTests.guest_client.get(reverse('posts:index'))
        self.assertIn(new_post.text.encode('utf8'), response.content)

        Post.objects.get(id=new_post.id).delete()
        response = PostPagesTests.guest_client.get(reverse('posts:index'))
        self.assertIn(new_post.text.encode('utf8'), response.content)

        cache.clear()
        response = PostPagesTests.guest_client.get(reverse('posts:index'))
        self.assertNotIn(new_post.text.encode('utf8'), response.content)

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
            first_post.image,
            PostPagesTests.post.image
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
            first_post.image,
            PostPagesTests.post.image
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
            first_post.image,
            PostPagesTests.post.image
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

    def check_page_with_comments_shows_correct_context(self, response):
        form_fields = {
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                self.assertIn('form', response.context)
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

        self.assertIn('comments', response.context)
        first_comment = response.context['comments'][0]
        self.assertEqual(
            first_comment.author.username,
            PostPagesTests.comment.author.username
        )
        self.assertEqual(
            first_comment.created,
            PostPagesTests.comment.created
        )
        self.assertEqual(
            first_comment.text,
            PostPagesTests.comment.text
        )
        self.assertEqual(
            first_comment.post,
            PostPagesTests.post
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
            post.image,
            PostPagesTests.post.image
        )
        self.assertEqual(
            post.id,
            PostPagesTests.post.id
        )
        self.check_page_with_comments_shows_correct_context(response)

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

        for url, is_displayed in urls_with_new_post.items():
            with self.subTest(url=url):
                response = PostPagesTests.guest_client.get(url)
                self.check_post_is_displayed_on_first_page(
                    context=response.context,
                    new_post_id=new_post.id,
                    is_displayed=is_displayed
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
            reverse('posts:post_create')
        )
        form_fields = {
            'group': forms.ModelChoiceField,
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField,
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
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                self.assertIn('form', response.context)
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

        self.assertTrue(response.context['is_edit'])
        self.assertEqual(
            response.context['post_id'],
            PostPagesTests.post.id
        )

    def test_auth_client_can_follow_other_users(self):
        follows_count = Follow.objects.count()
        response = PostPagesTests.authorized_client_reader.post(
            path=reverse(
                'posts:profile_follow',
                kwargs={'username': PostPagesTests.author.username}
            )
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': PostPagesTests.author.username}
            )
        )
        self.assertEqual(
            Follow.objects.count(),
            follows_count + 1
        )
        new_follow = Follow.objects.all()[0]
        self.assertEqual(
            new_follow.author,
            PostPagesTests.author
        )
        self.assertEqual(
            new_follow.user,
            PostPagesTests.reader
        )

    def test_auth_client_can_unfollow_other_users(self):
        assert PostPagesTests.reader != PostPagesTests.author
        new_follow = Follow.objects.create(
            author=PostPagesTests.author,
            user=PostPagesTests.reader
        )
        response = PostPagesTests.authorized_client_reader.post(
            path=reverse(
                'posts:profile_unfollow',
                kwargs={'username': PostPagesTests.author.username}
            )
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': PostPagesTests.author.username}
            )
        )
        self.assertFalse(
            Follow.objects.filter(id=new_follow.id).exists()
        )

    def test_auth_client_can_not_follow_himself(self):
        follows_count = Follow.objects.count()
        response = PostPagesTests.authorized_client_author.post(
            path=reverse(
                'posts:profile_follow',
                kwargs={'username': PostPagesTests.author.username}
            )
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': PostPagesTests.author.username}
            )
        )
        self.assertEqual(
            Follow.objects.count(),
            follows_count
        )

    def test_follow_index_is_correctly_shown_for_followers_and_others(self):
        Follow.objects.create(
            user=PostPagesTests.reader,
            author=PostPagesTests.author,
        )

        not_reader = User.objects.create_user(username='Notreader')
        authorized_client = Client()
        authorized_client.force_login(user=not_reader)

        new_post = Post.objects.create(
            text='New post',
            author=PostPagesTests.author,
        )

        is_displayed_for_clients = {
            PostPagesTests.authorized_client_reader: True,
            authorized_client: False
        }

        for client, is_displayed in is_displayed_for_clients.items():
            with self.subTest(client=client):
                response = client.get(reverse('posts:follow_index'))
                self.check_post_is_displayed_on_first_page(
                    context=response.context,
                    new_post_id=new_post.id,
                    is_displayed=is_displayed
                )


class PaginatorViewsTest(TestCase):
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

    def tearDown(self):
        super().tearDown()
        cache.clear()

    def test_first_page_contains_posts(self):
        page_names_num_posts = {
            reverse('posts:index'): settings.NUM_INDEX_POST,
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginatorViewsTest.group.slug}
            ): settings.NUM_GROUP_POST,
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewsTest.author.username}
            ): settings.NUM_USER_POST
        }
        for url, num_posts in page_names_num_posts.items():
            with self.subTest(url=url):
                response = PaginatorViewsTest.guest_client.get(url)
                self.assertEqual(
                    len(response.context['page_obj']),
                    num_posts
                )

    def test_second_page_contains_posts(self):
        page_names_num_posts = {
            reverse('posts:index') + '?page=2': (
                min(
                    settings.NUM_INDEX_POST,
                    PaginatorViewsTest.num - settings.NUM_INDEX_POST
                )
            ),
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginatorViewsTest.group.slug}
            ) + '?page=2': (
                min(
                    settings.NUM_GROUP_POST,
                    PaginatorViewsTest.num - settings.NUM_GROUP_POST
                )
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewsTest.author.username}
            ) + '?page=2': (
                min(
                    settings.NUM_USER_POST,
                    PaginatorViewsTest.num - settings.NUM_USER_POST
                )
            ),
        }

        for url, num_posts in page_names_num_posts.items():
            with self.subTest(url=url):
                response = PaginatorViewsTest.guest_client.get(url)
                self.assertEqual(
                    len(response.context['page_obj']),
                    num_posts
                )
