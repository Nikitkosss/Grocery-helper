# Generated by Django 3.2 on 2023-09-14 10:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_subscriptions_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscriptions',
            options={'ordering': ('-author_id',), 'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ('username',), 'verbose_name': 'Пользователь', 'verbose_name_plural': 'Пользователи'},
        ),
    ]