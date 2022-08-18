from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


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

    def test_url_exists_at_desired_location_for_guest_client(self):
        url_guest_list = [
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

        for url in url_guest_list:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_does_not_exist_at_desired_location_for_guest_client(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_url_exists_at_desired_location_for_auth_clients(self):
        response = PostURLTests.authorized_client_user.get(
            reverse('posts:create_post')
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

    def test_create_url_redirects_anonymous_on_auth_login(self):
        create_url = reverse('posts:create_post')
        response = self.guest_client.get(create_url)
        expected_url = (
            reverse('users:login')
            + '?next='
            + create_url
        )
        self.assertRedirects(
            response=response,
            expected_url=expected_url
        )

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
