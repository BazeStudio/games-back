# Generated by Django 2.1.4 on 2019-02-02 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0014_auto_20190131_2245'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='facebook_token',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='vk_token',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
