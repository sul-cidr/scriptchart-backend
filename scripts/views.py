from rest_framework import generics
from scripts.models import Manuscript
from scripts.serializers import ManuscriptSerializer
from scripts.models import Letter
from scripts.serializers import LetterSerializer


class ManuscriptList(generics.ListAPIView):
    queryset = Manuscript.objects.all()
    serializer_class = ManuscriptSerializer


class ManuscriptDetail(generics.RetrieveAPIView):
    queryset = Manuscript.objects.all()
    serializer_class = ManuscriptSerializer


class LetterList(generics.ListAPIView):
    queryset = Letter.objects.all()
    serializer_class = LetterSerializer


class LetterDetail(generics.RetrieveAPIView):
    queryset = Letter.objects.all()
    serializer_class = LetterSerializer
