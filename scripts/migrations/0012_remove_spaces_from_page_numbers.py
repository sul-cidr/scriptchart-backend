# Generated by Django 2.2 on 2019-05-13 20:20

from django.db import migrations

from scripts.models import Page


def remove_spaces_from_page_numbers(apps, schema_editor):
    for page in Page.objects.all():
        if ' ' in page.number:
            page.number = ''.join(page.number.split())
            page.save()


class Migration(migrations.Migration):

    dependencies = [
        ('scripts', '0011_manually_populate_coordinates_priority_field'),
    ]

    operations = [
        migrations.RunPython(remove_spaces_from_page_numbers),
    ]