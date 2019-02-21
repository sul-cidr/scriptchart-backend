from django.db import models
from .utils import get_sizes


class Manuscript(models.Model):
    shelfmark = models.CharField(unique=True, max_length=250)
    source = models.CharField(blank=True, null=True, max_length=255)
    page = models.CharField(blank=True, null=True, max_length=255)
    folio = models.CharField(blank=True, null=True, max_length=255)
    scribe = models.CharField(blank=True, null=True, max_length=255)
    date = models.CharField(blank=True, null=True, max_length=255)
    catalogue = models.CharField(blank=True, null=True, max_length=255)
    resolution = models.CharField(blank=True, null=True, max_length=255)
    notes = models.CharField(blank=True, null=True, max_length=255)
    manifest = models.URLField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.shelfmark}"


class Page(models.Model):
    manuscript = models.ForeignKey(to='Manuscript', related_name='pages',
                                   on_delete=models.CASCADE)
    number = models.CharField(max_length=255)
    url = models.URLField(blank=False, null=False)
    height = models.IntegerField()
    width = models.IntegerField()
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.manuscript.shelfmark} (p. {self.number})"

    def save(self, *args, **kwargs):
        if self.url and not (self.height and self.width):
            _, (width, height) = get_sizes(self.url)
            self.height |= height
            self.width |= width
        super().save(*args, **kwargs)


class Letter(models.Model):
    letter = models.CharField(max_length=255)
    is_script = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.letter}"


class Coordinates(models.Model):
    page = models.ForeignKey(to='Page', related_name='coordinates',
                             on_delete=models.CASCADE)
    letter = models.ForeignKey(to='Letter', related_name='coordinates',
                               on_delete=models.CASCADE)
    top = models.IntegerField()
    left = models.IntegerField()
    height = models.IntegerField()
    width = models.IntegerField()
    binary_url = models.URLField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Coordinates"

    def __str__(self):
        return (f"{self.page} "
                f"[{self.top}, {self.left}, {self.height}, {self.width}]")
