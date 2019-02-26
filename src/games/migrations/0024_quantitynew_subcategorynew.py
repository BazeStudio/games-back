# Generated by Django 2.1.5 on 2019-02-26 17:50

from django.db import migrations, models
import games.validators


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0023_small_letter'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuantityNew',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=50, unique=True, verbose_name='Количество')),
                ('description_eng', models.CharField(default='change me', max_length=100, verbose_name='Количество на английском')),
                ('audio', models.FileField(blank=True, help_text='до 5 мб', null=True, upload_to='audios/', validators=[games.validators.validate_file_extension, games.validators.validate_file_size], verbose_name='Аудио')),
                ('audio_eng', models.FileField(blank=True, help_text='до 5 мб', null=True, upload_to='audios/', validators=[games.validators.validate_file_extension, games.validators.validate_file_size], verbose_name='Аудио на английском')),
            ],
            options={
                'verbose_name': 'Количество',
                'verbose_name_plural': 'Показатель количества',
            },
        ),
        migrations.CreateModel(
            name='SubCategoryNew',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=100, unique=True, verbose_name='Подкатегория')),
                ('description_eng', models.CharField(default='change me', max_length=100, verbose_name='Подкатегория на английском')),
                ('audio', models.FileField(blank=True, help_text='до 5 мб', null=True, upload_to='audios/', validators=[games.validators.validate_file_extension, games.validators.validate_file_size], verbose_name='Аудио')),
                ('audio_eng', models.FileField(blank=True, help_text='до 5 мб', null=True, upload_to='audios/', validators=[games.validators.validate_file_extension, games.validators.validate_file_size], verbose_name='Аудио на английском')),
            ],
            options={
                'verbose_name': 'Подкатегории',
                'verbose_name_plural': 'Подкатегория',
            },
        ),
    ]
