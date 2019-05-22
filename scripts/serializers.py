from rest_framework import serializers
from scripts.models import Manuscript
from scripts.models import Page
from scripts.models import Coordinates


class ManuscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manuscript
        fields = ('id', 'slug', 'shelfmark', 'date', 'manifest')


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ('id', 'manuscript', 'url', 'height', 'width')


class CoordinatesSerializer(serializers.ModelSerializer):
    page = PageSerializer(read_only=True)

    class Meta:
        model = Coordinates
        fields = ('id', 'page', 'letter', 'top', 'left', 'width', 'height',
                  'binary_url', 'page')
