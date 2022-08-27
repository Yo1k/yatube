from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create_user(username='Author')
        cls.user = User.objects.create_user(username='User')
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
        cls.authorized_client_author.force_login(user=PostURLTests.author)

        cls.authorized_client_user = Client()
        cls.authorized_client_user.force_login(user=PostURLTests.user)

    def tearDown(self):
        super().tearDown()
        cache.clear()

    def test_url_exists_at_desired_location_for_guest_client(self):
        urls_for_guest = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': PostURLTests.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PostURLTests.author.username}
            ),
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostURLTests.post.id}
            ),
        ]

        for url in urls_for_guest:
            with self.subTest(url=url):
                response = PostURLTests.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_does_not_exist_at_desired_location_for_guest_client(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(
            response,
            template_name='core/404.html'
        )

    def test_url_exists_at_desired_location_for_auth_clients(self):
        response = PostURLTests.authorized_client_user.get(
            reverse('posts:post_create'),
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_exists_at_desired_location_for_auth_post_authors(self):
        response = PostURLTests.authorized_client_author.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostURLTests.post.id}
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_redirects_anonymous_on_auth_login(self):
        for_auth_only_urls = [
            reverse('posts:post_create'),
            reverse(
                'posts:add_comment',
                kwargs={'post_id': PostURLTests.post.id}
            ),
            reverse('posts:follow_index'),
            reverse(
                'posts:profile_follow',
                kwargs={'username': PostURLTests.author.username}
            ),
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': PostURLTests.author.username}
            )
        ]
        for url in for_auth_only_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                expected_url = (reverse('users:login') + '?next=' + url)
                self.assertRedirects(response, expected_url)

    def test_post_edit_url_redirects_anonymous_on_auth_login(self):
        post_edit_url = reverse(
            'posts:post_edit',
            kwargs={'post_id': PostURLTests.post.id}
        )
        response = self.guest_client.get(post_edit_url)
        expected_url = (
            reverse('users:login')
            + '?next='
            + post_edit_url
        )
        self.assertRedirects(
            response=response,
            expected_url=expected_url
        )

    def test_post_edit_url_redirects_user_not_author_on_post_detail(self):
        response = PostURLTests.authorized_client_user.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostURLTests.post.id}
            )
        )
        expected_url = reverse(
            'posts:post_detail',
            kwargs={'post_id': PostURLTests.post.id}
        )
        self.assertRedirects(
            response=response,
            expected_url=expected_url
        )
