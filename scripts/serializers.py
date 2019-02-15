from rest_framework import serializers
from scripts.models import Manuscript
from scripts.models import Letter


class ManuscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manuscript
        fields = ('id', 'shelfmark', 'source', 'page', 'folio', 'scribe', 'date',
                  'resolution', 'notes', 'manifest')


class LetterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Letter
        fields = ('id', 'letter', 'is_script')
