# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Coordinates(models.Model):
    image_name = models.TextField(db_column='Image_name', blank=True, null=True)
    letter = models.TextField(db_column='Letter', blank=True, null=True)
    x_coordinate = models.IntegerField(db_column='x_Coordinate', blank=True, null=True)
    y_coordinate = models.IntegerField(db_column='y_Coordinate', blank=True, null=True)
    length = models.IntegerField(db_column='Length', blank=True, null=True)
    width = models.IntegerField(db_column='Width', blank=True, null=True)
    binary_url = models.CharField(unique=True, max_length=250, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'coordinatestable'
        verbose_name_plural = "Coordinates"


class Letter(models.Model):
    letter = models.TextField(blank=True, null=True)
    is_script = models.BooleanField(blank=False, null=False, default=True)

    class Meta:
        managed = False
        db_table = 'lettertable'


class Manuscript(models.Model):
    manuscript_no = models.TextField(db_column='Manuscript_no', blank=True, null=True)
    page_no = models.TextField(db_column='Page_no', blank=True, null=True)
    folio_no = models.TextField(db_column='Folio_no', blank=True, null=True)
    catalogue_citation = models.TextField(db_column='Catalogue_citation', blank=True, null=True)
    date = models.TextField(db_column='Date', blank=True, null=True)
    scribe = models.TextField(db_column='Scribe', blank=True, null=True)
    resolution = models.TextField(db_column='Resolution', blank=True, null=True)
    other_information = models.TextField(db_column='Other_Information', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'manuscripttable'


class Page(models.Model):
    image_name = models.CharField(db_column='Image_Name', max_length=255)
    page_no = models.CharField(db_column='Page_No', max_length=255)
    manuscript_no = models.CharField(db_column='Manuscript_No', max_length=255)

    class Meta:
        managed = False
        db_table = 'pagetable'

    def __str__(self):
        return f"{self.manuscript_no} (p. {self.page_no})"

    def get_coordinates(self):
        return (Coordinates.objects
            .filter(image_name=self.image_name)
            .values('x_coordinate', 'y_coordinate', 'length', 'width', 'letter')
            .distinct()
        )
