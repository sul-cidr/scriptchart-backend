# Manual data migration created by hand

from django.db import models, migrations, transaction


def populate_new_coordinates_fields(apps, schema_editor):
    # We can't import the models directly as they may be different
    # versions than this migration expects. We use the historical versions.
    Coordinates = apps.get_model('scripts', 'Coordinates')
    Letter = apps.get_model('scripts', 'Letter')
    Manuscript = apps.get_model('scripts', 'Manuscript')

    letter_ids = Letter.objects.values_list('id', flat=True)
    ms_ids = Manuscript.objects.values_list('id', flat=True)

    for ms_id in ms_ids:
        ms_coords = Coordinates.objects.filter(page__manuscript_id=ms_id)

        with transaction.atomic():
            for letter_id in letter_ids:
                comparable = list(ms_coords.filter(
                    letter_id=letter_id, binary_url__isnull=False))
                for index, coordinates in enumerate(comparable):
                    coordinates.priority = index + 1
                    coordinates.save_base(raw=True)


class Migration(migrations.Migration):

    dependencies = [
        ('scripts', '0010_add_coordinates_priority_field'),
    ]

    operations = [
        migrations.RunPython(populate_new_coordinates_fields),
    ]
