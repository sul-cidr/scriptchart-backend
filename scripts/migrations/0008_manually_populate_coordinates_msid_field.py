# Manual data migration created by hand

from django.db import models, migrations, transaction


def populate_new_coordinates_fields(apps, schema_editor):
    # We can't import the models directly as they may be different
    # versions than this migration expects. We use the historical versions.
    Coordinates = apps.get_model('scripts', 'Coordinates')
    Manuscript = apps.get_model('scripts', 'Manuscript')

    ms_ids = Manuscript.objects.values_list('id', flat=True)

    for i, ms_id in enumerate(ms_ids):
        ms_coords = Coordinates.objects.filter(page__manuscript_id=ms_id)
        ms_coords.update(manuscript_id=ms_id)


class Migration(migrations.Migration):

    dependencies = [
        ('scripts', '0007_add_coordinates_msid_field'),
    ]

    operations = [
        migrations.RunPython(populate_new_coordinates_fields),
    ]
