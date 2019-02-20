from rest_framework import generics
from scripts.models import Manuscript
from scripts.serializers import ManuscriptSerializer
from scripts.models import Letter
from scripts.serializers import LetterSerializer
from scripts.models import Page
from scripts.serializers import PageSerializer
from scripts.models import Coordinates
from scripts.serializers import CoordinatesSerializer


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


class PageList(generics.ListAPIView):
    serializer_class = PageSerializer

    def get_queryset(self):
        queryset = Page.objects.all()
        manuscript_id = self.request.query_params.get('manuscript_id', None)
        if manuscript_id is not None:
            queryset = queryset.filter(manuscript_id=manuscript_id)
        return queryset


class PageDetail(generics.RetrieveAPIView):
    queryset = Page.objects.all()
    serializer_class = PageSerializer


class CoordinatesList(generics.ListAPIView):
    queryset = Coordinates.objects.all()
    serializer_class = CoordinatesSerializer

    def get_queryset(self):
        queryset = Coordinates.objects.all()
        page_id = self.request.query_params.get('page_id', None)
        if page_id is not None:
            queryset = queryset.filter(page_id=page_id)
        return queryset


class CoordinatesDetail(generics.RetrieveAPIView):
    queryset = Coordinates.objects.all()
    serializer_class = CoordinatesSerializer
