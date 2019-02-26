from django.db import migrations


def reset(apps, schema_editor):
    SubCategory = apps.get_model('games', 'SubCategory')
    SubCategoryNew = apps.get_model('games', 'SubCategoryNew')
    Quantity = apps.get_model('games', 'Quantity')
    QuantityNew = apps.get_model('games', 'QuantityNew')

    Game1Obj = apps.get_model('games', 'Game_1_obj')

    for sub in SubCategory.objects.all():
        new_sub_category = SubCategoryNew.objects.create(
            description=sub.description.lower(),
            description_eng=sub.description_eng,
            audio=sub.audio,
            audio_eng=sub.audio_eng,
        )
        for game_obj in Game1Obj.objects.filter(sub_category=sub):
            game_obj.sub_category_new = new_sub_category
            game_obj.save()

    for q in Quantity.objects.all():
        new_q = QuantityNew.objects.create(
            description=q.description.lower(),
            description_eng=q.description_eng,
            audio=q.audio,
            audio_eng=q.audio_eng,
        )
        for game_obj in Game1Obj.objects.filter(quantity=q):
            game_obj.quantity_new = new_q
            game_obj.save()


def rollback(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0025_auto_20190226_2108'),
    ]

    operations = [
        migrations.RunPython(reset, rollback)
    ]
