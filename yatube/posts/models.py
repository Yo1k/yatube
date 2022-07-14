from django.db import models
from django.contrib import admin
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    title = models.CharField(unique=True, max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(
            User,
            on_delete=models.CASCADE,
            related_name='posts'
    )
    group = models.ForeignKey(
            Group,
            blank=True,
            null=True,
            on_delete=models.CASCADE,
            related_name='group'
    )


class PostAdmin(admin.ModelAdmin):
    list_display = (
            'pk',
            'text',
            'pub_date',
            'author',
            'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'
