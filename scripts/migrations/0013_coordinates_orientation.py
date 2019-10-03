# Generated by Django 2.2.4 on 2019-10-01 22:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scripts', '0012_remove_spaces_from_page_numbers'),
    ]

    operations = [
        migrations.AddField(
            model_name='coordinates',
            name='orientation',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Same as Manuscript Page Image (default)'), (2, 'Rotated through 180⁰')], default=1),
        ),
    ]
