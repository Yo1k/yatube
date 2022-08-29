import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации комментария',
    )
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментарий'
    )
    text = models.TextField(
        help_text='Текст нового комментария',
        verbose_name='Текст комментария',
    )

    class Meta:
        ordering = ['created']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class Group(models.Model):
    description = models.TextField()
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = "Группы"

    def __str__(self):
        return self.title


class Follow(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='uniq_user_author'
            ),
            models.CheckConstraint(
                    check=~models.Q(user=models.F('author')),
                    name='forbid_self_follow'
            )
        ]

    def __str__(self):
        return f'{self.user} follows {self.author}'


class Post(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        help_text='Группа, к которой будет относиться пост',
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
    )
    image = models.ImageField(
        blank=True,
        upload_to=os.path.join('posts', ''),
        verbose_name='Картинка',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )
    text = models.TextField(
        help_text='Текст нового поста',
        verbose_name='Текст поста',
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:settings.LEN_POST_STR]
