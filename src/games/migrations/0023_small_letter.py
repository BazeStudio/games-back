from django.db import migrations


def set_small_letter(apps, schema_editor):
    SubCategory = apps.get_model('games', 'SubCategory')
    Game1Obj = apps.get_model('games', 'Game_1_obj')

    for sub in SubCategory.objects.all():
        if not sub.description[0].islower():
            new_sub_category = SubCategory.objects.create(
                description=sub.description.lower(),
                description_eng=sub.description_eng,
                audio=sub.audio,
                audio_eng=sub.audio_eng,
            )
            for game_obj in Game1Obj.objects.filter(sub_category=sub):
                game_obj.sub_category = new_sub_category
                game_obj.save()

            sub.delete()


def rollback(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0022_auto_20190222_2007'),
    ]

    operations = [
        migrations.RunPython(set_small_letter, rollback)
    ]
