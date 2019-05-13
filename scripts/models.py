from django.db import models
from django.template.defaultfilters import slugify

from .priority_field import PriorityField
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
    display = models.BooleanField(default=False)
    slug = models.SlugField(allow_unicode=True, unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.shelfmark)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.shelfmark}'


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
        return f'{self.manuscript.shelfmark} (p. {self.number})'

    def save(self, *args, **kwargs):
        if self.url and not (self.height and self.width):
            _, (width, height) = get_sizes(self.url)
            self.height |= height
            self.width |= width
        # ensure no spaces
        self.number = ''.join(self.number.split())
        super().save(*args, **kwargs)


class Letter(models.Model):
    letter = models.CharField(max_length=255)
    is_script = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.letter}'


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
    manuscript_id = models.PositiveSmallIntegerField(null=False)
    priority = PriorityField(
        collection=('manuscript_id', 'letter'),
        null=True, default=None, blank=True,
        help_text='Examples with the lowest priorities will be selected first '
        'for display in the Script Chart. Examples with no value here will '
        'never be displayed in the Script Chart.<br>This value should only be '
        'set if a binarized image has been uploaded.')

    class Meta:
        verbose_name_plural = 'Coordinates'
        indexes = [
            models.Index(fields=('priority',)),
            models.Index(fields=('letter', 'manuscript_id'))
        ]

    def __str__(self):
        return f'{self.page.manuscript.slug}/{self.letter.letter} ' +\
               f'[{self.priority}], ' +\
               f'{self.height}x{self.width} @{self.top},{self.left}'

    def save(self, *args, **kwargs):
        self.manuscript_id = self.page.manuscript_id

        super().save(*args, **kwargs)
