# Generated by Django 2.1.5 on 2019-02-26 18:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0028_auto_20190226_2124'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='QuantityNew',
            new_name='Quantity',
        ),
        migrations.RenameModel(
            old_name='SubCategoryNew',
            new_name='SubCategory',
        ),
    ]
