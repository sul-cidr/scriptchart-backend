import json

from django import forms
from django.core import validators
from django.db.models import F
from django.utils.translation import gettext as _
from .models import Coordinates, Page, Letter


class PageCoordinatesForm(forms.Form):
    url = forms.CharField(label='Image URL',
                          widget=forms.HiddenInput(),
                          required=True)
    annotations = forms.CharField(label='JSON Annotations',
                                  widget=forms.HiddenInput(),
                                  required=True)

    def __init__(self, *args, **kwargs):
        self.page = kwargs.pop('instance')
        super().__init__(*args, **kwargs)
        self.fields['url'].initial = self.page.url
        annotations = list(self.page
            .coordinates
            .annotate(label=F('letter__letter'))
            .all()
            .values('left', 'top', 'height', 'width', 'label')
        )
        self.fields['annotations'].initial = json.dumps(annotations)

    def clean_url(self):
        url = self.cleaned_data['url']
        if validators.URLValidator()(url):
            raise ValidationError(
                _('Invalid URL: %(url)s'),
                code='invalid',
                params={'url': url},
            )
        return url

    def clean_annotations(self):
        annotations = self.cleaned_data['annotations']
        try:
            annotations = json.loads(annotations)
        except json.decoder.JSONDecodeError:
            raise ValidationError(
                _('Invalid JSON annotations: %(annotations)s'),
                code='invalid',
                params={'annotations': annotations},
            )
        return annotations

    def save(self, *args, **kwargs):
        # Identify which boxes disappeared so we can delete them
        annotations = [
            (annotation['left'], annotation['top'],
             annotation['width'], annotation['height'],
             annotation['label'])
            for annotation in self.cleaned_data['annotations']
        ]
        coordinates = (
            self.page
            .coordinates
            .annotate(label=F('letter__letter'))
            .values_list('id', 'left', 'top', 'width', 'height', 'label')
        )
        coords_to_id = {tuple(coords[1:]): coords[0] for coords in coordinates}
        coords_to_delete = [coords_id
                            for coords, coords_id in coords_to_id.items()
                            if coords not in annotations]
        self.page.coordinates.filter(id__in=coords_to_delete).delete()
        # And create them all over unless they already exist
        for annotation in self.cleaned_data['annotations']:
            Coordinates.objects.get_or_create(
                page=self.page,
                letter=Letter.objects.get(letter=annotation['label']),
                left=annotation['left'],
                top=annotation['top'],
                width=annotation['width'],
                height=annotation['height'],
            )

