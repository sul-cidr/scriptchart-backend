# Generated by Django 2.1.7 on 2019-03-06 02:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scripts', '0002_auto_20190117_0007'),
    ]

    operations = [
        migrations.AddField(
            model_name='manuscript',
            name='display',
            field=models.BooleanField(default=False),
        ),
    ]