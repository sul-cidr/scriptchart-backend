import json

from django import forms
from django.core import validators
from django.utils.translation import gettext as _
from .models import Page, Coordinates


class PageCoordinatesForm(forms.Form):
    url = forms.CharField(label='Image URL',
                          widget=forms.HiddenInput(),
                          required=True)
    annotations = forms.CharField(label='JSON Annotations',
                                  widget=forms.HiddenInput(),
                                  required=True)

    def __init__(self, *args, **kwargs):
        page = kwargs.pop('instance')
        super().__init__(*args, **kwargs)
        self.page = page
        self.fields['url'].initial = page.image_name
        annotations = json.dumps(list(map(lambda entry: {
            "left": entry["x_coordinate"],
            "top": entry["y_coordinate"],
            "height": entry["length"],
            "width": entry["width"],
            "label": entry["letter"],
        }, page.get_coordinates())))
        self.fields['annotations'].initial = annotations

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
        # If we don't delete first, bbox deletion will not be saved
        Coordinates.objects.filter(
            pk__in=list(self.page.get_coordinates().values_list('id', flat=True))
        ).delete()
        for coordinate in self.cleaned_data['annotations']:
            Coordinates.objects.get_or_create(
                image_name=self.page.image_name,
                letter=coordinate['label'],
                x_coordinate=coordinate['left'],
                y_coordinate=coordinate['top'],
                length=coordinate['height'],
                width=coordinate['width'],
            )

