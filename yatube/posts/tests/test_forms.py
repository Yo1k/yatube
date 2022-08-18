from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create_user(username='Author')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description'
        )

        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(user=PostFormTests.author)

    def check_create_post(self, form_data):
        posts_count = Post.objects.count()
        response = PostFormTests.authorized_client_author.post(
            path=reverse('posts:create_post'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': f'{PostFormTests.author.username}'})
        )
        self.assertEqual(
            Post.objects.count(),
            posts_count + 1
        )

        last_added_post = Post.objects.select_related('author', 'group')[0]
        if form_data.get('group'):
            self.assertEqual(last_added_post.group.pk, form_data.get('group'))
        else:
            self.assertEqual(last_added_post.group, None)
        self.assertEqual(last_added_post.text, form_data.get('text'))
        self.assertEqual(last_added_post.author.pk, PostFormTests.author.pk)

    def test_create_post_without_group(self):
        form_data = {
            'text': 'Test post',
        }
        self.check_create_post(form_data)

    def test_create_post_with_group(self):
        form_data = {
            'group': PostFormTests.group.pk,
            'text': 'Test post',
        }
        self.check_create_post(form_data)

    def check_edit_post(self, form_data, post_id):
        posts_count = Post.objects.count()
        response = PostFormTests.authorized_client_author.post(
            path=reverse('posts:post_edit', kwargs={'post_id': post_id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post_id})
        )
        self.assertEqual(
            Post.objects.count(),
            posts_count
        )

        last_added_post = Post.objects.select_related('author', 'group')[0]
        if form_data.get('group'):
            self.assertEqual(last_added_post.group.pk, form_data.get('group'))
        else:
            self.assertEqual(last_added_post.group, None)
        self.assertEqual(last_added_post.text, form_data.get('text'))
        self.assertEqual(last_added_post.author.pk, PostFormTests.author.pk)

    def test_edit_post_without_group_add_group(self):
        post = Post.objects.create(
            text='Test post',
            author=PostFormTests.author,
        )
        form_data = {
            'text': 'Post changes',
            'group': PostFormTests.group.pk
        }
        self.check_edit_post(form_data, post.id)

    def test_edit_post_with_group_remove_group(self):
        post = Post.objects.create(
            text='Test post',
            author=PostFormTests.author,
            group=PostFormTests.group,
        )
        form_data = {
            'text': 'Post changes',
        }
        self.check_edit_post(form_data, post.id)
