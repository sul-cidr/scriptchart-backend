from rest_framework import serializers
from scripts.models import Manuscript
from scripts.models import Letter
from scripts.models import Page
from scripts.models import Coordinates


class ManuscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manuscript
        fields = ('id', 'shelfmark', 'source', 'page', 'folio', 'scribe', 'date',
                  'resolution', 'notes', 'manifest', 'display')


class LetterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Letter
        fields = ('id', 'letter', 'is_script')


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ('id', 'manuscript', 'url', 'height', 'width')


class CoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinates
        fields = ('id', 'page', 'letter', 'top', 'left', 'width', 'height', 'binary_url')
