from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description',
        )
        cls.post = Post.objects.create(
            text='Test post',
            author=cls.user,
        )

    def test_models_have_correct_object_names(self):
        """Checks correctness working method `__str__` on models."""
        post = PostModelTest.post
        self.assertEqual(
            str(post),
            post.text
        )

        group = PostModelTest.group
        self.assertEqual(
            str(group),
            group.title
        )

    def test_verbose_name(self):
        post = PostModelTest.post
        field_verbose = {
            'author': 'Автор',
            'group': 'Группа',
            'pub_date': 'Дата публикации',
            'text': 'Текст поста',
        }
        for field, expected_value in field_verbose.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_help_text(self):
        post = PostModelTest.post
        field_help_text = {
            'group': 'Группа, к которой будет относиться пост',
            'text': 'Текст нового поста',
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text,
                    expected_value
                )
