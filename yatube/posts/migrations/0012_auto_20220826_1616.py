# Generated by Django 2.2.16 on 2022-08-26 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0011_auto_20220823_1150'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='uniq_user_author',
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('author', 'user'), name='uniq_user_author'),
        ),
    ]
