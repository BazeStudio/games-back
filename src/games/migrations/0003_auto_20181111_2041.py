# Generated by Django 2.1.3 on 2018-11-11 20:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0002_auto_20181107_1911'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'Родителя', 'verbose_name_plural': 'Родители'},
        ),
        migrations.AlterField(
            model_name='child',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Родитель'),
        ),
    ]
