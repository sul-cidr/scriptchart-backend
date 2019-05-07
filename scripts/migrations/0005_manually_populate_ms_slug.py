# Manual data migration created by hand

from django.db import models, migrations
from django.template.defaultfilters import slugify


def create_manuscript_slugs(apps, schema_editor):
    # We can't import the Manuscript model directly as it may be a different
    # version than this migration expects. We use the historical version.
    Manuscript = apps.get_model("scripts", "Manuscript")
    for manuscript in Manuscript.objects.all():
        manuscript.slug = slugify(manuscript.shelfmark)
        manuscript.save()


class Migration(migrations.Migration):

    dependencies = [
        ('scripts', '0004_manuscript_slug'),
    ]

    operations = [
        migrations.RunPython(create_manuscript_slugs),
    ]
