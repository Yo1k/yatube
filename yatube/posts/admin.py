from django.contrib import admin
from .models import Post, PostAdmin, Group

admin.site.register(Post, PostAdmin)
admin.site.register(Group)
