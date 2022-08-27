import shutil
import tempfile
from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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

        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

    def setUp(self):
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=PostFormTests.small_gif,
            content_type='image/gif'
        )

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        cache.clear()

    def check_create_post(self, form_data):
        posts_count = Post.objects.count()
        response = PostFormTests.authorized_client_author.post(
            path=reverse('posts:post_create'),
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
            self.assertEqual(last_added_post.group.id, form_data.get('group'))
        else:
            self.assertEqual(last_added_post.group, None)

        if not form_data.get('image'):
            self.assertEqual(last_added_post.image.name, '')
        else:
            self.assertEqual(
                form_data.get('image').name,
                Path(last_added_post.image.name).name
            )

        self.assertEqual(last_added_post.text, form_data.get('text'))
        self.assertEqual(last_added_post.author.id, PostFormTests.author.id)

    def test_create_post_with_image(self):
        form_data = {
            'text': 'Test post',
            'image': self.uploaded,
        }
        self.check_create_post(form_data)

    def test_create_post_with_group(self):
        form_data = {
            'group': PostFormTests.group.id,
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
            self.assertEqual(last_added_post.group.id, form_data.get('group'))
        else:
            self.assertEqual(last_added_post.group, None)

        if not form_data.get('image'):
            self.assertEqual(last_added_post.image.name, '')
        else:
            self.assertEqual(
                form_data.get('image').name,
                Path(last_added_post.image.name).name
            )

        self.assertEqual(last_added_post.text, form_data.get('text'))
        self.assertEqual(last_added_post.author.id, PostFormTests.author.id)

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

    def test_edit_post_without_group_add_group(self):
        post = Post.objects.create(
            text='Test post',
            author=PostFormTests.author,
        )
        form_data = {
            'text': 'Post changes',
            'group': PostFormTests.group.id
        }
        self.check_edit_post(form_data, post.id)

    def test_edit_post_without_image_add_image(self):
        post = Post.objects.create(
            text='Test post',
            author=PostFormTests.author,
        )
        form_data = {
            'text': 'Post changes',
            'image': self.uploaded
        }
        self.check_edit_post(form_data, post.id)

    def test_add_comment(self):
        post = Post.objects.create(
            text='Test post',
            author=PostFormTests.author,
        )
        form_data = {
            'text': 'Test comment',
        }
        comments_count = Comment.objects.count()
        response = PostFormTests.authorized_client_author.post(
            path=reverse('posts:add_comment', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post.id})
        )
        self.assertEqual(
            Comment.objects.count(),
            comments_count + 1
        )

        last_added_comment = Comment.objects.select_related('author')[0]
        self.assertEqual(last_added_comment.text, form_data['text'])
        self.assertEqual(last_added_comment.author, PostFormTests.author)
